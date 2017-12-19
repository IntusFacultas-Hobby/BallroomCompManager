from django.conf.urls import url
from competition.views import (
    CompetitionListView, CompetitionCreateView,
    CompetitionAddEvents, CompetitionEditView)
app_name = "competition"

urlpatterns = [
    url(r'^$', CompetitionListView.as_view(), name="index"),
    url(r'^competition/(?P<competition>[0-9+])$',
        CompetitionEditView.as_view(), name="edit"),
    url(r'^competition/create/(?P<competition>[0-9]+)/events$',
        CompetitionAddEvents.as_view(), name="events-create"),
    url(r'^competition/create/$', CompetitionCreateView.as_view(),
        name="create"),
]
