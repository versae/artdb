# -*-*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('artworks.views',
    url(r'serie/(?P<serie_id>\d+)/$', 'series_record', name="series_record"),
    url(r'serie/$', 'series_list', name="series_list"),
    (r'range/(?P<year_from>\d+)/to/(?P<year_to>\d+)/$', 'in_range'),
    url(r'(?P<artwork_id>\d+)/$', 'artworks_record', name="artworks_record"),
    (r'(?P<artwork_id>\d+)/$', 'properties'),
    url(r'^$', 'artworks_list', name="artworks_list"),
    url(r'locations/(?P<year_from>\d+)/to/(?P<year_to>\d+)/$',
        'artworks_locations', name="artworks_locations"),
    url(r'locations/(?P<geospatialreference_id>\d+)/list/$',
        'artworks_by_locations', name="artworks_by_locations"),
    url(r'(?P<artwork_id>\d+)/$', 'artworks_record', name="artworks_record"),
)
