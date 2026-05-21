from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import ServiceRequest, RequestActivity


@receiver(pre_save, sender=ServiceRequest)
def remember_old_request_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_status = None
        return

    try:
        old_instance = ServiceRequest.objects.get(pk=instance.pk)
        instance._old_status = old_instance.status
    except ServiceRequest.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=ServiceRequest)
def create_request_activity(sender, instance, created, **kwargs):
    if created:
        RequestActivity.objects.create(
            service_request=instance,
            action=RequestActivity.ACTION_CREATED,
            message="Request was submitted.",
        )
        return

    old_status = getattr(instance, "_old_status", None)

    if old_status and old_status != instance.status:
        status_action_map = {
            ServiceRequest.STATUS_ASSIGNED: RequestActivity.ACTION_ASSIGNED,
            ServiceRequest.STATUS_ACCEPTED: RequestActivity.ACTION_ACCEPTED,
            ServiceRequest.STATUS_IN_PROGRESS: RequestActivity.ACTION_STARTED,
            ServiceRequest.STATUS_COMPLETED: RequestActivity.ACTION_COMPLETED,
        }

        action = status_action_map.get(
            instance.status,
            RequestActivity.ACTION_STATUS_UPDATED
        )

        RequestActivity.objects.create(
            service_request=instance,
            action=action,
            message=f"Request status changed from {old_status} to {instance.status}.",
        )