import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel, TimeStampedModel


class Plan(TimeStampedModel):
    class Billing(models.TextChoices):
        MONTHLY = "monthly", _("Monthly")
        YEARLY = "yearly", _("Yearly")

    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default="USD")
    billing_cycle = models.CharField(max_length=10, choices=Billing.choices, default=Billing.MONTHLY)
    job_post_limit = models.PositiveIntegerField(default=5)
    featured_job_limit = models.PositiveIntegerField(default=0)
    resume_views_limit = models.PositiveIntegerField(default=50)
    has_ai_tools = models.BooleanField(default=False)
    has_analytics = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True)
    features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "price"]

    def __str__(self):
        return self.name


class Subscription(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        EXPIRED = "expired", _("Expired")
        CANCELLED = "cancelled", _("Cancelled")
        PENDING = "pending", _("Pending")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=False)
    jobs_posted = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE and (not self.expires_at or self.expires_at > timezone.now())

    def __str__(self):
        return f"{self.user} - {self.plan} ({self.status})"


class Invoice(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PAID = "paid", _("Paid")
        FAILED = "failed", _("Failed")
        REFUNDED = "refunded", _("Refunded")

    class Gateway(models.TextChoices):
        STRIPE = "stripe", "Stripe"
        PAYPAL = "paypal", "PayPal"
        ZAAD = "zaad", "Zaad"
        EVC = "evc", "EVC Plus"
        SAHAL = "sahal", "Sahal"
        PREMIER = "premier", "Premier Wallet"
        MANUAL = "manual", "Manual"

    number = models.CharField(max_length=30, unique=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invoices")
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default="USD")
    gateway = models.CharField(max_length=20, choices=Gateway.choices, default=Gateway.MANUAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reference = models.CharField(max_length=120, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"INV-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    @property
    def total(self):
        return (self.amount or Decimal("0")) + (self.tax or Decimal("0")) - (self.discount or Decimal("0"))

    def __str__(self):
        return self.number


class Coupon(TimeStampedModel):
    code = models.CharField(max_length=40, unique=True)
    percent_off = models.PositiveIntegerField(default=0)
    amount_off = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valid_until = models.DateField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(default=0)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
