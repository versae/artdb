from django.conf.urls.defaults import *

urlpatterns = patterns('graphs.views',
    url(r'^force/$', 'force_graph', name="force_graph"),
)
