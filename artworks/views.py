# -*-*- coding: utf-8 -*-
from django.shortcuts import HttpResponse, render_to_response
from django.template import RequestContext
from django.utils.simplejson import dumps
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.utils.translation import gettext as _
from artworks.models import Artwork, Serie
from django_descriptors.models import Descriptor

def series_list(request):
    orderby = None
    serie_list = None
    orderby = request.GET.get('orderby', None)
    if orderby is None:
        orderby = 'title'
    if orderby == 'no_of_artworks':
        serie_list = Serie.objects.annotate(no_of_artwork=Count('artwork')).order_by('no_of_artwork')
    else:
        serie_list = Serie.objects.order_by(orderby)
    paginator = Paginator(serie_list, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    series = paginator.page(page)
    return render_to_response('serie_list.html',
                              {"series": series, "order": orderby}, context_instance=RequestContext(request))


def series_record(request, serie_id):
    request.breadcrumbs('Series', reverse('series_list'))
    serie_id = int(serie_id)
    serie = None
    artworks = None
    serie = Serie.objects.get(id=serie_id)
    artworks_list = Artwork.objects.filter(serie=serie_id)
    paginator = Paginator(artworks_list, 5)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    artworks = paginator.page(page)
    return render_to_response('serie.html',
                              {"serie": serie, "artworks": artworks}, context_instance=RequestContext(request))
    
    
def artworks_list(request):
    orderby = None
    artwork_list = None
    orderby = request.GET.get('orderby', None)
    if orderby is None:
        orderby = 'title'
    if orderby == 'creation_year_start':
        artwork_list = Artwork.objects.order_by('creation_year_start', 'creation_year_end')
    else:
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
    description = Descriptor.objects.get_for_object(artwork)   
    return render_to_response('artworks.html',
                              {"artwork": artwork, 'descriptor':description}, context_instance=RequestContext(request))
   

def in_range(request, year_from, year_to):
    year_from = int(year_from)
    year_to = int(year_to)
    artworks_by = request.GET.get("filter", "artwork_current_place")
    dics = []
    if artworks_by == "artwork_original_place":
        filter_args = {
            'original_place__title__isnull': False,
            'original_place__point__isnull': False,
        }
        place_field_name = "original_place"
    else:
        filter_args = {
            'current_place__title__isnull': False,
            'current_place__point__isnull': False,
        }
        place_field_name = "current_place"
    artworks = Artwork.objects.in_range(year_from,
                                        year_to).filter(**filter_args)
    for artwork in artworks:
        place_field = getattr(artwork, place_field_name)
        if place_field.geometry:
            place_title = u"%s (%s)" % (place_field.title, _("region"))
            print place_title
        else:
            place_title = place_field.title
        dic = {
            'identifier': artwork.id,
            'title': artwork.title,
            'place': place_title,
            'coordinates': place_field.point.wkt,
        }
        dics.append(dic)
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

