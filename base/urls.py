from django.conf.urls.defaults import *

urlpatterns = patterns('base.views',
    url(r'search_view/$', 'search', name="search_view"),                       
    url(r'^$', 'public_view', name="public_view"),
)