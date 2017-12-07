from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'session_security/', include('session_security.urls')),
    url(r'^select2/', include('django_select2.urls')),
    url(r'', include('session.urls')),
    url(r'', include('competition.urls')),
    url(r'', include('competitor.urls')),
]
