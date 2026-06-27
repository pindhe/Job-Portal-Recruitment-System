from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Invoice, Plan, Subscription


def pricing(request):
    plans = Plan.objects.filter(is_active=True)
    return render(request, "payments/pricing.html", {"plans": plans})


@login_required
def subscribe(request, slug):
    plan = get_object_or_404(Plan, slug=slug, is_active=True)
    if request.method == "POST":
        sub = Subscription.objects.create(
            user=request.user,
            plan=plan,
            status=Subscription.Status.ACTIVE,
            started_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=365 if plan.billing_cycle == "yearly" else 30),
        )
        Invoice.objects.create(
            user=request.user,
            subscription=sub,
            amount=plan.price,
            currency=plan.currency,
            gateway=request.POST.get("gateway", "manual"),
            status=Invoice.Status.PAID,
            paid_at=timezone.now(),
        )
        messages.success(request, f"You're now subscribed to {plan.name}!")
        return redirect("dashboard:billing")
    return render(request, "payments/checkout.html", {"plan": plan})
