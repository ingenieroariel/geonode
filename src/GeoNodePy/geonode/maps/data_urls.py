from django.conf.urls.defaults import patterns, url

js_info_dict = {
    'packages': ('geonode.maps',),
}

urlpatterns = patterns('geonode.maps.views',
    url(r'^$', 'browse_data', name='data'),
    url(r'^search/?$', 'search_page', name='search'),
    url(r'^search/api/?$', 'metadata_search', name='search_api'),
    url(r'^search/detail/?$', 'search_result_detail', name='search_result_detail'),
    url(r'^upload$', 'upload_layer', name='data_upload'),
    (r'^download$', 'batch_layer_download'),
    (r'^(?P<layername>[^/]*)$', 'layerController'),
)
