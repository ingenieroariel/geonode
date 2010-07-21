from django.conf.urls.defaults import *
from django.conf import settings
from utils import path_extrapolate

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

js_info_dict = {
    'packages': ('geonode.maps',),
}

urlpatterns = patterns('',
    # Geonode specific urls
    (r'^(?:index/?)?$', 'geonode.views.index'),
    (r'^(?P<page>developer|help)/?$', 'geonode.views.static'),
    (r'^maps/', include('geonode.maps.urls')),
    (r'^data/', include('geonode.maps.data_urls')),
    (r'^community/$', 'geonode.views.community'),
    (r'^proxy/', 'geonode.proxy.views.proxy'),
    (r'^geoserver/','geonode.proxy.views.geoserver'),
       
    # Support urls
    (r'^lang\.js$', 'geonode.views.lang'),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    (r'^accounts/login', 'django.contrib.auth.views.login'),
    (r'^accounts/logout', 'django.contrib.auth.views.logout'),
    
    # External apps
    (r'^avatar/', include('avatar.urls')),
    (r'^accounts/', include('registration.urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^admin/', include(admin.site.urls)),

)

#
# Extra static file endpoint for development use
if settings.DEBUG:
    import os
    def here(*x): 
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

    root = here("..", "..", "geonode-client", "build", "geonode-client") if settings.MINIFIED_RESOURCES else here("..", "..", "geonode-client", "")
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': root}),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': path_extrapolate('django/contrib/admin/media', 'django')})
    )


