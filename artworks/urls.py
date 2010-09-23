# -*-*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('artworks.views',
    url(r'^$', 'artworks_list', name="artworks_list"),
    url(r'locations/(?P<year_from>\d+)/to/(?P<year_to>\d+)/$',
        'artworks_locations', name="artworks_locations"),
    url(r'(?P<artwork_id>\d+)/properties/$', 'artworks_properties',
        name="artworks_properties"),
    url(r'(?P<artwork_id>\d+)/$', 'artworks_record', name="artworks_record"),
)
