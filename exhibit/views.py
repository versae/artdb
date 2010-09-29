# -*-*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponse, render_to_response
from django.template import RequestContext
from django.utils.simplejson import dumps

from django_descriptors.models import Descriptor

from artworks.models import Artwork
from exhibit.utils import clean_years


def artworks_exhibit(request):
    year_range, year_from, year_to = clean_years(request)
    return render_to_response('exhibit.html',
                              {"year_from": year_from,
                               "year_to": year_to,
                               "year_range": year_range},
                              context_instance=RequestContext(request))


def artworks_json(request):
    mimetype = "application/json"
    data = {}
    items = []
    year_range, year_from, year_to = clean_years(request)
    artworks = Artwork.objects.in_range(year_from, year_to)
    for artwork in artworks:
        creators = [creator.get("name")
                    for creator in artwork.creators.all().values("name")]
#        images = [image for image in artwork.images.all()]
        descriptors_objects = Descriptor.objects.get_for_object(artwork)
        descriptors = [descriptor.get("path")
                       for descriptor in descriptors_objects.values("path")]
        artwork_dic = {
            "identifier": artwork.id,
            "type": artwork._meta.object_name,
            "label": artwork.title,
            "serie": artwork.serie and artwork.serie.title,
#            "size": artwork.size,
            "creators": creators,
            "creation_year_start": artwork.creation_year_start,
            "creation_year_end": artwork.creation_year_end,
#            "inscription": artwork.inscription,
#            "notes": artwork.notes,
#            "image": images,
            "URI": artwork.get_absolute_url(),
            "original_place": (artwork.original_place
                               and artwork.original_place.title),
            "current_place": (artwork.current_place
                              and artwork.current_place.title),
            "descriptors": descriptors,
        }
        if (request.user and request.user.is_authenticated()
            and (request.user.is_staff or request.user.is_superuser)):
            artwork_dic.update({
                "admin": reverse("admin:artworks_artwork_change",
                                 args=[artwork.id]),
            })
        items.append(artwork_dic)
    data.update({
        "properties": {
            "creation_year_start": {
                "valueType": "number",
            },
            "creation_year_end": {
                "valueType": "number",
            },
            "URI": {
                "valueType": "url",
            },
            "admin": {
                "valueType": "url",
            },
        },
        "types": {
            Artwork._meta.verbose_name.capitalize(): {
                "pluralLabel": Artwork._meta.verbose_name_plural.capitalize(),
            }
        },
        "items": items
    })
    return HttpResponse(dumps(data), mimetype=mimetype)


def artworks_history(request):  
    """Used for Exhibit to safe a navigation history."""
    return HttpResponse(u"")
