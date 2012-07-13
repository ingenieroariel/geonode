from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns(
    '',

    url(r'.*','geonode.catalogue.views.global_dispatch'),
)
