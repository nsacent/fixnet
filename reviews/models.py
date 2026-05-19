from django.conf import settings
from django.db import models
from technicians.models import TechnicianProfile
from requests_app.models import ServiceRequest


class Review(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_given"
    )

    technician = models.ForeignKey(
        TechnicianProfile,
        on_delete=models.CASCADE,
        related_name="reviews_received"
    )

    request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="review"
    )

    rating = models.PositiveIntegerField(
        help_text="Rating from 1 to 5"
    )

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.client} → {self.technician} ({self.rating})"