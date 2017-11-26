from django.shortcuts import render
from django.http import HttpResponseRedirect
# Create your views here.

def index(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/login/")
    return render(
        request,
        'competitor/index.html',
        {

        }
    )