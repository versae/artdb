# -*-*- coding: utf-8 -*-
from django.db.models import Q
from django.shortcuts import HttpResponse, render_to_response
from django.template import RequestContext
from django.utils.simplejson import dumps
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.utils.translation import gettext as _

from artworks.models import Artwork
from base.models import GeospatialReference


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
    

def artworks_locations(request, year_from, year_to):
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
        place_field = "original_places"
    else:
        filter_args = {
            'current_place__title__isnull': False,
            'current_place__point__isnull': False,
        }
        place_field_name = "current_place"
        place_field = "current_places"
    filter_params = ((
        (Q(**{"%s__creation_year_start__lte" % place_field: year_from}) &
         Q(**{"%s__creation_year_end__gte" % place_field: year_from})) |
        (Q(**{"%s__creation_year_start__gte" % place_field: year_from}) &
         Q(**{"%s__creation_year_end__lte" % place_field: year_to})) |
        (Q(**{"%s__creation_year_start__lte" % place_field: year_from}) &
         Q(**{"%s__creation_year_end__gte" % place_field: year_from}))) &
        Q(**{"title__isnull": False}) &
        Q(**{"point__isnull": False})
    )
    locations = GeospatialReference.objects.filter(filter_params).distinct()
    for location in locations:
        if location.geometry:
            location_place = u"%s (%s)" % (location.title, _("region"))
            location_coordinates = location.geometry.wkt
        else:
            location_place = location.title
            location_coordinates = location.point.wkt
        dic = {
            'identifier': location.id,
            'place': location_place,
            'title': location.address,
            'coordinates': location_coordinates,
        }
        dics.append(dic)
    return HttpResponse(dumps(dics), mimetype="application/json")


def artworks_properties(request, artwork_id):
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
