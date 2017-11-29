from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.views import View
from session.forms import SignUpForm
from competitor.forms import AssociationForm, DancerForm
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
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'session/signup.html', {'form': form})


class ProfileView(LoginRequiredMixin, View):

    def get(self, request):
        request_user = request.user
        user = User.objects.get(username=request_user.username)
        dancer = user.dancer
        dancer_form = DancerForm(instance=user.dancer)
        form = AssociationForm(request.user)
        change_password_form = PasswordChangeForm(request.user)
        return render(request, 'session/account.html',
                      {
                          'user': user,
                          'dancer': dancer,
                          'dancer_form': dancer_form,
                          'form': form,
                          'change_password_form': change_password_form,
                      }
                      )
