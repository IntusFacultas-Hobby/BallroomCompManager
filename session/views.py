from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from session.forms import SignUpForm
from competitor.models import Dancer

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
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