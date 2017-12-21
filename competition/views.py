import datetime
import json
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from competition.models import Competition, Staff
from competition.forms import CompetitionForm, EventFormSet
from competitor.models import Dancer


class CompetitionCreateView(LoginRequiredMixin, View):
    def get(self, request):
        if (request.user.dancer.owned_studio is None):
            messages.error(
                request, "You need a studio to create a competition.")
            return HttpResponseRedirect(reverse("session:studio"))
        else:
            form = CompetitionForm()
            dancers = Dancer.objects.all()
            dictionaries = [obj.as_dict() for obj in dancers]
            return render(request, 'competition/competition_create.html', {
                "form": form,
                "users": dictionaries
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
                data = request.POST.get("staff")
                data = json.loads(data)
                for entry in data:
                    person = entry["person"]
                    role = int(entry["role"])
                    dancer = Dancer.objects.get(
                        judging_pin=person["judging_pin"])
                    role = Staff.ROLE_CHOICES[role]
                    Staff.objects.create(
                        competition=competition,
                        dancer=dancer,
                        role=role[0]
                    )
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
            formset = EventFormSet(instance=comp)
            form = CompetitionForm(instance=comp)
            dancers = Dancer.objects.exclude(roles__competition=comp)
            dictionaries = [obj.as_dict() for obj in dancers]
            staff = Staff.objects.filter(competition=comp)
            staff_dictionaries = [obj.as_dict() for obj in staff]
            return render(request, 'competition/competition_edit.html', {
                "formset": formset,
                "form": form,
                "competition": comp,
                "users": dictionaries,
                "staff": staff_dictionaries
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
        elif request.POST.get("form_type") == 'staff':
            data = request.POST.get("staff")
            data = json.loads(data)
            Staff.objects.filter(competition=comp).delete()
            for entry in data:
                person = entry["person"]
                role = int(entry["role"])
                dancer = Dancer.objects.get(judging_pin=person["judging_pin"])
                role = Staff.ROLE_CHOICES[role]
                Staff.objects.create(
                    competition=comp,
                    dancer=dancer,
                    role=role[0]
                )
            messages.success(request, "Staff successfully added.")
            return HttpResponseRedirect(
                reverse("competition:edit",
                        kwargs={'competition': comp.pk}))
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
