from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from session.forms import SignUpForm
from competitor.forms import (
    AssociationForm, DancerForm, StudioRequestForm, StudioForm)
from competitor.models import Dancer


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
            login(request, user)
            return redirect('session:index')
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
        print(data)
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
                data = self.return_context(request=request, user=user,
                                           dancer=dancer)
                return render(request, 'session/account.html', data)
            else:
                dancer = user.dancer
                data = self.return_context(request=request, user=user,
                                           dancer=dancer, form=form)
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
                data = self.return_context(request=request, user=user,
                                           dancer=dancer)
                return render(request, 'session/account.html', data)
            else:
                user = request.user
                dancer = user.dancer
                data = self.return_context(request=request, user=user,
                                           dancer=dancer,
                                           change_password_form=form)
                return render(request, 'session/account.html', data)
        # TODO Studio Association


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
            return render(request, 'session/studio_management.html', {
                "form": form,
                "studio": user.dancer.owned_studio
            })

    def post(self, request):
        type = request.POST.get("type")
        if type == 'studio_request':
            form = StudioRequestForm(data=request.POST)
            if form.is_valid():
                studio_request = form.save(commit=False)
                studio_request.user = request.user
                print(studio_request)
                studio_request.save()
                messages.success(
                    request,
                    "Studio request submitted.")
                return HttpResponseRedirect(reverse('session:account'))
