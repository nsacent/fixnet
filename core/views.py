from django.shortcuts import render, redirect
from requests_app.forms import ServiceRequestForm


def home(request):
    if request.method == "POST":
        form = ServiceRequestForm(request.POST, request.FILES)

        if form.is_valid():
            service_request = form.save(commit=False)

            if request.user.is_authenticated:
                service_request.client = request.user

            service_request.save()
            return redirect("request_success")

    else:
        form = ServiceRequestForm()

    return render(request, "home.html", {
        "form": form
    })


def request_success(request):
    return render(request, "request_success.html")