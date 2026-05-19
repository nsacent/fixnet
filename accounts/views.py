from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from .forms import ClientRegistrationForm, TechnicianRegistrationForm
from .models import User


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        user = self.request.user

        if user.role == User.ROLE_TECHNICIAN:
            return "/technician/dashboard/"

        if user.role == User.ROLE_ADMIN or user.is_superuser:
            return "/admin/"

        return "/client/dashboard/"


class CustomLogoutView(LogoutView):
    next_page = "/"


def register_client(request):
    if request.method == "POST":
        form = ClientRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/client/dashboard/")
    else:
        form = ClientRegistrationForm()

    return render(request, "accounts/register_client.html", {
        "form": form
    })


def register_technician(request):
    if request.method == "POST":
        form = TechnicianRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/technician/dashboard/")
    else:
        form = TechnicianRegistrationForm()

    return render(request, "accounts/register_technician.html", {
        "form": form
    })