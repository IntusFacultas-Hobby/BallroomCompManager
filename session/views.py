import datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import authenticate
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views import View
from session.forms import SignUpForm
from competitor.forms import (
    AssociationForm, DancerForm, StudioRequestForm, StudioForm)
from competitor.models import Dancer, Request
from competition.models import Couple


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.save()
            name = user.first_name + " " + user.last_name
            dancer = Dancer(profile=user, name=name, email=user.email)
            dancer.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            # login(request, user)
            return HttpResponseRedirect(reverse('session:login'))
    else:
        form = SignUpForm()
    return render(request, 'session/signup.html', {'form': form})


class ProfileView(LoginRequiredMixin, View):
    def return_context(self, request, user, dancer, dancer_form=None,
                       form=None, change_password_form=None):
        data = {
            'user': None,
            'dancer': None,
            'dancer_form': None,
            'form': None,
            'change_password_form': None,
        }
        data["user"] = user
        data["dancer"] = dancer
        cutoff = datetime.date.today() - datetime.timedelta(days=30)
        roles = dancer.roles.filter(competition__date_of_start__gte=cutoff)
        data['roles'] = roles
        if (dancer_form is None):
            dancer_form = DancerForm(instance=dancer)
            data["dancer_form"] = dancer_form
        else:
            data["dancer_form"] = dancer_form
        if (form is None):
            form = AssociationForm(dancer)
            data["form"] = form
        else:
            data["form"] = form
        if (change_password_form is None):
            change_password_form = PasswordChangeForm(dancer)
            data["change_password_form"] = change_password_form
        else:
            data["change_password_form"] = change_password_form
        return data

    def get(self, request):
        request_user = request.user
        user = User.objects.get(username=request_user.username)
        dancer = user.dancer
        data = self.return_context(request=request, user=user, dancer=dancer)
        return render(request, 'session/account.html', data)

    def post(self, request):
        user = User.objects.get(username=request.user.username)
        if request.POST.get("form_type") == 'dancer_form':
            form = DancerForm(instance=request.user.dancer, data=request.POST)
            if form.is_valid():
                try:
                    validate_email(request.POST.get("email"))
                except ValidationError:
                    form.add_error("email", "Input a valid email.")
                    dancer = user.dancer
                    data = self.return_context(request=request, user=user,
                                               dancer=dancer, dancer_form=form)
                    return render(request, 'session/account.html', data)
                dancer = form.save()
                messages.success(request, "Information updated")
                return HttpResponseRedirect(reverse("session:account"))
            else:
                dancer = user.dancer
                data = self.return_context(request=request, user=user,
                                           dancer=dancer, form=form)
                messages.error(request, "Please check form and try again.")
                return render(request, 'session/account.html', data)
        elif request.POST.get("form_type") == 'change_password_form':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                user = request.user
                dancer = user.dancer
                messages.success(
                    request,
                    "Password updated.")
                return HttpResponseRedirect(reverse('session:account'))
            else:
                user = request.user
                dancer = user.dancer
                data = self.return_context(request=request, user=user,
                                           dancer=dancer,
                                           change_password_form=form)
                messages.error(request, "Please check form and try again.")
                return render(request, 'session/account.html', data)
        elif request.POST.get("form_type") == "association_form":
            form = AssociationForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    "Request sent."
                )
                user = request.user
                dancer = user.dancer
                return HttpResponseRedirect(reverse('session:account'))
            else:
                user = request.user
                dancer = user.dancer
                data = self.return_context(request=request, user=user,
                                           dancer=dancer,
                                           form=form)
                messages.error(
                    request,
                    "No studio exists with this pin."
                )
                return render(request, 'session/account.html', data)


class RegistrationsView(LoginRequiredMixin, View):
    def get(self, request):
        request_user = request.user
        user = User.objects.get(username=request_user.username)
        dancer = user.dancer
        events = Couple.objects.filter(Q(lead=dancer) | Q(follow=dancer))
        return render(request, 'session/account_registrations.html', {
            "events": events,
        })


class StudioView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user
        if user.dancer.owned_studio is None:
            form = StudioRequestForm(instance=request.user)
            return render(request, 'session/studio_request.html', {
                "form": form,
            })
        else:
            form = StudioForm(instance=user.dancer.owned_studio)
            dancers = Dancer.objects.filter(studio=user.dancer.owned_studio)
            requests = Request.objects.filter(studio=user.dancer.owned_studio)
            competitions = user.dancer.owned_studio.competitions.all()
            return render(request, 'session/studio_management.html', {
                "form": form,
                "studio": user.dancer.owned_studio,
                "dancers": dancers,
                "requests": requests,
                "competitions": competitions,
            })

    def post(self, request):
        type = request.POST.get("type")
        if type == 'studio_request':
            form = StudioRequestForm(data=request.POST)
            if form.is_valid():
                studio_request = form.save(commit=False)
                studio_request.user = request.user
                studio_request.save()
                messages.success(
                    request,
                    "Studio request submitted.")
                return HttpResponseRedirect(reverse('session:account'))
            else:
                messages.error(request, "Please review form and try again.")
                return render(request, 'session/studio_management.html', {
                    "form": form,
                })


class DeleteDancer(LoginRequiredMixin, View):
    def return_default(self, request, user):
        form = StudioForm(instance=user.dancer.owned_studio)
        dancers = Dancer.objects.filter(studio=user.dancer.owned_studio)
        requests = Request.objects.filter(studio=user.dancer.owned_studio)
        return render(request, 'session/studio_management.html', {
            "form": form,
            "studio": user.dancer.owned_studio,
            "dancers": dancers,
            "requests": requests
        })

    def post(self, request):
        post_data = request.POST.copy()
        del post_data["csrfmiddlewaretoken"]
        user = request.user
        if (user.dancer.owned_studio):
            for key in post_data:
                dancer = Dancer.objects.get(pk=key)
                if (user.dancer.owned_studio == dancer.studio and
                        post_data[key] == "on"):
                    dancer.studio = None
                    dancer.save()
                else:
                    messages.error(
                        request, "Cannot delete dancer that does not belong to your studio")
                    return self.return_default(request, user)
            messages.success(request, "Dancers removed.")
            return HttpResponseRedirect(reverse('session:studio'))
        else:
            messages.error(
                request, "Bad request on Dancer Removal. Contact Support")
            return HttpResponseRedirect(reverse('session:studio'))


class RequestConfirm(LoginRequiredMixin, View):
    def return_default(self, request, user):
        form = StudioForm(instance=user.dancer.owned_studio)
        dancers = Dancer.objects.filter(studio=user.dancer.owned_studio)
        requests = Request.objects.filter(studio=user.dancer.owned_studio)
        return render(request, 'session/studio_management.html', {
            "form": form,
            "studio": user.dancer.owned_studio,
            "dancers": dancers,
            "requests": requests
        })

    def post(self, request):
        user = request.user
        data = request.POST.copy()
        del data["csrfmiddlewaretoken"]
        if (user.dancer.owned_studio):
            for key in data:
                req = Request.objects.get(pk=key)
                print("Information forthcoming:")
                print(data[key])
                if (req.studio == user.dancer.owned_studio and
                        data[key] == "on"):
                    req.dancer.studio = req.studio
                    req.dancer.save()
                    req.delete()
                else:
                    messages.error(
                        request, "Cannot modify requests that do not belong to your studio")
                    return self.return_default(request, user)
            messages.success(request, "Requests confirmed.")
            return HttpResponseRedirect(reverse('session:studio'))
        else:
            messages.error(
                request, "Bad request on Request Confirm. Contact Support.")
            return HttpResponseRedirect(reverse('session:studio'))


class RequestDelete(LoginRequiredMixin, View):

    def post(self, request):
        user = request.user
        data = request.POST.copy()
        del data["csrfmiddlewaretoken"]
        if (user.dancer.owned_studio):
            for key in data:
                request = Request.objects.get(pk=key)
                if (request.studio == user.dancer.owned_studio and
                        data[key] == "on"):
                    request.delete()
                else:
                    return HttpResponse("Cannot modify requests that do not belong to your studio",
                                        status=400)
            return HttpResponse("Ok", status=200)
        else:
            return HttpResponse("Bad request", status=400)
