from django.db import models


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Example: wifi, router, camera, cable"
    )

    starting_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Estimated starting price in UGX"
    )

    estimated_response_time = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: Within 30 minutes, Same day, 24 hours"
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Service categories"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name