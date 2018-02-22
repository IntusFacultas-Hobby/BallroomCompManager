from django.conf.urls import url
from competition.views import (
    CompetitionListView, CompetitionCreateView,
    CompetitionAddEvents, CompetitionEditView, CompetitionManageView,
    CompetitionSignupView, CompetitionAJAX, CompetitionAddDances,
    CompetitionActivateView)
app_name = "competition"

urlpatterns = [
    url(r'^$', CompetitionListView.as_view(), name="index"),
    url(r'^competition/(?P<competition>[0-9+])/signup$',
        CompetitionSignupView.as_view(), name="signup"),
    url(r'^competition/(?P<competition>[0-9+])/manage$',
        CompetitionManageView.as_view(), name="manage"),
    url(r'^competition/(?P<competition>[0-9+])$',
        CompetitionEditView.as_view(), name="edit"),
    url(r'^competition/create/(?P<competition>[0-9]+)/dances$',
        CompetitionAddDances.as_view(), name="dances-create"),
    url(r'^competition/create/(?P<competition>[0-9]+)/events$',
        CompetitionAddEvents.as_view(), name="events-create"),
    url(r'^competition/create/$', CompetitionCreateView.as_view(),
        name="create"),
    url(r'^competition/activate/(?P<competition>[0-9]+)',
        CompetitionActivateView.as_view(), name="activate"),
    url(r'^ajax/dancers$', CompetitionAJAX.as_view(), name="ajax-dancers")
]
