from django.contrib import admin
from .models import ServiceRequest


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
        "created_at",
    )

    list_filter = (
        "status",
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