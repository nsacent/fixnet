from django.conf import settings
from django.db import models
from services.models import ServiceCategory
from technicians.models import TechnicianProfile


class ServiceRequest(models.Model):

    STATUS_PENDING = "pending"
    STATUS_ASSIGNED = "assigned"
    STATUS_ACCEPTED = "accepted"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ASSIGNED, "Assigned"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    PRIORITY_NORMAL = "normal"
    PRIORITY_URGENT = "urgent"
    PRIORITY_EMERGENCY = "emergency"

    PRIORITY_CHOICES = [
        (PRIORITY_NORMAL, "Normal"),
        (PRIORITY_URGENT, "Urgent"),
        (PRIORITY_EMERGENCY, "Emergency"),
    ]

    client = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="service_requests"
    )

    client_name = models.CharField(
    max_length=150,
    blank=True
    )

    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests"
    )

    assigned_technician = models.ForeignKey(
        TechnicianProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_requests"
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    admin_notes = models.TextField(
    blank=True,
    help_text="Internal notes visible only to FixNet admin."
    )

    location = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)

    image = models.ImageField(
        upload_to="request_images/",
        blank=True,
        null=True
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_NORMAL
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    estimated_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    price_note = models.TextField(
    blank=True,
    help_text="Reason for final price change or pricing explanation."
)

    final_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.client}"