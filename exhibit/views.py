# -*-*- coding: utf-8 -*-
from django.shortcuts import HttpResponse, render_to_response
from django.template import RequestContext
from django.utils.simplejson import dumps

from artworks.models import Artwork


def artworks_view(request):
    return render_to_response('exhibit.html',
                              {},
                              context_instance=RequestContext(request))

def json_artworks(request):
    mimetype = "application/json"
    data = {}
    items = []
    artworks = Artwork.objects.all()
    for artwork in artworks[:100]:
        creators = [creator.creator.name
                    for creator in artwork.artworkcreator_set.all()]
        images = [image for image in artwork.images.all()]
        artwork_dic = {
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
        }
        items.append(artwork_dic)
    data.update({
        "properties": {
            "label": {
                "valueType": "item",
            },
            "creators": {
                "valueType": "item",
            },
            "serie": {
                "valueType": "item",
            },
            "creation_year_start": {
                "valueType": "number",
            },
            "creation_year_end": {
                "valueType": "number",
            },
        },
        "items": items
    })
    return HttpResponse(dumps(data), mimetype=mimetype)
