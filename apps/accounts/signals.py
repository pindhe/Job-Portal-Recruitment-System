"""Create role-specific profiles automatically when a user is created."""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Role


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_role_profile(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.role == Role.CANDIDATE:
        from apps.candidates.models import CandidateProfile

        CandidateProfile.objects.get_or_create(user=instance)
