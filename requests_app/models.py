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

    cancellation_reason = models.TextField(
        blank=True,
        help_text="Reason why this request was cancelled."
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

    platform_commission_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20,
        help_text="Platform commission percentage."
    )

    platform_commission_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    technician_earning = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    PAYOUT_UNPAID = "unpaid"
    PAYOUT_PAID = "paid"

    PAYOUT_STATUS_CHOICES = [
        (PAYOUT_UNPAID, "Unpaid"),
        (PAYOUT_PAID, "Paid"),
    ]

    PAYOUT_CASH = "cash"
    PAYOUT_MOBILE_MONEY = "mobile_money"
    PAYOUT_BANK = "bank"
    PAYOUT_OTHER = "other"

    PAYOUT_METHOD_CHOICES = [
        (PAYOUT_CASH, "Cash"),
        (PAYOUT_MOBILE_MONEY, "Mobile Money"),
        (PAYOUT_BANK, "Bank Transfer"),
        (PAYOUT_OTHER, "Other"),
    ]

    technician_payout_status = models.CharField(
        max_length=20,
        choices=PAYOUT_STATUS_CHOICES,
        default=PAYOUT_UNPAID,
    )

    technician_payout_method = models.CharField(
        max_length=30,
        choices=PAYOUT_METHOD_CHOICES,
        blank=True,
    )

    technician_payout_note = models.TextField(
        blank=True,
        help_text="Internal payout note or transaction reference."
    )

    technician_payout_date = models.DateTimeField(
        blank=True,
        null=True,
    )

    PAYMENT_UNPAID = "unpaid"
    PAYMENT_PARTIAL = "partial"
    PAYMENT_PAID = "paid"

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_UNPAID, "Unpaid"),
        (PAYMENT_PARTIAL, "Partially Paid"),
        (PAYMENT_PAID, "Paid"),
    ]

    PAYMENT_CASH = "cash"
    PAYMENT_MOBILE_MONEY = "mobile_money"
    PAYMENT_BANK = "bank"
    PAYMENT_OTHER = "other"

    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_CASH, "Cash"),
        (PAYMENT_MOBILE_MONEY, "Mobile Money"),
        (PAYMENT_BANK, "Bank Transfer"),
        (PAYMENT_OTHER, "Other"),
    ]

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_UNPAID,
    )

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    payment_note = models.TextField(
        blank=True,
        help_text="Internal payment note or transaction reference."
    )

    payment_proof = models.ImageField(
        upload_to="payment_proofs/",
        blank=True,
        null=True,
        help_text="Screenshot or receipt proof of payment."
    )


    PROOF_NOT_SUBMITTED = "not_submitted"
    PROOF_PENDING = "pending"
    PROOF_APPROVED = "approved"
    PROOF_REJECTED = "rejected"

    PAYMENT_PROOF_STATUS_CHOICES = [
        (PROOF_NOT_SUBMITTED, "Not Submitted"),
        (PROOF_PENDING, "Pending Review"),
        (PROOF_APPROVED, "Approved"),
        (PROOF_REJECTED, "Rejected"),
    ]

    payment_proof_status = models.CharField(
        max_length=30,
        choices=PAYMENT_PROOF_STATUS_CHOICES,
        default=PROOF_NOT_SUBMITTED,
    )

    def calculate_earnings(self):
        final_price = self.final_price or 0
        commission_percent = self.platform_commission_percent or 0

        self.platform_commission_amount = (final_price * commission_percent) / 100
        self.technician_earning = final_price - self.platform_commission_amount

    @property
    def balance_due(self):
        return max(self.final_price - self.amount_paid, 0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.client}"
    

class RequestActivity(models.Model):
    ACTION_CREATED = "created"
    ACTION_ASSIGNED = "assigned"
    ACTION_ACCEPTED = "accepted"
    ACTION_STARTED = "started"
    ACTION_COMPLETED = "completed"
    ACTION_STATUS_UPDATED = "status_updated"
    ACTION_PAYMENT_UPDATED = "payment_updated"
    ACTION_PROOF_UPLOADED = "proof_uploaded"
    ACTION_NOTES_UPDATED = "notes_updated"
    ACTION_PRICE_UPDATED = "price_updated"

    ACTION_CHOICES = [
        (ACTION_CREATED, "Created"),
        (ACTION_ASSIGNED, "Assigned"),
        (ACTION_ACCEPTED, "Accepted"),
        (ACTION_STARTED, "Started"),
        (ACTION_COMPLETED, "Completed"),
        (ACTION_STATUS_UPDATED, "Status Updated"),
        (ACTION_PAYMENT_UPDATED, "Payment Updated"),
        (ACTION_PROOF_UPLOADED, "Proof Uploaded"),
        (ACTION_NOTES_UPDATED, "Notes Updated"),
        (ACTION_PRICE_UPDATED, "Price Updated"),
    ]

    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="activities"
    )

    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )

    message = models.TextField()

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Request activities"

    def __str__(self):
        return f"{self.service_request.title} - {self.get_action_display()}"