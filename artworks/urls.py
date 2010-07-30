# -*-*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('artworks.views',
    (r'range/(?P<year_from>\d+)/to/(?P<year_to>\d+)/$', 'in_range'),
    (r'(?P<artwork_id>\d+)/$', 'properties'),
    (r'^records/', 'artworks_record'),
)
