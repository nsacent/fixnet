from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg

from .models import Review


def update_technician_rating(technician):
    stats = technician.reviews_received.aggregate(
        average=Avg("rating")
    )

    technician.average_rating = stats["average"] or 0
    technician.completed_jobs = technician.reviews_received.count()
    technician.save()


@receiver(post_save, sender=Review)
def review_saved(sender, instance, **kwargs):
    update_technician_rating(instance.technician)


@receiver(post_delete, sender=Review)
def review_deleted(sender, instance, **kwargs):
    update_technician_rating(instance.technician)