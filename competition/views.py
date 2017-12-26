import datetime
import json
import hashlib
from itertools import chain
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from competition.models import (Competition, Staff, Event,
                                Mark, Performance, Couple)
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
                form = CompetitionForm(instance=comp)
                return render(request, 'competition/competition_edit.html', {
                    "formset": formset,
                    "form": form,
                    "competition": comp
                })
            else:
                comp.events.all().delete()
                for form in formset:
                    if (form.is_valid() and
                            form.cleaned_data.get('DELETE') is False):
                        event = form.save(commit=False)
                        event.competition = comp
                        event.save()
                messages.success(request, "Competition successfully updated.")
                return HttpResponseRedirect(
                    reverse("competition:edit",
                            kwargs={'competition': comp.pk}))


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


class CompetitionManageView(LoginRequiredMixin, View):
    def find_heat(self, heats, pk):
        pk = int(pk)
        print("Finding " + str(pk))
        print(heats)
        for heat in heats:
            print(str(heat) + " pk=" + str(heat.pk))
            if heat.pk == pk:
                return heat
        return None

    def update_hash(self, competition):
        events = competition.events.all()
        rounds = []
        for event in events:
            rounds = chain(rounds, event.heats.all())
        rounds = list(rounds)
        ordered_array = json.loads(competition.heat_list)
        ordered_heats = []
        for pk in ordered_array:
            heat = self.find_heat(rounds, pk)
            ordered_heats.append({
                "id": heat.pk,
                "dancers": list(heat.couples.all().values_list(
                    "couple_number",
                    flat=True
                ))
            })
        status = json.dumps(ordered_heats)
        status = status.replace(" ", "")
        status = status.encode("utf-8")
        hash_output = hashlib.sha256()
        hash_output.update(status)
        hash_output = hash_output.hexdigest()
        return hash_output

    def generate_round_population(self, population, limit):
        # population is smaller than limit, just have one round
        if population < limit:
            return {
                "number_of_heats": 1,
                "limit": limit,
                "exception": 0,
            }
        # population easily divides into event limit
        elif population % limit == 0:
            return {
                "number_of_heats": population / limit,
                "limit": limit,
                "exception": 0,
            }
        else:
            left_over = population % limit
            number_of_heats_without_leftover = int(population / limit)
            attempted_dispersal = left_over % number_of_heats_without_leftover
            cut_off_for_creating_new_event = int(limit * .6)
            if (attempted_dispersal == 0 and
                    left_over < cut_off_for_creating_new_event):
                # leftover dancers can be evenly dispersed between the
                # other heats and aren't enough to warrant another round
                return {
                    "number_of_heats": number_of_heats_without_leftover,
                    "limit": limit +
                    (left_over / number_of_heats_without_leftover),
                    "exception": 0,
                }
            # leftover dancers too many to just add to last heat.
            # Create one more underpopulated round for the remainder
            elif (left_over > cut_off_for_creating_new_event):
                return {
                    "number_of_heats": number_of_heats_without_leftover + 1,
                    "limit": limit,
                    "exception": 0,
                }
            else:
                # there are fewer than the cutoff to make a new round but
                # they cannot be evenly distributed. Increase event heat limit,
                # try and minimize how many have to be added to each round
                # then add the remainder to the final round
                return {
                    "number_of_heats": number_of_heats_without_leftover,
                    "limit": limit +
                    (int(
                        left_over / number_of_heats_without_leftover
                    )),
                    "exception": attempted_dispersal,
                }

    def get(self, request, competition):
        comp = Competition.objects.get(pk=competition)
        roles_in_comp = request.user.dancer.roles.filter(competition=comp)
        print(request.user.dancer)
        print(len(request.user.dancer.roles.filter(competition=comp)))
        unqualified = False
        if len(roles_in_comp) == 0:
            unqualified = True
        if ((request.user.dancer.owned_studio is None or
                comp.host != request.user.dancer.owned_studio) and unqualified):
            messages.error(
                request,
                "You do not have permission to manage this competition."
            )
            return HttpResponseRedirect(reverse("session:account"))
        dancers = Dancer.objects.exclude(roles__competition=comp)
        dictionaries = [obj.as_dict() for obj in dancers]
        staff = Staff.objects.filter(competition=comp)
        staff_dictionaries = [obj.as_dict() for obj in staff]
        events = Event.objects.filter(competition=comp)
        events_dict = [obj.as_dict() for obj in events]
        rounds = []
        for event in events:
            rounds = chain(rounds, event.heats.all())
        rounds = list(rounds)
        ordered_array = json.loads(comp.heat_list)
        ordered_heats = []
        for pk in ordered_array:
            heat = self.find_heat(rounds, pk)

            ordered_heats.append(heat)
        heat_list = comp.heat_list
        if heat_list != "" and heat_list is not None:
            heat_list = json.loads(heat_list)
        heats_dict = [obj.as_dict() for obj in ordered_heats]
        return render(request, "competition/competition_management.html", {
            "competition": comp,
            "users": dictionaries,
            "staff": staff_dictionaries,
            "events": events_dict,
            "heats": heats_dict,
            "heat_list": comp.heat_list
        })

    def post(self, request, competition):
        comp = Competition.objects.get(pk=competition)
        if request.POST.get("form_type") == 'competition_start':
            comp.begun = True
            comp.save()
            events = Event.objects.filter(competition=comp)
            for event in events:
                num_event_couples = event.couples.count()
                event_heat_limit = event.max_per_heat
                round_calculation = num_event_couples
                round_counter = 0
                while (round_calculation > 3):
                    print("round_calculation " + str(round_calculation))
                    # create heats here
                    round_counter += 1
                    round_population = self.generate_round_population(
                        round_calculation,
                        event_heat_limit
                    )
                    print("round_population " + json.dumps(round_population))
                    num_heats = round_population["number_of_heats"]
                    for x in range(0, num_heats):
                        event.heats.create(round_number=round_counter)
                    round_calculation = int(round_calculation / 2)
                # add couples to first round events
                first_round_heats = event.heats.filter(round_number=1)
                event_couples = event.couples.all()
                round_stats = self.generate_round_population(
                    num_event_couples,
                    event_heat_limit
                )
                added_couples = 0
                current_round_being_populated = 0
                for couple in event_couples:
                    if added_couples >= round_stats["limit"]:
                        if (current_round_being_populated + 1 !=
                                round_stats["number_of_heats"]):
                            current_round_being_populated += 1
                        added_couples = 0
                    first_round_heats[current_round_being_populated].couples.add(
                        couple
                    )
                    added_couples += 1
            messages.success(
                request,
                "Competition begun, first rounds populated, rest of rounds generated."
            )
            return HttpResponseRedirect(
                reverse("competition:manage",
                        kwargs={'competition': comp.pk}))

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
            messages.success(request, "Staff successfully updated.")
            return HttpResponseRedirect(
                reverse("competition:manage",
                        kwargs={'competition': comp.pk}))
        elif request.POST.get("form_type") == "order":
            data = request.POST.getlist("heatOrder[]")
            print("Previous Heat List: " + comp.heat_list)
            comp.heat_list = json.dumps(data)
            print("New Heat List: " + comp.heat_list)
            comp.save()
            print("Previous status: " + comp.status)
            comp.status = self.update_hash(comp)
            comp.save()
            print("New status: " + comp.status)
            return HttpResponse("Ok", status=200)
        elif request.POST.get("form_type") == "checkin":
            data = request.POST.get("hash")
            status = comp.status
            print("From Client " + data)
            print("From Server " + status)
            if (data == status):
                return HttpResponse("Ok", status=200)
            else:
                return HttpResponse("Update", status=201)


class CompetitionAJAX(View):
    def get(self, request):
        dancers = Dancer.objects.all()
        dictionaries = [obj.as_dict() for obj in dancers]
        response = {"dancers": dictionaries}
        return JsonResponse(response)


class CompetitionSignupView(LoginRequiredMixin, View):
    def get(self, request, competition):
        comp = Competition.objects.get(pk=competition)
        dancers = Dancer.objects.all()
        dictionaries = [obj.as_dict() for obj in dancers]
        events = Event.objects.filter(competition=comp)
        events_dict = [obj.as_dict() for obj in events]
        return render(request, "competition/competition_signup.html", {
            "competition": comp,
            "users": dictionaries,
            "events": events_dict
        })

    def post(self, request, competition):
        comp = Competition.objects.get(pk=competition)
        events = json.loads(request.POST.get("events"))
        events_to_be_added = []
        for event in events:
            django_event = object
            try:
                django_event = Event.objects.get(pk=event["id"])
            except ObjectDoesNotExist:
                messages.error(
                    request,
                    "Event does not exist. Please contact SysAdmin."
                )
                dancers = Dancer.objects.all()
                dictionaries = [obj.as_dict() for obj in dancers]
                events = Event.objects.filter(competition=comp)
                events_dict = [obj.as_dict() for obj in events]
                return render(request, "competition/competition_signup.html", {
                    "competition": comp,
                    "users": dictionaries,
                    "events": events_dict
                })
            couple = event["couple"]
            lead = couple[0]
            follow = couple[1]
            django_couple = object
            try:
                django_couple = Couple.objects.get(
                    lead__judging_pin=lead["judging_pin"],
                    follow__judging_pin=follow["judging_pin"],
                    competition=comp,
                )
                # remove events prior to adding
                django_couple.events.clear()
            except ObjectDoesNotExist:
                number = comp.couples.count() + 1
                django_lead = Dancer.objects.get(
                    judging_pin=lead["judging_pin"]
                )
                django_follow = Dancer.objects.get(
                    judging_pin=follow["judging_pin"]
                )
                django_couple = Couple.objects.create(
                    lead=django_lead,
                    follow=django_follow,
                    competition=comp,
                    couple_number=number
                )

            if len(django_couple.events.filter(pk=django_event.pk)) == 0:
                # event hasn't been added to couple yet
                events_to_be_added.append({
                    "couple": django_couple,
                    "event": django_event
                })

        for pair in events_to_be_added:
            couple = pair["couple"]
            print(pair["event"])
            couple.events.add(pair["event"])
        messages.success(
            request,
            "Signup successful. Check your profile \
             for registration information"
        )
        return HttpResponseRedirect(reverse("competition:index"))
