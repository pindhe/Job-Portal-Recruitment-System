from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Notification
from .services import notify

User = get_user_model()


@login_required
def notification_list(request):
    notes = request.user.notifications.all()
    context = {"notifications": notes}
    if request.user.is_admin_side:
        from apps.accounts.models import Role

        context["roles"] = Role.choices
        context["all_users"] = User.objects.order_by("first_name", "email")
    return render(request, "notifications/list.html", context)


@login_required
@require_POST
def compose_notification(request):
    """Admin: send an in-app (and optionally email) notification to users."""
    if not request.user.is_admin_side:
        return redirect("notifications:list")

    title = request.POST.get("title", "").strip()
    body = request.POST.get("body", "").strip()
    audience = request.POST.get("audience", "all")
    url = request.POST.get("url", "").strip()
    if not title:
        messages.error(request, "Notification title is required.")
        return redirect("notifications:list")

    if audience == "role":
        recipients = User.objects.filter(role=request.POST.get("role"), is_active=True)
    elif audience == "user":
        recipients = User.objects.filter(pk=request.POST.get("user"))
    else:
        recipients = User.objects.filter(is_active=True)

    channels = ["in_app"]
    if request.POST.get("send_email"):
        channels.append("email")

    count = 0
    for user in recipients.iterator():
        notify(user, title=title, body=body, url=url, icon="megaphone", channels=tuple(channels))
        count += 1

    messages.success(request, f"Notification sent to {count} user(s).")
    return redirect("notifications:list")


@login_required
def mark_read(request, pk):
    note = get_object_or_404(Notification, pk=pk, recipient=request.user)
    note.is_read = True
    note.save(update_fields=["is_read"])
    return redirect(note.url or "notifications:list")


@login_required
@require_POST
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect("notifications:list")
