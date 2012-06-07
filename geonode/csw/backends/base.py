"""Base CSW backend class."""

class BaseCSWBackend(object):
    """
    Base class for CSW backend implementations.

    Subclasses must at least overwrite send_messages().
    """
    def __init__(self, **kwargs):
        pass

    def open(self):
        """Open a network connection.

        This method can be overwritten by backend implementations to
        open a network connection.

        It's up to the backend implementation to track the status of
        a network connection if it's needed by the backend.

        This method can be called by applications to force a single
        network connection to be used when sending mails.

        The default implementation does nothing.
        """
        pass

    def close(self):
        """Close a network connection."""
        pass

    def get_by_uuid(self, uuid):
        raise NotImplementedError

    def url_for_uuid(self):
        raise NotImplementedError

    def url_for_uuid(self, uuid, outputschema):
        """Returns list of valid GetRecordById URLs for a given record"""
        raise NotImplementedError

    def csw_request(self, layer, template):
        raise NotImplementedError

    def create_from_layer(self, layer):
        raise NotImplementedError

    def delete_layer(self, layer):
        raise NotImplementedError

    def update_layer(self, layer):
        raise NotImplementedError

    def set_metadata_privs(self, uuid, privileges):
        """
        set the full set of privileges on the item with the 
        specified uuid based on the dictionary given of the form: 
        {
          'group_name1': {'operation1': True, 'operation2': True, ...},
          'group_name2': ...
        }

        all unspecified operations and operations for unspecified groups 
        are set to False.
        """
        pass

    def search(self, keywords, startposition, maxrecords, bbox):
        """CSW search wrapper"""
        raise NotImplementedError


def metadatarecord2dict(rec, catalogue):
    """
    accepts a node representing a catalogue result 
    record and builds a POD structure representing 
    the search result.
    """

    if rec is None:
        return None
    # Let owslib do some parsing for us...
    result = {}
    result['uuid'] = rec.identifier
    result['title'] = rec.identification.title
    result['abstract'] = rec.identification.abstract

    keywords = []
    for kw in rec.identification.keywords:
        keywords.extend(kw['keywords'])

    result['keywords'] = keywords

    # XXX needs indexing ? how
    result['attribution'] = {'title': '', 'href': ''}

    result['name'] = result['uuid']

    result['bbox'] = {
        'minx': rec.identification.bbox.minx,
        'maxx': rec.identification.bbox.maxx,
        'miny': rec.identification.bbox.miny,
        'maxy': rec.identification.bbox.maxy
        }

    # locate all distribution links
    result['download_links'] = _extract_links(rec)

    # construct the link to the Catalogue metadata record (not self-indexed)
    result['metadata_links'] = [("text/xml", "TC211", catalogue.url_for_uuid(rec.identifier, 'http://www.isotc211.org/2005/gmd'))]

    return result


def normalize_bbox(bbox):
    """
    fix bbox axis order
    GeoNetwork accepts x/y
    pycsw accepts y/x
    """

    if connection['type'] == 'geonetwork':
        return bbox
    else:  # swap coords per standard
        return [bbox[1], bbox[0], bbox[3], bbox[2]]


def _extract_links(rec):
    # fetch all distribution links

    links = []
    # extract subset of description value for user-friendly display
    format_re = re.compile(".*\((.*)(\s*Format*\s*)\).*?")

    if not hasattr(rec, 'distribution'):
        return None
    if not hasattr(rec.distribution, 'online'):
        return None

    for link_el in rec.distribution.online:
        if link_el.protocol == 'WWW:DOWNLOAD-1.0-http--download':
            try:
                extension = link_el.name.split('.')[-1]
                format = format_re.match(link_el.description).groups()[0]
                href = link_el.url
                links.append((extension, format, href))
            except:
                pass
    return links
