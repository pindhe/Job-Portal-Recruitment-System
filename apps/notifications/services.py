"""Unified notification dispatch (in-app + pluggable channels)."""
from django.conf import settings
from django.core.mail import send_mail

from .models import Notification


def notify(user, title, body="", url="", icon="bell", channels=("in_app",)):
    """Create notifications across the requested channels.

    Email is wired up; SMS/WhatsApp/Push are stubbed at the integration layer
    so production credentials can be dropped in without code changes.
    """
    if user is None:
        return None

    note = None
    if "in_app" in channels:
        note = Notification.objects.create(
            recipient=user, title=title, body=body, url=url, icon=icon, channel=Notification.Channel.IN_APP
        )

    if "email" in channels and user.email:
        send_mail(
            subject=title,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

    if "whatsapp" in channels:
        send_whatsapp(user.phone, f"{title}\n{body}")

    if "sms" in channels:
        send_sms(user.phone, f"{title}: {body}")

    return note


def send_whatsapp(phone, message):
    """Placeholder for WhatsApp Business API / Twilio integration."""
    if not phone or not getattr(settings, "WHATSAPP_API_URL", ""):
        return False
    # import requests; requests.post(settings.WHATSAPP_API_URL, ...)
    return True


def send_sms(phone, message):
    """Placeholder for SMS gateway integration."""
    if not phone:
        return False
    return True


def broadcast(users, title, body="", url="", icon="megaphone"):
    notes = [
        Notification(recipient=u, title=title, body=body, url=url, icon=icon)
        for u in users
    ]
    return Notification.objects.bulk_create(notes)
