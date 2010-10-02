# -*- coding: utf-8 -*-
from django.conf import settings


def url_map(lat, lon, width=300, height=300, marker_size='tiny', map_type="roadmap"):
    return u"http://maps.google.com/staticmap?center=%s,%s&zoom=15&size=%sx%s&maptype=%s&key=%s&markers=%s,%s,%sblue" % (str(lat), str(lon), str(width), str(height), map_type, settings.GOOGLE_API_KEY, str(lat), str(lon), marker_size)


def url_map_points(points, width=300, height=300, create_path=True, marker_size='tiny', map_type="roadmap"):
    if len(points) == 1:
        lat = points[0][1]
        lon = points[0][0]
        return u"http://maps.google.com/staticmap?center=%s,%s&zoom=5&size=%sx%s&maptype=%s&key=%s&markers=%s,%s,%sblue" % (str(lat), str(lon), str(width), str(height), map_type, settings.GOOGLE_API_KEY, str(lat), str(lon), marker_size)
    else:
        if create_path:
            path = "|".join(["%s,%s" % (lat, lon) for lat, lon in points])
            show = "path=%s" % path
        else:
            markers = "|".join(["%s,%s,%sblue" % (lat, lon, marker_size) for lat, lon in points])
            show = "markers=%s" % markers
        return u"http://maps.google.com/staticmap?size=%sx%s&maptype=%s&key=%s&%s" % (str(width), str(height), map_type, settings.GOOGLE_API_KEY, show)
