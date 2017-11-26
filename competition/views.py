from django.views.generic.list import ListView
from competition.models import Competition
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin


class CompetitionListView(LoginRequiredMixin, ListView):

    model = Competition

    def get_context_data(self, **kwargs):
        context = super(CompetitionListView, self).get_context_data(**kwargs)
        return context
