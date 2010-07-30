from django.conf.urls.defaults import *

urlpatterns = patterns('creators.views',
    url(r'^records/', 'creator_record', name="creator_record"),
)