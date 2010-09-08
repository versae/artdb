from django.shortcuts import HttpResponse, render_to_response
from django.template import RequestContext
from artworks.models import Artwork
from creators.models import Creator
from random import randint

def public_view(request):
    num_artworks = Artwork.objects.count()
    random_artwork = Artwork.objects.all()[randint(0, num_artworks-1)]
    num_creator = Creator.objects.count()
    random_creator = Creator.objects.all()[randint(0, num_creator-1)]
    return render_to_response('pv_home.html',
                              {"artwork": random_artwork, "artist": random_creator}, context_instance=RequestContext(request))
