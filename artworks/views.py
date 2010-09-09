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
    artworks_by = request.GET.get("filter", "artwork_current_place")
    dics = []
    if artworks_by == "artwork_original_place":
        place_field_name = "original_place"
    else:
        place_field_name = "current_place"
    artworks = Artwork.objects.in_range(year_from, year_to)
    points = set()
    for artwork in artworks:
        dic = {
            'identifier': artwork.id,
            'title': artwork.title,
        }
        place = None
        place_field = getattr(artwork, place_field_name)
        if (place_field and place_field.point
            and place_field.point.wkt not in points):
            points.add(place_field.point.wkt)
            dic.update({
                'place': place_field.title,
                'coordinates': place_field.point.wkt,
            })
        dics.append(dic)
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
