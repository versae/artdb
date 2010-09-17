from django.conf.urls.defaults import *

urlpatterns = patterns('creators.views',
    url(r'(?P<creator_id>\d+)/$', 'creator_record', name="creator_record"),
    url(r'^$', 'creators_list', name="creators_list"),
)