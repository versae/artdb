from django.conf.urls.defaults import *

urlpatterns = patterns('creators.views',
    url(r'records/(?P<creator_id>\d+)/$', 'creator_record', name="creator_record"),
    url(r'records/list/', 'creators_list', name="creators_list"),
)