# -*- coding: utf-8 -*-
from django.template import Library

from base.utils import url_map_points

register = Library()


@register.inclusion_tag('templatetags/place_map.html', takes_context=True)
def place_map(context, geometry, point):
    points = [point]
    img_src = url_map_points(points, width=250, height=200, create_path=True,
                             marker_size='small')
    return {
        'img_src': img_src,
    }
