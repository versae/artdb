# Create your views here.
from django.shortcuts import HttpResponse, render_to_response
from django.template import RequestContext
from django.utils.simplejson import dumps
from django.core.urlresolvers import reverse
from creators.models import Creator


def creator_record(request, creator_id):
    request.breadcrumbs('Creators', reverse('creators_list'))
    creator_id = int(creator_id)
    creator = None
    creator = Creator.objects.get(id=creator_id)
    return render_to_response('creators.html',
                              {"creator": creator}, context_instance=RequestContext(request))
    
    
def creators_list(request):
    return render_to_response('creators_list.html',
                              {}, context_instance=RequestContext(request))