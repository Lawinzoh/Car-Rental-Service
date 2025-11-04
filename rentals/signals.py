from .models import Rental
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Rental)
def send_rental_notifications(sender, instance, created, **kwargs):
    if created:
        # a new rental has been created(confirmed payment)
        print(f"TASK: Sending Booking Confirmation to User {instance.user.email}") #replaece with actual email sending logic
    elif instance.status == 'comleted':
        #rental status changed to completed(vehicle returned)
        print(f'TASK: Sending Receipt to User {instance.user.email} for Rental {instance.id}') #replaece with actual email sending logic
    elif instance.status == 'cancelled':
        #rental cancelled(refund if paid)
        print(f'TASK: Sending Cancellation/Refund Notice to User {instance.user.email} for Rental {instance.id}') #replaece with actual email sending logic
        