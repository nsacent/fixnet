from django.contrib import admin
from .models import ServiceRequest, RequestActivity

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "client",
        "client_name",
        "category",
        "assigned_technician",
        "priority",
        "status",
        "location",
        "final_price",
        "amount_paid",
        "payment_status",
        "created_at",
    )

    list_filter = (
    "status",
    "payment_status",
    "payment_method",
    "priority",
    "category",
    "created_at",
    )

    search_fields = (
    "title",
    "description",
    "admin_notes",
    "client__username",
    "client_name",
    "location",
    "phone_number",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

@admin.register(RequestActivity)
class RequestActivityAdmin(admin.ModelAdmin):
    list_display = (
        "service_request",
        "action",
        "performed_by",
        "created_at",
    )

    list_filter = (
        "action",
        "created_at",
    )

    search_fields = (
        "service_request__title",
        "message",
        "performed_by__username",
    )

    readonly_fields = (
        "service_request",
        "action",
        "message",
        "performed_by",
        "created_at",
    )