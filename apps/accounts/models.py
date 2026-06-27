"""User model with RBAC roles, profiles, devices, and login history."""
import secrets
from datetime import timedelta

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class Role(models.TextChoices):
    SUPER_ADMIN = "super_admin", _("Super Admin")
    ADMIN = "admin", _("Admin")
    EMPLOYER = "employer", _("Employer")
    RECRUITER = "recruiter", _("Recruiter")
    HR_MANAGER = "hr_manager", _("HR Manager")
    CANDIDATE = "candidate", _("Candidate")
    SUPPORT_AGENT = "support_agent", _("Support Agent")
    ACCOUNTANT = "accountant", _("Accountant")
    MODERATOR = "moderator", _("Moderator")
    GUEST = "guest", _("Guest")


EMPLOYER_SIDE_ROLES = {Role.EMPLOYER, Role.RECRUITER, Role.HR_MANAGER}
STAFF_ROLES = {Role.SUPER_ADMIN, Role.ADMIN, Role.SUPPORT_AGENT, Role.ACCOUNTANT, Role.MODERATOR}


class UserManager(BaseUserManager):
    """Email-based user manager (email is the unique identifier)."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", Role.CANDIDATE)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Role.SUPER_ADMIN)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("email_verified", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user: email login, role-based access, verification flags."""

    username = None
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CANDIDATE, db_index=True)

    phone = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)

    # Social auth references (provider ids, no secrets stored)
    google_id = models.CharField(max_length=120, blank=True)
    linkedin_id = models.CharField(max_length=120, blank=True)
    github_id = models.CharField(max_length=120, blank=True)
    facebook_id = models.CharField(max_length=120, blank=True)

    locale = models.CharField(max_length=10, default="en")
    dark_mode = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ["-date_joined"]
        indexes = [models.Index(fields=["role", "is_active"])]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email.split("@")[0]

    @property
    def initials(self):
        parts = [p for p in [self.first_name, self.last_name] if p]
        if parts:
            return "".join(p[0].upper() for p in parts)[:2]
        return self.email[:2].upper()

    @property
    def is_employer_side(self):
        return self.role in {r.value for r in EMPLOYER_SIDE_ROLES}

    @property
    def is_admin_side(self):
        return self.is_superuser or self.role in {r.value for r in STAFF_ROLES}

    @property
    def dashboard_url_name(self):
        mapping = {
            Role.CANDIDATE: "dashboard:candidate",
            Role.EMPLOYER: "dashboard:employer",
            Role.HR_MANAGER: "dashboard:employer",
            Role.RECRUITER: "dashboard:recruiter",
        }
        if self.is_admin_side:
            return "dashboard:admin"
        return mapping.get(self.role, "dashboard:candidate")


class OTPCode(TimeStampedModel):
    """One-time codes for email / phone verification and 2FA."""

    class Purpose(models.TextChoices):
        EMAIL = "email", _("Email Verification")
        PHONE = "phone", _("Phone Verification")
        TWO_FACTOR = "2fa", _("Two Factor")
        PASSWORD_RESET = "reset", _("Password Reset")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otp_codes")
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=10, choices=Purpose.choices)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def issue(cls, user, purpose, ttl_minutes=10):
        code = f"{secrets.randbelow(1000000):06d}"
        return cls.objects.create(
            user=user,
            code=code,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=ttl_minutes),
        )

    @property
    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.user} {self.purpose} {self.code}"


class Device(TimeStampedModel):
    """Registered devices for push notifications + device management."""

    class Platform(models.TextChoices):
        WEB = "web", "Web"
        ANDROID = "android", "Android"
        IOS = "ios", "iOS"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    name = models.CharField(max_length=120, blank=True)
    platform = models.CharField(max_length=10, choices=Platform.choices, default=Platform.WEB)
    push_token = models.CharField(max_length=255, blank=True)
    last_active = models.DateTimeField(auto_now=True)
    is_trusted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-last_active"]

    def __str__(self):
        return f"{self.user} - {self.name or self.platform}"


class LoginHistory(TimeStampedModel):
    """Audit each authentication attempt for security review."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_history")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    successful = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Login history"

    def __str__(self):
        status = "ok" if self.successful else "failed"
        return f"{self.user} {status} @ {self.created_at:%Y-%m-%d %H:%M}"
