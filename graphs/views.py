# -*-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.simplejson import dumps
from django.utils.translation import gettext as _

from django_descriptors.models import Descriptor
from exhibit.utils import clean_years

from artworks.models import Artwork, Creator


def force_graph(request):
    return render_to_response('force_graph.html',
                              {},
                              context_instance=RequestContext(request))
