from django.contrib import admin
from .models import TechnicianProfile


@admin.register(TechnicianProfile)
class TechnicianProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "service_area",
        "experience_level",
        "is_verified",
        "average_rating",
        "completed_jobs"
    )

    list_filter = (
        "experience_level",
        "is_verified",
    )

    search_fields = (
        "user__username",
        "business_name",
        "skills",
        "service_area",
    )