from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from admin import admin_site


urlpatterns = patterns('',
    # static server
    url(r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    # artwork
    url(r'^artworks/', include('artworks.urls')),
    
    # creator
    url(r'^creators/', include('creators.urls')),

    # map
    url(r'^map/$', direct_to_template, {'template': 'map.html'}, name="map"),

    # exhibit
    url(r'^exhibit/', include('exhibit.urls')),

    # base
    url(r'^$', direct_to_template, {'template': 'map.html'}),

    # admin
    url(r'^admin/', include(admin_site.urls)),
)
