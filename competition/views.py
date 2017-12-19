import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from competition.models import Competition
from competition.forms import CompetitionForm, EventFormSet


class CompetitionCreateView(LoginRequiredMixin, View):
    def get(self, request):
        if (request.user.dancer.owned_studio is None):
            messages.error(
                request, "You need a studio to create a competition.")
            return HttpResponseRedirect(reverse("session:studio"))
        else:
            form = CompetitionForm()
            return render(request, 'competition/competition_create.html', {
                "form": form,
            })

    def post(self, request):
        if (request.user.dancer.owned_studio is None):
            messages.error(
                request, "You need a studio to create a competition.")
            return HttpResponseRedirect(reverse("session:studio"))
        else:
            form = CompetitionForm(request.POST)
            if form.is_valid():
                competition = form.save(commit=False)
                competition.host = request.user.dancer.owned_studio
                competition.save()
                messages.success(
                    request, "Competition created. Please add events now.")
                return HttpResponseRedirect(
                    reverse("competition:events-create",
                            kwargs={'competition': competition.pk})
                )


class CompetitionAddEvents(LoginRequiredMixin, View):
    def get(self, request, competition):
        comp = Competition.objects.get(pk=competition)
        if (request.user.dancer.owned_studio is None or
                comp.host != request.user.dancer.owned_studio):
            messages.error(
                request,
                "You do not have permission to modify this competition."
            )
            return HttpResponseRedirect(reverse("session:studio"))
        else:
            formset = EventFormSet()
            return render(request, 'competition/add_events.html', {
                "formset": formset,
                "competition": comp
            })

    def post(self, request, competition):
        comp = Competition.objects.get(pk=competition)
        if (request.user.dancer.owned_studio is None or
                comp.host != request.user.dancer.owned_studio):
            messages.error(
                request,
                "You do not have permission to modify this competition."
            )
            return HttpResponseRedirect(reverse("session:studio"))
        formset = EventFormSet(request.POST)
        if formset.is_valid() is False:
            messages.error(
                request, "Please review the forms and try again.")
            return render(request, 'competition/add_events.html', {
                "formset": formset,
                "competition": comp
            })
        for form in formset:
            if form.is_valid():
                event = form.save(commit=False)
                event.competition = comp
                event.save()
        messages.success(request, "Events added successfully")
        return HttpResponseRedirect(reverse("session:studio"))


class CompetitionEditView(LoginRequiredMixin, View):
    def get(self, request, competition):
        comp = Competition.objects.get(pk=competition)
        if (request.user.dancer.owned_studio is None or
                comp.host != request.user.dancer.owned_studio):
            messages.error(
                request,
                "You do not have permission to modify this competition."
            )
            return HttpResponseRedirect(reverse("session:studio"))
        else:
            events = comp.events.all().values()
            print(events)
            formset = EventFormSet(instance=comp)
            form = CompetitionForm(instance=comp)
            return render(request, 'competition/competition_edit.html', {
                "formset": formset,
                "form": form,
                "competition": comp
            })

    def post(self, request, competition):
        comp = Competition.objects.get(pk=competition)
        if (request.user.dancer.owned_studio is None or
                comp.host != request.user.dancer.owned_studio):
            messages.error(
                request,
                "You do not have permission to modify this competition."
            )
            return HttpResponseRedirect(reverse("session:studio"))
        events = comp.events
        if request.POST.get("form_type") == 'competition':
            print("competition")
            form = CompetitionForm(request.POST, instance=comp)
            if form.is_valid():
                saved_comp = form.save(commit=False)
                saved_comp.host = request.user.dancer.owned_studio
                saved_comp.save()
                print(saved_comp.date_of_start)
                messages.success(request, "Competition successfully updated.")
                return HttpResponseRedirect(
                    reverse("competition:edit",
                            kwargs={'competition': comp.pk}))
            else:
                messages.error(request, "Please check form and try again.")
                formset = EventFormSet(events)
                return render(request, 'competition/competition_edit.html', {
                    "formset": formset,
                    "form": form,
                    "competition": comp
                })
        else:
            formset = EventFormSet(request.POST, instance=comp)
            if formset.is_valid() is False:
                form = CompetitionForm(comp)
                return render(request, 'competition/competition_edit.html', {
                    "formset": formset,
                    "form": form,
                    "competition": comp
                })
            else:
                for form in formset:
                    if form.is_valid():
                        event = form.save(commit=False)
                        event.competition = comp
                        event.save()
                messages.success(request, "Competition successfully updated.")
                return HttpResponseRedirect(
                    reverse("competition:edit", kwargs={'competition': comp.pk}))


class CompetitionListView(LoginRequiredMixin, View):
    def get(self, request):
        upcoming = Competition.objects.filter(
            date_of_start__gte=datetime.date.today())
        past = Competition.objects.filter(
            date_of_start__lte=datetime.date.today())
        return render(request, "competition/competition_list.html", {
            "competitions": upcoming,
            "past_competitions": past
        })
