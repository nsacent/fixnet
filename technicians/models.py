from django.conf import settings
from django.db import models


class TechnicianProfile(models.Model):

    EXPERIENCE_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("expert", "Expert"),
    ]

    AVAILABILITY_AVAILABLE = "available"
    AVAILABILITY_BUSY = "busy"
    AVAILABILITY_OFFLINE = "offline"

    AVAILABILITY_CHOICES = [
        (AVAILABILITY_AVAILABLE, "Available"),
        (AVAILABILITY_BUSY, "Busy"),
        (AVAILABILITY_OFFLINE, "Offline"),
    ]

    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default=AVAILABILITY_AVAILABLE,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="technician_profile"
    )

    business_name = models.CharField(
        max_length=150,
        blank=True
    )

    bio = models.TextField(blank=True)

    skills = models.TextField(
        help_text="Example: WiFi, Router Setup, CCTV, LAN Cabling"
    )

    service_area = models.CharField(
        max_length=150
    )

    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES
    )

    is_verified = models.BooleanField(
        default=False
    )

    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0
    )

    completed_jobs = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    profile_photo = models.ImageField(
        upload_to="technician_profiles/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username