#########################################################################
#
# Copyright (C) 2012 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.models import User
from django.core.cache import cache

from geonode.maps.views import default_map_config
from geonode.maps.models import Layer
from geonode.maps.models import Map
from geonode.people.models import Contact
from geonode.search.search import combined_search_results
from geonode.search.util import resolve_extension
from geonode.search.normalizers import apply_normalizers
from geonode.search.query import query_from_request
from geonode.search.query import BadQuery

from datetime import datetime
from time import time
import json
import cPickle as pickle
import operator
import logging
import zlib

logger = logging.getLogger(__name__)

_extra_context = resolve_extension('extra_context')

DEFAULT_MAPS_SEARCH_BATCH_SIZE = 10


def _create_viewer_config():
    DEFAULT_MAP_CONFIG, DEFAULT_BASE_LAYERS = default_map_config()
    _map = Map(projection="EPSG:900913", zoom = 1, center_x = 0, center_y = 0)
    return json.dumps(_map.viewer_json(*DEFAULT_BASE_LAYERS))
_viewer_config = _create_viewer_config()


def search_page(request, **kw):
    params = {}
    if kw:
        params.update(kw)

    context = _get_search_context()
    context['init_search'] = json.dumps(params)

    return render_to_response('search/search.html', RequestContext(request, context))

def advanced_search(request, **kw):
    params = {}
    if kw:
        params.update(kw)

    context = _get_search_context()
    context['init_search'] = json.dumps(params)
    return render_to_response('search/advanced_search.html', RequestContext(request, context))

def _get_search_context():
    cache_key = 'simple_search_context'
    context = cache.get(cache_key)
    if context: return context

    counts = {
        'maps' : Map.objects.count(),
        'layers' : Layer.objects.count(),
        'vector' : Layer.objects.filter(storeType='dataStore').count(),
        'raster' : Layer.objects.filter(storeType='coverageStore').count(),
        'users' : Contact.objects.count()
    }
    topics = Layer.objects.all().values_list('topic_category',flat=True)
    topic_cnts = {}
    for t in topics: topic_cnts[t] = topic_cnts.get(t,0) + 1
    context = {
        'viewer_config': _viewer_config,
        'GOOGLE_API_KEY' : settings.GOOGLE_API_KEY,
        "site" : settings.SITEURL,
        'counts' : counts,
        'users' : User.objects.all(),
        'topics' : topic_cnts,
        'keywords' : _get_all_keywords()
    }
    if _extra_context:
        _extra_context(context)
    cache.set(cache_key, context, 60)

    return context


def _get_all_keywords():
    allkw = {}
    # @todo tagging added to maps and contacts, depending upon search type,
    # need to get these... for now it doesn't matter (in mapstory) as
    # only layers support keywords ATM.
    for l in Layer.objects.all().select_related().only('keywords'):
        kw = [ k.name for k in l.keywords.all() ]
        for k in kw:
            allkw[k] = allkw.get(k,0) + 1

    return allkw


def search_api(request, **kwargs):
    if request.method not in ('GET','POST'):
        return HttpResponse(status=405)
    debug = logger.isEnabledFor(logging.DEBUG)
    if debug:
        connection.queries = []
    ts = time()
    try:
        query = query_from_request(request, kwargs)
        items, facets = _search(query)
        ts1 = time() - ts
        if debug:
            ts = time()
        results = _search_json(query, items, facets, ts1)
        if debug:
            ts2 = time() - ts
            logger.debug('generated combined search results in %s, %s',ts1,ts2)
            logger.debug('with %s db queries',len(connection.queries))
        return results
    except Exception, ex:
        if not isinstance(ex, BadQuery):
            logger.exception("error during search")
        return HttpResponse(json.dumps({
            'success' : False,
            'errors' : [str(ex)]
        }), status=400)


def _search_json(query, items, facets, time):
    total = len(items)

    if query.limit > 0:
        items = items[query.start:query.start + query.limit]

    # unique item id for ext store (this could be done client side)
    iid = query.start
    for r in items:
        r.iid = iid
        iid += 1

    exclude = query.params.get('exclude')
    exclude = set(exclude.split(',')) if exclude else ()
    items = map(lambda r: r.as_dict(exclude), items)

    results = {
        '_time' : time,
        'results' : items,
        'total' :  total,
        'success' : True,
        'query' : query.get_query_response(),
        'facets' : facets
    }
    return HttpResponse(json.dumps(results), mimetype="application/json")


def cache_key(query,filters):
    return str(reduce(operator.xor,map(hash,filters.items())) ^ hash(query))


def _search(query):
    # to support super fast paging results, cache the intermediates
    results = None
    cache_time = 60
    if query.cache:
        key = query.cache_key()
        results = cache.get(key)
        if results:
            # put it back again - this basically extends the lease
            cache.add(key, results, cache_time)

    if not results:
        results = combined_search_results(query)
        facets = results['facets']
        results = apply_normalizers(results)
        if query.cache:
            dumped = zlib.compress(pickle.dumps((results, facets)))
            logger.debug("cached search results %s", len(dumped))
            cache.set(key, dumped, cache_time)

    else:
        results, facets = pickle.loads(zlib.decompress(results))

    # @todo - sorting should be done in the backend as it can optimize if
    # the query is restricted to one model. has implications for caching...
    if query.sort == 'title':
        keyfunc = lambda r: r.title().lower()
    elif query.sort == 'last_modified':
        old = datetime(1,1,1)
        keyfunc = lambda r: r.last_modified() or old
    else:
        keyfunc = lambda r: getattr(r, query.sort)()
    results.sort(key=keyfunc, reverse=not query.order)

    return results, facets


def author_list(req):
    q = User.objects.all()

    query = req.REQUEST.get('query',None)
    start = int(req.REQUEST.get('start',0))
    limit = int(req.REQUEST.get('limit',20))

    if query:
        q = q.filter(username__icontains=query)

    vals = q.values_list('username',flat=True)[start:start+limit]
    results = {
        'total' : q.count(),
        'names' : [ dict(name=v) for v in vals ]
    }
    return HttpResponse(json.dumps(results), mimetype="application/json")

# Haystack Implementation
'''
import json
import xmlrpclib

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core import serializers

from haystack.inputs import AutoQuery, Raw 
from haystack.query import SearchQuerySet, SQ
from django.db.models import Sum
from django.contrib.gis.geos import GEOSGeometry

from geonode.maps.views import default_map_config, Map, Layer

default_facets = ["map", "layer", "vector", "raster", "contact"]
fieldsets = {
    "brief": ["name", "type", "description"],
    "summary": ["name", "type", "description", "owner"],
    "full": ["name", "type", "description", "owner", "language"],
}


def search(request):
    """
    View that drives the search page
    """

    DEFAULT_MAP_CONFIG, DEFAULT_BASE_LAYERS = default_map_config()
    #DEFAULT_MAP_CONFIG, DEFAULT_BASE_LAYERS = default_map_config(request)
    # for non-ajax requests, render a generic search page

    params = dict(request.REQUEST)

    map = Map(projection="EPSG:900913", zoom=1, center_x=0, center_y=0)

    # Default Counts to 0, JS will Load the Correct Counts
    facets = {}
    for facet in default_facets:
        facets[facet] = 0

    return render_to_response("search/search.html", RequestContext(request, {
        "init_search": json.dumps(params),
        #'viewer_config': json.dumps(map.viewer_json(added_layers=DEFAULT_BASE_LAYERS, authenticated=request.user.is_authenticated())),
        "viewer_config": json.dumps(map.viewer_json(*DEFAULT_BASE_LAYERS)),
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY,
        "site": settings.SITEURL,
        "facets": facets,
        "keywords": Layer.objects.gn_catalog.get_all_keywords()
    }))


def search_api(request):
    """
    View that drives the search api
    """

    # Retrieve Query Params
    id = request.REQUEST.get("id", None)
    query = request.REQUEST.get('q',None)
    name = request.REQUEST.get("name", None)
    category = request.REQUEST.get("cat", None)
    limit = int(request.REQUEST.get("limit", getattr(settings, "HAYSTACK_SEARCH_RESULTS_PER_PAGE", 20)))
    startIndex = int(request.REQUEST.get("startIndex", 0))
    startPage = int(request.REQUEST.get("startPage", 0))
    sort = request.REQUEST.get("sort", "relevance")
    order = request.REQUEST.get("order", "asc")
    type = request.REQUEST.get("type", None)
    fields = request.REQUEST.get("fields", None)
    fieldset = request.REQUEST.get("fieldset", None)
    format = request.REQUEST.get("format", "json")
    # Geospatial Elements
    bbox = request.REQUEST.get("bbox", None)

    sqs = SearchQuerySet()

    # Filter by ID
    if id:
        sqs = sqs.narrow("django_id:%s" % id)

    # Filter by Type
    if type is not None:
        if type in ["map", "layer", "contact"]:
            # Type is one of our Major Types (not a sub type)
            sqs = sqs.narrow("type:%s" % type)
        elif type in ["vector", "raster"]:
            # Type is one of our sub types
            sqs = sqs.narrow("subtype:%s" % type)

    # Filter by Query Params
    if query:
        sqs = sqs.filter(content=Raw(query))
        
    # filter by cateory
    
    if category is not None:
        sqs = sqs.narrow('category:%s' % category)

    # Apply Sort
    # TODO: Handle for Revised sort types
    # [relevance, alphabetically, rating, created, updated, popularity]
    if sort.lower() == "newest":
        sqs = sqs.order_by("-date")
    elif sort.lower() == "oldest":
        sqs = sqs.order_by("date")
    elif sort.lower() == "alphaaz":
        sqs = sqs.order_by("title")
    elif sort.lower() == "alphaza":
        sqs = sqs.order_by("-title")
        
    # Setup Search Results
    results = []
    
    """
    if bbox is not None:
        left,bottom,right,top = bbox.split(',')
        sqs = sqs.filter(
            # first check if the bbox has at least one point inside the window
            SQ(bbox_left__gte=left) & SQ(bbox_left__lte=right) & SQ(bbox_top__gte=bottom) & SQ(bbox_top__lte=top) | #check top_left is inside the window
            SQ(bbox_right__lte=right) &  SQ(bbox_right__gte=left) & SQ(bbox_top__lte=top) &  SQ(bbox_top__gte=bottom) | #check top_right is inside the window
            SQ(bbox_bottom__gte=bottom) & SQ(bbox_bottom__lte=top) & SQ(bbox_right__lte=right) &  SQ(bbox_right__gte=left) | #check bottom_right is inside the window
            SQ(bbox_top__lte=top) & SQ(bbox_top__gte=bottom) & SQ(bbox_left__gte=left) & SQ(bbox_left__lte=right) | #check bottom_left is inside the window
            # then check if the bbox is including the window
            SQ(bbox_left__lte=left) & SQ(bbox_right__gte=right) & SQ(bbox_bottom__lte=bottom) & SQ(bbox_top__gte=top)
        )
    """

    # Filter by permissions
    """
    for i, result in enumerate(sqs):
        if result.type == 'layer':
            if not request.user.has_perm('maps.view_layer',obj = result.object):
                sqs = sqs.exclude(id = result.id)
        if result.type == 'map':
            if not request.user.has_perm('maps.view_map',obj = result.object):
                sqs = sqs.exclude(id = result.id)
    """

    # Build the result based on the limit
    for i, result in enumerate(sqs[startIndex:startIndex + limit]):
        data = json.loads(result.json)
        data.update({"iid": i + startIndex})
        results.append(data)
    
    # Filter Fields/Fieldsets
    if fieldset:
        if fieldset in fieldsets.keys():
            for result in results:
                for key in result.keys():
                    if key not in fieldsets[fieldset]:
                        del result[key]
    elif fields:
        fields = fields.split(',')
        for result in results:
            for key in result.keys():
                if key not in fields:
                    del result[key]        

    # Setup Facet Counts
    sqs = sqs.facet("type").facet("subtype")
    
    sqs = sqs.facet('category')

    facets = sqs.facet_counts()

    # Prepare Search Results
    data = {
        "success": True,
        "total": sqs.count(),
        "query_info": {
            "q": query,
            "startIndex": startIndex,
            "limit": limit,
            "sort": sort,
            "type": type,
        },
        "facets": facets,
        "results": results,
        "counts": dict(facets.get("fields")['type']+facets.get('fields')['subtype']),
        "categories": [facet[0] for facet in facets.get('fields')['category']]
    }

    # Return Results
    if format:
        if format == "xml":
            return HttpResponse(xmlrpclib.dumps((data,), allow_none=True), mimetype="text/xml")
        elif format == "json":
            return HttpResponse(json.dumps(data), mimetype="application/json")
    else:
        return HttpResponse(json.dumps(data), mimetype="application/json")
'''
