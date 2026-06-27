"""Employer organisations: companies, branches, departments, recruiter links."""
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel, TimeStampedModel


class Company(BaseModel):
    class OrgType(models.TextChoices):
        COMPANY = "company", _("Company")
        RECRUITER = "recruiter", _("Recruitment Agency")
        UNIVERSITY = "university", _("University")
        NGO = "ngo", _("NGO")
        GOVERNMENT = "government", _("Government")

    class Size(models.TextChoices):
        MICRO = "1-10", "1-10"
        SMALL = "11-50", "11-50"
        MEDIUM = "51-200", "51-200"
        LARGE = "201-1000", "201-1000"
        ENTERPRISE = "1000+", "1000+"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_companies")
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    org_type = models.CharField(max_length=20, choices=OrgType.choices, default=OrgType.COMPANY)
    tagline = models.CharField(max_length=200, blank=True)
    about = models.TextField(blank=True)
    industry = models.CharField(max_length=120, blank=True)
    size = models.CharField(max_length=20, choices=Size.choices, default=Size.SMALL)
    founded_year = models.PositiveIntegerField(null=True, blank=True)

    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=160, blank=True)

    logo = models.ImageField(upload_to="company/logos/", blank=True, null=True)
    cover = models.ImageField(upload_to="company/covers/", blank=True, null=True)

    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Companies"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug, i = base, 1
            while Company.all_objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def open_jobs_count(self):
        return self.jobs.filter(status="published").count()


class Branch(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="branches")
    name = models.CharField(max_length=120)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)
    is_headquarters = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class Department(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class CompanyMember(TimeStampedModel):
    """Links recruiters / HR managers to a company with a role."""

    class MemberRole(models.TextChoices):
        OWNER = "owner", _("Owner")
        HR_MANAGER = "hr_manager", _("HR Manager")
        RECRUITER = "recruiter", _("Recruiter")

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="company_memberships")
    member_role = models.CharField(max_length=20, choices=MemberRole.choices, default=MemberRole.RECRUITER)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ("company", "user")

    def __str__(self):
        return f"{self.user} @ {self.company} ({self.member_role})"
