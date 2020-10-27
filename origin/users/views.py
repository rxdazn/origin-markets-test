from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rest_framework.authtoken.models import Token

from users.forms import UserCreationForm


def sign_up(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "users/sign_up.html", {"form": form})


@login_required
def home(request):
    try:
        api_key = Token.objects.get(user=request.user)
    except Token.DoesNotExist:
        api_key = "No API key found"
    return render(request, "users/home.html", {"api_key": api_key})
