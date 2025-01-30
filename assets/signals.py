from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Asset, PriceTunnel, Frequency

@receiver(post_save, sender=Asset)
def create_related_objects(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            # Create PriceTunnel if it doesn't exist
            PriceTunnel.objects.get_or_create(
                asset=instance,
                defaults={
                    'lower_limit': 0.00,
                    'upper_limit': 0.00
                }
            )

            # Create Frequency if it doesn't exist
            Frequency.objects.get_or_create(
                asset=instance,
                defaults={
                    'interval_minutes': 5
                }
            )