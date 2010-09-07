from django.conf.urls.defaults import *

urlpatterns = patterns('base.views',
    url(r'^$', 'public_view', name="public_view"),
)