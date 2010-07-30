# Create your views here.
from django.shortcuts import HttpResponse, render_to_response
from django.template import RequestContext
from django.utils.simplejson import dumps

from creators.models import Creator


def creator_record(request):
    creator_id = None
    creator = None
    if request.GET and "id" in request.GET:
        creator_id = int(request.GET.get("id", 0))
    creator = Creator.objects.get(id=creator_id)
    return render_to_response('creators.html',
                              {"creator": creator}, context_instance=RequestContext(request))