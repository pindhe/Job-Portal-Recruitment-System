from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import (
    EmailLoginForm,
    ForgotPasswordForm,
    ProfileForm,
    RegisterForm,
    ResetPasswordForm,
)
from .models import LoginHistory, OTPCode

User = get_user_model()


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        otp = OTPCode.issue(user, OTPCode.Purpose.EMAIL)
        send_mail(
            subject=f"Verify your {settings.SITE_NAME} account",
            message=f"Your verification code is {otp.code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        login(request, user)
        messages.success(request, "Welcome aboard! We sent a verification code to your email.")
        return redirect("dashboard:home")
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    form = EmailLoginForm(request, data=request.POST or None)
    if request.method == "POST":
        email = request.POST.get("username", "").lower()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if not request.POST.get("remember_me"):
                request.session.set_expiry(0)
            LoginHistory.objects.create(
                user=user,
                ip_address=_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
                successful=True,
            )
            messages.success(request, f"Welcome back, {user.full_name}!")
            return redirect(request.GET.get("next") or "dashboard:home")
        existing = User.objects.filter(email=email).first()
        if existing:
            LoginHistory.objects.create(
                user=existing,
                ip_address=_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
                successful=False,
            )
        messages.error(request, "Invalid email or password.")
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect("public:home")


def forgot_password_view(request):
    form = ForgotPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = User.objects.filter(email=form.cleaned_data["email"].lower()).first()
        if user:
            otp = OTPCode.issue(user, OTPCode.Purpose.PASSWORD_RESET)
            send_mail(
                subject=f"{settings.SITE_NAME} password reset",
                message=f"Your password reset code is {otp.code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            request.session["reset_email"] = user.email
        messages.success(request, "If that email exists, a reset code has been sent.")
        return redirect("accounts:reset_password")
    return render(request, "accounts/forgot_password.html", {"form": form})


def reset_password_view(request):
    form = ResetPasswordForm(request.POST or None)
    email = request.session.get("reset_email")
    if request.method == "POST" and form.is_valid() and email:
        user = User.objects.filter(email=email).first()
        otp = (
            OTPCode.objects.filter(user=user, purpose=OTPCode.Purpose.PASSWORD_RESET, code=form.cleaned_data["code"])
            .order_by("-created_at")
            .first()
        )
        if user and otp and otp.is_valid:
            user.set_password(form.cleaned_data["password1"])
            user.save()
            otp.is_used = True
            otp.save(update_fields=["is_used"])
            request.session.pop("reset_email", None)
            messages.success(request, "Password updated. You can sign in now.")
            return redirect("accounts:login")
        messages.error(request, "Invalid or expired code.")
    return render(request, "accounts/reset_password.html", {"form": form})


@login_required
def verify_email_view(request):
    if request.method == "POST":
        code = request.POST.get("code", "")
        otp = (
            OTPCode.objects.filter(user=request.user, purpose=OTPCode.Purpose.EMAIL, code=code)
            .order_by("-created_at")
            .first()
        )
        if otp and otp.is_valid:
            request.user.email_verified = True
            request.user.save(update_fields=["email_verified"])
            otp.is_used = True
            otp.save(update_fields=["is_used"])
            messages.success(request, "Email verified successfully.")
            return redirect("dashboard:home")
        messages.error(request, "Invalid or expired code.")
    return render(request, "accounts/verify_email.html")


@login_required
def profile_settings_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("accounts:settings")
    history = request.user.login_history.all()[:10]
    devices = request.user.devices.all()
    return render(
        request,
        "accounts/settings.html",
        {"form": form, "history": history, "devices": devices},
    )
