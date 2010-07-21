from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('geonode.maps.views',
    (r'^$', 'maps'),
    url(r'^new$', 'newmap', name="map_new"),
    (r'^(?P<mapid>\d+)$', 'map_controller'),
    (r'^(?P<mapid>\d+)/view$', 'view'),
    (r'^(?P<mapid>\d+)/download/$', 'map_download'),
    (r'^check/$', 'check_download'),
    (r'^embed/$', 'embed'),
    (r'^(?P<mapid>\d+)/embed$', 'embed'),
    (r'^(?P<mapid>\d+)/data$', 'mapJSON'),
    url(r'^change-poc/(?P<ids>\w+)$', 'change_poc', name="change_poc"),
)
