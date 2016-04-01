from django.shortcuts import render

# Create your views here.

from models import Content
from django.template import RequestContext
from django.shortcuts import render_to_response


def search(request):
    try:
        query = request.GET.get('q')
    except ValueError:
        query = None
        results = None
    if query:
        results = Content.objects.get(html=query)
    context = RequestContext(request)
    return render_to_response('results.html',
                              {"results": results, },
                              context_instance=context)
