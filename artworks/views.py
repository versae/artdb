# -*-*- coding: utf-8 -*-
from django.shortcuts import HttpResponse, render_to_response
from django.template import RequestContext
from django.utils.simplejson import dumps

from artworks.models import Artwork


def artworks_record(request):
    artwork_id = None
    artwork = None
    if request.GET and "id" in request.GET:
        artwork_id = int(request.GET.get("id", 0))
    artwork = Artwork.objects.get(id=artwork_id)
    artwork.fm_descriptors = artwork.fm_descriptors.split(';')
    return render_to_response('artworks.html',
                              {"artwork": artwork}, context_instance=RequestContext(request))
    

def in_range(request, year_from, year_to):
    year_from = int(year_from)
    year_to = int(year_to)
    dics = []
#    artworks = Artwork.objects.in_range(year_from, year_to)
#    for artwork in artworks:
#        dic = {
#            'identifier': artwork.id,
#            'title': artwork.title,
#        }
#        place = None
#        try:
#            place_history = artwork.placeshistory_set.get(artwork=artwork,
#                                                          place_type='L')
#            place = place_history.place
#            if hasattr(place.geometry, 'wkt'):
#                dic.update({
#                    'place': place.name,
#                    'coordinates': place.geometry.wkt,
#                })
#                dics.append(dic)
#        except PlacesHistory.DoesNotExist:
#            pass
    print len(dics)
    return HttpResponse(dumps(dics), mimetype="application/json")


def properties(request, artwork_id):
    artworks = Artwork.objects.in_bulk([int(artwork_id)])
    dic = {}
#    if artworks:
#        artwork = artworks[int(artwork_id)]
#        dic = {
#            'identifier': artwork.id,
#            'title': artwork.title,
#            'size': artwork.size,
#            'notes': artwork.notes,
#            'inscription': artwork.inscription,
#        }
#    try:
#        place_history = artwork.placeshistory_set.get(artwork=artwork,
#                                                      place_type='L')
#        place = place_history.place
#        if hasattr(place.geometry, 'wkt'):
#            dic.update({
#                'place': place.name,
#                'coordinates': place.geometry.wkt,
#            })
#            print dic
#    except PlacesHistory.DoesNotExist:
#        pass
    return HttpResponse(dumps(dic), mimetype="application/json")
