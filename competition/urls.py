from django.conf.urls import url
from competition.views import CompetitionListView
app_name = "competition"

urlpatterns = [
    url(r'^$', CompetitionListView.as_view(), name="index"),
]