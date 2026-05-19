from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CLIENT = "client"
    ROLE_TECHNICIAN = "technician"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = [
        (ROLE_CLIENT, "Client"),
        (ROLE_TECHNICIAN, "Technician"),
        (ROLE_ADMIN, "Admin"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CLIENT
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True
    )

    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    district = models.CharField(
        max_length=100,
        blank=True
    )

    is_phone_verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def is_client(self):
        return self.role == self.ROLE_CLIENT

    def is_technician(self):
        return self.role == self.ROLE_TECHNICIAN

    def is_platform_admin(self):
        return self.role == self.ROLE_ADMIN

    def __str__(self):
        return f"{self.username} ({self.role})"