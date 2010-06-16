# -*-*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponse, render_to_response
from django.template import RequestContext
from django.utils.simplejson import dumps

from artworks.models import Artwork


def artworks_exhibit(request):
    year_from = None
    year_to = None
    if request.GET and "from" in request.GET and "to" in request.GET:
        year_from = int(request.GET.get("from", 0))
        year_to = int(request.GET.get("to", 0))
    return render_to_response('exhibit.html',
                              {"year_from": year_from,
                               "year_to": year_to},
                              context_instance=RequestContext(request))


def artworks_json(request):
    mimetype = "application/json"
    data = {}
    items = []
    if request.GET and "from" in request.GET and "to" in request.GET:
        year_from = int(request.GET.get("from", 0))
        year_to = int(request.GET.get("to", 0))
        artworks = Artwork.objects.in_range(year_from, year_to)
    else:
        artworks = Artwork.objects.all()
    for artwork in artworks:
        creators = [creator.name
                    for creator in artwork.creators.all()]
        images = [image for image in artwork.images.all()]
        artwork_dic = {
            "identifier": artwork.id,
            "admin": reverse("admin:artworks_artwork_change",
                             args=[artwork.id]),
            "type": artwork._meta.object_name,
            "label": artwork.title,
            "serie": artwork.serie and artwork.serie.title,
            "size": artwork.size,
            "creators": creators,
            "creation_year_start": artwork.creation_year_start,
            "creation_year_end": artwork.creation_year_end,
            "inscription": artwork.inscription,
            "notes": artwork.notes,
            "image": images,
            "current_place": (artwork.current_place
                              and artwork.current_place.title),
        }
        items.append(artwork_dic)
    data.update({
        "properties": {
            "id": {
                "valueType": "number",
            },
            "label": {
                "valueType": "item",
            },
            "creators": {
                "valueType": "item",
            },
            "serie": {
                "valueType": "item",
            },
            "current_place": {
                "valueType": "item",
            },
            "creation_year_start": {
                "valueType": "number",
            },
            "creation_year_end": {
                "valueType": "number",
            },
            "admin": {
                "valueType": "url",
            },
        },
        "types": {
            "Artwork": {
                "pluralLabel": "Artworks",
            }
        },
        "items": items
    })
    return HttpResponse(dumps(data), mimetype=mimetype)


def artworks_history(request):  
    """Used for Exhibit to safe a navigation history."""
    return HttpResponse(u"")
