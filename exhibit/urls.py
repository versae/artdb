from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('exhibit.views',

    # exhibit
    url(r'^artworks/$', "artworks_view", name="exhibit_artworks"),
    url(r'^artworks/json/$', "json_artworks", name="json_artworks"),

)
