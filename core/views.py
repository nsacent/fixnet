from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from requests_app.forms import ServiceRequestForm
from requests_app.models import ServiceRequest

from reviews.forms import ReviewForm
from reviews.models import Review
from services.models import ServiceCategory

from technicians.forms import TechnicianProfileForm

"""Admins"""
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import User
from technicians.models import TechnicianProfile
from requests_app.admin_forms import (
    AssignTechnicianForm,
    UpdateRequestStatusForm,
    UpdateAdminNotesForm,
    UpdateFinalPriceForm,
)

def home(request):
    if request.method == "POST":
        form = ServiceRequestForm(request.POST, request.FILES)

        if form.is_valid():
            service_request = form.save(commit=False)

            if request.user.is_authenticated:
                service_request.client = request.user

            if service_request.category:
                service_request.estimated_price = service_request.category.starting_price

            service_request.save()
            return redirect("request_success")
    else:
        form = ServiceRequestForm()

    service_categories = ServiceCategory.objects.filter(
        is_active=True
    ).order_by("name")[:8]

    return render(request, "home.html", {
        "form": form,
        "service_categories": service_categories,
    })


def request_success(request):
    return render(request, "request_success.html")


@login_required
def client_dashboard(request):
    requests = ServiceRequest.objects.filter(
        client=request.user
    ).select_related(
        "category",
        "assigned_technician",
        "assigned_technician__user",
    )

    return render(request, "client/dashboard.html", {
        "requests": requests
    })


@login_required
def technician_dashboard(request):
    technician_profile = getattr(request.user, "technician_profile", None)

    assigned_requests = ServiceRequest.objects.none()
    pending_requests = ServiceRequest.objects.filter(
        status=ServiceRequest.STATUS_PENDING
    ).select_related("category", "client")

    if technician_profile:
        assigned_requests = ServiceRequest.objects.filter(
            assigned_technician=technician_profile
        ).select_related("category", "client")

    return render(request, "technician/dashboard.html", {
        "technician_profile": technician_profile,
        "assigned_requests": assigned_requests,
        "pending_requests": pending_requests,
    })

@login_required
def accept_request(request, request_id):
    technician_profile = getattr(request.user, "technician_profile", None)

    if not technician_profile:
        messages.error(request, "You do not have a technician profile.")
        return redirect("technician_dashboard")

    if not technician_profile.is_verified:
        messages.error(request, "Your technician account is not verified yet. Please wait for admin approval.")
        return redirect("technician_dashboard")

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
        status=ServiceRequest.STATUS_PENDING
    )

    service_request.assigned_technician = technician_profile
    service_request.status = ServiceRequest.STATUS_ACCEPTED
    service_request.save()

    messages.success(request, "Job accepted successfully.")
    return redirect("technician_dashboard")

@login_required
def start_request(request, request_id):
    technician_profile = getattr(request.user, "technician_profile", None)

    if not technician_profile:
        messages.error(request, "You do not have a technician profile.")
        return redirect("technician_dashboard")

    service_request = get_object_or_404(
    ServiceRequest,
    id=request_id,
    assigned_technician=technician_profile,
    status__in=[
        ServiceRequest.STATUS_ASSIGNED,
        ServiceRequest.STATUS_ACCEPTED,
    ],
    )

    service_request.status = ServiceRequest.STATUS_IN_PROGRESS
    service_request.save()

    messages.success(request, "Job marked as in progress.")
    return redirect("technician_dashboard")


@login_required
def complete_request(request, request_id):
    technician_profile = getattr(request.user, "technician_profile", None)

    if not technician_profile:
        messages.error(request, "You do not have a technician profile.")
        return redirect("technician_dashboard")

    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
        assigned_technician=technician_profile,
        status=ServiceRequest.STATUS_IN_PROGRESS,
    )

    service_request.status = ServiceRequest.STATUS_COMPLETED
    service_request.completed_at = timezone.now()
    service_request.save()

    messages.success(request, "Job marked as completed.")
    return redirect("technician_dashboard")

@login_required
def leave_review(request, request_id):
    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
        client=request.user,
        status=ServiceRequest.STATUS_COMPLETED,
    )

    if not service_request.assigned_technician:
        messages.error(request, "This request has no assigned technician.")
        return redirect("client_dashboard")

    existing_review = Review.objects.filter(
        request=service_request
    ).first()

    if existing_review:
        messages.info(request, "You have already reviewed this job.")
        return redirect("client_dashboard")

    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.client = request.user
            review.technician = service_request.assigned_technician
            review.request = service_request
            review.save()

            messages.success(request, "Review submitted successfully.")
            return redirect("client_dashboard")
    else:
        form = ReviewForm()

    return render(request, "client/leave_review.html", {
        "form": form,
        "service_request": service_request,
    })   

@login_required
def client_request_detail(request, request_id):
    service_request = get_object_or_404(
        ServiceRequest.objects.select_related(
            "category",
            "assigned_technician",
            "assigned_technician__user",
            "review",
        ),
        id=request_id,
        client=request.user,
    )

    return render(request, "client/request_detail.html", {
        "service_request": service_request,
    })    

@login_required
def edit_technician_profile(request):
    technician_profile = getattr(request.user, "technician_profile", None)

    if not technician_profile:
        messages.error(request, "You do not have a technician profile.")
        return redirect("technician_dashboard")

    if request.method == "POST":
        form = TechnicianProfileForm(request.POST, instance=technician_profile)

        if form.is_valid():
            form.save()
            messages.success(request, "Technician profile updated successfully.")
            return redirect("technician_dashboard")
    else:
        form = TechnicianProfileForm(instance=technician_profile)

    return render(request, "technician/edit_profile.html", {
        "form": form,
        "technician_profile": technician_profile,
    })

@login_required
def technician_request_detail(request, request_id):
    technician_profile = getattr(request.user, "technician_profile", None)

    if not technician_profile:
        messages.error(request, "You do not have a technician profile.")
        return redirect("technician_dashboard")

    service_request = get_object_or_404(
        ServiceRequest.objects.select_related(
            "category",
            "client",
            "assigned_technician",
            "assigned_technician__user",
        ),
        id=request_id,
    )

    # Technician can view:
    # 1. Pending jobs not yet assigned
    # 2. Jobs assigned to them
    if service_request.status != ServiceRequest.STATUS_PENDING and service_request.assigned_technician != technician_profile:
        messages.error(request, "You are not allowed to view this job.")
        return redirect("technician_dashboard")

    return render(request, "technician/request_detail.html", {
    "service_request": service_request,
    "technician_profile": technician_profile,
})

@staff_member_required
def admin_dashboard(request):
    total_requests = ServiceRequest.objects.count()
    pending_requests_count = ServiceRequest.objects.filter(
        status=ServiceRequest.STATUS_PENDING
    ).count()
    accepted_requests_count = ServiceRequest.objects.filter(
        status=ServiceRequest.STATUS_ACCEPTED
    ).count()
    in_progress_requests_count = ServiceRequest.objects.filter(
        status=ServiceRequest.STATUS_IN_PROGRESS
    ).count()
    completed_requests_count = ServiceRequest.objects.filter(
        status=ServiceRequest.STATUS_COMPLETED
    ).count()

    total_clients = User.objects.filter(role=User.ROLE_CLIENT).count()
    total_technicians = TechnicianProfile.objects.count()
    verified_technicians = TechnicianProfile.objects.filter(is_verified=True).count()
    unverified_technicians = TechnicianProfile.objects.filter(is_verified=False).count()

    latest_requests = ServiceRequest.objects.select_related(
        "category",
        "client",
        "assigned_technician",
        "assigned_technician__user",
    ).order_by("-created_at")[:10]

    latest_technicians = TechnicianProfile.objects.select_related(
        "user"
    ).order_by("-created_at")[:8]

    return render(request, "admin_dashboard/dashboard.html", {
        "total_requests": total_requests,
        "pending_requests_count": pending_requests_count,
        "accepted_requests_count": accepted_requests_count,
        "in_progress_requests_count": in_progress_requests_count,
        "completed_requests_count": completed_requests_count,
        "total_clients": total_clients,
        "total_technicians": total_technicians,
        "verified_technicians": verified_technicians,
        "unverified_technicians": unverified_technicians,
        "latest_requests": latest_requests,
        "latest_technicians": latest_technicians,
    })

@staff_member_required
def admin_assign_request(request, request_id):
    service_request = get_object_or_404(
        ServiceRequest.objects.select_related(
            "category",
            "client",
            "assigned_technician",
            "assigned_technician__user",
        ),
        id=request_id,
    )

    if request.method == "POST":
        form = AssignTechnicianForm(request.POST)

        if form.is_valid():
            technician = form.cleaned_data["technician"]

            service_request.assigned_technician = technician
            service_request.status = ServiceRequest.STATUS_ASSIGNED
            service_request.save()

            messages.success(request, "Technician assigned successfully.")
            return redirect("admin_dashboard")
    else:
        form = AssignTechnicianForm()

    return render(request, "admin_dashboard/assign_request.html", {
        "form": form,
        "service_request": service_request,
    })

@staff_member_required
def admin_request_detail(request, request_id):
    service_request = get_object_or_404(
        ServiceRequest.objects.select_related(
            "category",
            "client",
            "assigned_technician",
            "assigned_technician__user",
            "review",
        ),
        id=request_id,
    )

    status_form = UpdateRequestStatusForm(initial={
        "status": service_request.status
    })

    notes_form = UpdateAdminNotesForm(initial={
    "admin_notes": service_request.admin_notes
    })

    return render(request, "admin_dashboard/request_detail.html", {
        "service_request": service_request,
        "status_form": status_form,
        "notes_form": notes_form,

    })

@staff_member_required
def admin_update_request_status(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)

    if request.method == "POST":
        form = UpdateRequestStatusForm(request.POST)

        if form.is_valid():
            new_status = form.cleaned_data["status"]

            service_request.status = new_status

            if new_status == ServiceRequest.STATUS_COMPLETED and not service_request.completed_at:
                service_request.completed_at = timezone.now()

            if new_status != ServiceRequest.STATUS_COMPLETED:
                service_request.completed_at = None

            service_request.save()

            messages.success(request, "Request status updated successfully.")
            return redirect("admin_request_detail", request_id=service_request.id)

    messages.error(request, "Invalid status update.")
    return redirect("admin_request_detail", request_id=service_request.id)

@staff_member_required
def admin_update_request_notes(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)

    if request.method == "POST":
        form = UpdateAdminNotesForm(request.POST)

        if form.is_valid():
            service_request.admin_notes = form.cleaned_data["admin_notes"]
            service_request.save()

            messages.success(request, "Admin notes updated successfully.")
            return redirect("admin_request_detail", request_id=service_request.id)

    messages.error(request, "Invalid notes update.")
    return redirect("admin_request_detail", request_id=service_request.id)
