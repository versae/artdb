# -*-*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('artworks.views',

    # Index
    url(r'^$', 'artworks_list', name="artworks_list"),

    # Serie
    url(r'^serie/(?P<serie_id>\d+)/$', 'series_record', name="series_record"),
    url(r'^serie/$', 'series_list', name="series_list"),

    # Locations
    url(r'^locations/(?P<geospatialreference_id>\d+)/list/$',
        'artworks_by_locations', name="artworks_by_locations"),
    url(r'^locations/(?P<year_from>\d+)/to/(?P<year_to>\d+)/$',
        'artworks_locations', name="artworks_locations"),

    # Artwork
    url(r'^(?P<artwork_id>\d+)/$', 'artworks_record', name="artworks_record"),

)
