from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('exhibit.views',

    # exhibit
    url(r'^artworks/json/', "artworks_json", name="artworks_json"),
    url(r'^artworks/__history__.html', "artworks_history",
        name="artworks_history"),
    url(r'^artworks/', "artworks_exhibit", name="artworks_exhibit"),

)
