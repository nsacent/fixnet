from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum

from requests_app.forms import ServiceRequestForm, ClientPaymentProofForm, CancelRequestForm
from requests_app.models import ServiceRequest, RequestActivity

from reviews.forms import ReviewForm
from reviews.models import Review
from services.models import ServiceCategory

from technicians.models import TechnicianProfile
from technicians.forms import TechnicianProfileForm


"""Admins"""
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import User
from requests_app.admin_forms import (
    AssignTechnicianForm,
    UpdateRequestStatusForm,
    UpdateAdminNotesForm,
    UpdateFinalPriceForm,
    UpdatePaymentForm,
    UpdateTechnicianPayoutForm,

)

def log_request_activity(service_request, action, message, user=None):
    RequestActivity.objects.create(
        service_request=service_request,
        action=action,
        message=message,
        performed_by=user if user and user.is_authenticated else None,
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

            messages.success(request, "Your request has been submitted successfully.")
            return redirect("request_success")
        else:
            messages.error(request, "Please correct the errors in the form.")

    else:
        form = ServiceRequestForm()

    service_categories = ServiceCategory.objects.filter(
        is_active=True
    ).order_by("display_order", "name")[:8]

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
    total_technician_earnings = ServiceRequest.objects.filter(
    assigned_technician=technician_profile,
        status=ServiceRequest.STATUS_COMPLETED,
    ).aggregate(
        total=Sum("technician_earning")
    )["total"] or 0
    pending_requests = ServiceRequest.objects.filter(
        status=ServiceRequest.STATUS_PENDING
    ).select_related("category", "client")

    if technician_profile:
        assigned_requests = ServiceRequest.objects.filter(
            assigned_technician=technician_profile
        ).select_related("category", "client")

    paid_technician_earnings = ServiceRequest.objects.filter(
        assigned_technician=technician_profile,
        status=ServiceRequest.STATUS_COMPLETED,
        technician_payout_status=ServiceRequest.PAYOUT_PAID,
    ).aggregate(
        total=Sum("technician_earning")
    )["total"] or 0

    unpaid_technician_earnings = total_technician_earnings - paid_technician_earnings

    return render(request, "technician/dashboard.html", {
        "technician_profile": technician_profile,
        "assigned_requests": assigned_requests,
        "pending_requests": pending_requests,
        "total_technician_earnings": total_technician_earnings,
        "paid_technician_earnings": paid_technician_earnings,
        "unpaid_technician_earnings": unpaid_technician_earnings,
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

    can_client_cancel = service_request.status in [
        ServiceRequest.STATUS_PENDING,
        ServiceRequest.STATUS_ASSIGNED,
        ServiceRequest.STATUS_ACCEPTED,
    ]

    return render(request, "client/request_detail.html", {
        "service_request": service_request,
        "can_client_cancel": can_client_cancel,

    })    

@login_required
def edit_technician_profile(request):
    technician_profile = getattr(request.user, "technician_profile", None)

    if not technician_profile:
        messages.error(request, "You do not have a technician profile.")
        return redirect("technician_dashboard")

    if request.method == "POST":
        form = TechnicianProfileForm(
            request.POST,
            request.FILES,
            instance=technician_profile
        )
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

    pending_payment_proofs = ServiceRequest.objects.filter(
        payment_proof_status=ServiceRequest.PROOF_PENDING
    ).count()

    approved_payment_proofs = ServiceRequest.objects.filter(
        payment_proof_status=ServiceRequest.PROOF_APPROVED
    ).count()

    rejected_payment_proofs = ServiceRequest.objects.filter(
        payment_proof_status=ServiceRequest.PROOF_REJECTED
    ).count()

    not_submitted_payment_proofs = ServiceRequest.objects.filter(
        payment_proof_status=ServiceRequest.PROOF_NOT_SUBMITTED
    ).count()

    total_final_value = ServiceRequest.objects.aggregate(
        total=Sum("final_price")
    )["total"] or 0

    total_amount_paid = ServiceRequest.objects.aggregate(
        total=Sum("amount_paid")
    )["total"] or 0

    outstanding_balance = total_final_value - total_amount_paid

    paid_jobs_count = ServiceRequest.objects.filter(
        payment_status=ServiceRequest.PAYMENT_PAID
    ).count()

    latest_requests = ServiceRequest.objects.select_related(
        "category",
        "client",
        "assigned_technician",
        "assigned_technician__user",
    ).order_by("-created_at")[:10]

    latest_technicians = TechnicianProfile.objects.select_related(
        "user"
    ).order_by("-created_at")[:8]

    pending_proof_requests = ServiceRequest.objects.select_related(
    "category",
    "client",
    "assigned_technician",
    "assigned_technician__user",
    ).filter(
        payment_proof_status=ServiceRequest.PROOF_PENDING
    ).order_by("-updated_at")[:8]

    unpaid_payout_requests = ServiceRequest.objects.select_related(
        "category",
        "client",
        "assigned_technician",
        "assigned_technician__user",
    ).filter(
        status=ServiceRequest.STATUS_COMPLETED,
        technician_payout_status=ServiceRequest.PAYOUT_UNPAID,
        technician_earning__gt=0,
    ).order_by("-completed_at")[:10]

    total_technician_earnings = ServiceRequest.objects.aggregate(
        total=Sum("technician_earning")
    )["total"] or 0

    total_technician_paid_out = ServiceRequest.objects.filter(
        technician_payout_status=ServiceRequest.PAYOUT_PAID
    ).aggregate(
        total=Sum("technician_earning")
    )["total"] or 0

    total_technician_unpaid = total_technician_earnings - total_technician_paid_out

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
        "pending_payment_proofs": pending_payment_proofs,
        "approved_payment_proofs": approved_payment_proofs,
        "rejected_payment_proofs": rejected_payment_proofs,
        "not_submitted_payment_proofs": not_submitted_payment_proofs,
        "total_final_value": total_final_value,
        "total_amount_paid": total_amount_paid,
        "outstanding_balance": outstanding_balance,
        "paid_jobs_count": paid_jobs_count,
        "pending_proof_requests": pending_proof_requests,
        "unpaid_payout_requests": unpaid_payout_requests,
        "total_technician_earnings": total_technician_earnings,
        "total_technician_paid_out": total_technician_paid_out,
        "total_technician_unpaid": total_technician_unpaid,

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

            log_request_activity(
                service_request,
                RequestActivity.ACTION_ASSIGNED,
                f"Admin assigned technician {technician.user.username}.",
                request.user,
            )


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

    price_form = UpdateFinalPriceForm(initial={
        "final_price": service_request.final_price,
        "price_note": service_request.price_note,
        "platform_commission_percent": service_request.platform_commission_percent,

    })

    payout_form = UpdateTechnicianPayoutForm(initial={
        "technician_payout_status": service_request.technician_payout_status,
        "technician_payout_method": service_request.technician_payout_method,
        "technician_payout_note": service_request.technician_payout_note,
    })

    payment_form = UpdatePaymentForm(initial={
        "payment_status": service_request.payment_status,
        "payment_method": service_request.payment_method,
        "amount_paid": service_request.amount_paid,
        "payment_note": service_request.payment_note,
        "payment_proof_status": service_request.payment_proof_status,
    })

    activities = service_request.activities.select_related(
        "performed_by"
    ).order_by("-created_at")

    return render(request, "admin_dashboard/request_detail.html", {
        "service_request": service_request,
        "status_form": status_form,
        "notes_form": notes_form,
        "price_form": price_form,
        "payment_form": payment_form,
        "payout_form": payout_form,
        "activities": activities,
        "activities_count": activities.count(),
    })


@staff_member_required
def admin_update_request_status(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)

    if request.method == "POST":
        form = UpdateRequestStatusForm(request.POST)

        if form.is_valid():
            old_status = service_request.status
            new_status = form.cleaned_data["status"]

            service_request.status = new_status

            # If admin marks completed, set completed date
            if new_status == ServiceRequest.STATUS_COMPLETED and not service_request.completed_at:
                service_request.completed_at = timezone.now()

            # If admin moves away from completed, clear completed date
            if new_status != ServiceRequest.STATUS_COMPLETED:
                service_request.completed_at = None

            # If admin reopens a cancelled request, clear cancellation reason
            if old_status == ServiceRequest.STATUS_CANCELLED and new_status != ServiceRequest.STATUS_CANCELLED:
                service_request.cancellation_reason = ""

            service_request.save()

            log_request_activity(
                service_request,
                RequestActivity.ACTION_STATUS_UPDATED,
                f"Admin changed status from {old_status} to {new_status}.",
                request.user,
            )

            messages.success(request, "Request status updated successfully.")
            return redirect("admin_request_detail", request_id=service_request.id)

        messages.error(request, form.errors)

    messages.error(request, "Invalid status update.")
    return redirect("admin_request_detail", request_id=service_request.id)




@staff_member_required
def admin_update_final_price(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)

    if request.method == "POST":
        form = UpdateFinalPriceForm(request.POST)

        if form.is_valid():
            service_request.final_price = form.cleaned_data["final_price"]
            service_request.price_note = form.cleaned_data["price_note"]
            service_request.platform_commission_percent = form.cleaned_data["platform_commission_percent"]
            service_request.calculate_earnings()
            service_request.save()

            log_request_activity(
                service_request,
                RequestActivity.ACTION_PRICE_UPDATED,
                f"Admin updated final price to UGX {service_request.final_price}.",
                request.user,
            )

            messages.success(request, "Final price updated successfully.")
            return redirect("admin_request_detail", request_id=service_request.id)

    messages.error(request, "Invalid final price update.")
    return redirect("admin_request_detail", request_id=service_request.id)

@staff_member_required
def admin_update_request_notes(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)

    if request.method == "POST":
        form = UpdateAdminNotesForm(request.POST)

        if form.is_valid():
            service_request.admin_notes = form.cleaned_data["admin_notes"]
            service_request.save()

            log_request_activity(
                service_request,
                RequestActivity.ACTION_NOTES_UPDATED,
                "Admin internal notes were updated.",
                request.user,
            )

            messages.success(request, "Admin notes updated successfully.")
            return redirect("admin_request_detail", request_id=service_request.id)

    messages.error(request, "Invalid notes update.")
    return redirect("admin_request_detail", request_id=service_request.id)   

@staff_member_required
def admin_update_payment(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)

    if request.method == "POST":
        form = UpdatePaymentForm(request.POST, request.FILES)

        if form.is_valid():
            service_request.payment_status = form.cleaned_data["payment_status"]
            service_request.payment_method = form.cleaned_data["payment_method"]
            service_request.amount_paid = form.cleaned_data["amount_paid"]
            service_request.payment_note = form.cleaned_data["payment_note"]
            service_request.payment_proof_status = form.cleaned_data["payment_proof_status"]
            if form.cleaned_data.get("payment_proof"):
                service_request.payment_proof = form.cleaned_data["payment_proof"]
            service_request.save()

            log_request_activity(
                service_request,
                RequestActivity.ACTION_PAYMENT_UPDATED,
                "Admin updated payment details.",
                request.user,
            )

            messages.success(request, "Payment details updated successfully.")
            return redirect("admin_request_detail", request_id=service_request.id)

    messages.error(request, "Invalid payment update.")
    return redirect("admin_request_detail", request_id=service_request.id)

@login_required
def client_upload_payment_proof(request, request_id):
    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
        client=request.user,
    )

    if request.method == "POST":
        form = ClientPaymentProofForm(request.POST, request.FILES)

        if form.is_valid():
            service_request.payment_proof = form.cleaned_data["payment_proof"]
            service_request.payment_proof_status = ServiceRequest.PROOF_PENDING
            service_request.save()

            log_request_activity(
                service_request,
                RequestActivity.ACTION_PROOF_UPLOADED,
                "Client uploaded payment proof.",
                request.user,
            )

            messages.success(
                request,
                "Payment proof uploaded successfully. FixNet admin will review it."
            )
            return redirect("client_request_detail", request_id=service_request.id)
    else:
        form = ClientPaymentProofForm()

    return render(request, "client/upload_payment_proof.html", {
        "form": form,
        "service_request": service_request,
    })


@login_required
def client_cancel_request(request, request_id):
    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
        client=request.user,
    )

    if service_request.status in [
        ServiceRequest.STATUS_IN_PROGRESS,
        ServiceRequest.STATUS_COMPLETED,
        ServiceRequest.STATUS_CANCELLED,
    ]:
        messages.error(request, "This request cannot be cancelled at this stage.")
        return redirect("client_request_detail", request_id=service_request.id)

    if request.method == "POST":
        form = CancelRequestForm(request.POST)

        if form.is_valid():
            service_request.cancellation_reason = form.cleaned_data["cancellation_reason"]
            service_request.status = ServiceRequest.STATUS_CANCELLED
            service_request.save()

            messages.success(request, "Request cancelled successfully.")
            return redirect("client_dashboard")
    else:
        form = CancelRequestForm()

    return render(request, "client/cancel_request.html", {
        "form": form,
        "service_request": service_request,
    })


@staff_member_required
def admin_cancel_request(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)

    if service_request.status == ServiceRequest.STATUS_COMPLETED:
        messages.error(request, "Completed requests should not be cancelled.")
        return redirect("admin_request_detail", request_id=service_request.id)

    service_request.status = ServiceRequest.STATUS_CANCELLED
    service_request.save()

    messages.success(request, "Request cancelled successfully.")
    return redirect("admin_request_detail", request_id=service_request.id)


@login_required
def technician_profile_detail(request, technician_id):
    technician_profile = get_object_or_404(
        TechnicianProfile.objects.select_related("user"),
        id=technician_id,
    )

    completed_jobs = ServiceRequest.objects.filter(
        assigned_technician=technician_profile,
        status=ServiceRequest.STATUS_COMPLETED,
    ).select_related(
        "category",
        "client",
    ).order_by("-completed_at")[:10]

    return render(request, "technician/profile_detail.html", {
        "technician_profile": technician_profile,
        "completed_jobs": completed_jobs,
    })

@staff_member_required
def admin_update_technician_payout(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)

    if request.method == "POST":
        form = UpdateTechnicianPayoutForm(request.POST)

        if form.is_valid():
            service_request.technician_payout_status = form.cleaned_data["technician_payout_status"]
            service_request.technician_payout_method = form.cleaned_data["technician_payout_method"]
            service_request.technician_payout_note = form.cleaned_data["technician_payout_note"]

            if service_request.technician_payout_status == ServiceRequest.PAYOUT_PAID:
                if not service_request.technician_payout_date:
                    service_request.technician_payout_date = timezone.now()
            else:
                service_request.technician_payout_date = None

            service_request.save()

            log_request_activity(
                service_request,
                RequestActivity.ACTION_PAYMENT_UPDATED,
                "Admin updated technician payout details.",
                request.user,
            )

            messages.success(request, "Technician payout updated successfully.")
            return redirect("admin_request_detail", request_id=service_request.id)

        messages.error(request, form.errors)

    messages.error(request, "Invalid technician payout update.")
    return redirect("admin_request_detail", request_id=service_request.id)




