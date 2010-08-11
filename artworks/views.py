# -*-*- coding: utf-8 -*-
from django.shortcuts import HttpResponse, render_to_response
from django.template import RequestContext
from django.utils.simplejson import dumps
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from artworks.models import Artwork
from django.core.urlresolvers import reverse

def artworks_list(request):
    orderby = None
    artwork_list = None       
    orderby = request.GET.get('orderby', None)
    if orderby is None:
            orderby = 'title'            
    artwork_list = Artwork.objects.order_by(orderby)
    paginator = Paginator(artwork_list, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    artworks = paginator.page(page)
    return render_to_response('artworks_list.html',
                              {"artworks": artworks, "order": orderby}, context_instance=RequestContext(request))


def artworks_record(request, artwork_id):
    request.breadcrumbs('Artworks', reverse('artworks_list'))
    artwork_id = int(artwork_id)
    artwork = None
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
