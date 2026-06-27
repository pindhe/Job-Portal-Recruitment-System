"""Job postings, categories, applications and saved jobs."""
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from apps.core.models import BaseModel, TimeStampedModel


class JobCategory(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    icon = models.CharField(max_length=60, blank=True, help_text="Lucide icon name")
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Job categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class JobType(models.TextChoices):
    FULL_TIME = "full_time", _("Full Time")
    PART_TIME = "part_time", _("Part Time")
    REMOTE = "remote", _("Remote")
    HYBRID = "hybrid", _("Hybrid")
    CONTRACT = "contract", _("Contract")
    INTERNSHIP = "internship", _("Internship")
    TEMPORARY = "temporary", _("Temporary")
    FREELANCE = "freelance", _("Freelance")
    VOLUNTEER = "volunteer", _("Volunteer")


class WorkMode(models.TextChoices):
    ONSITE = "onsite", _("On-site")
    REMOTE = "remote", _("Remote")
    HYBRID = "hybrid", _("Hybrid")


class Job(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PENDING = "pending", _("Pending Approval")
        PUBLISHED = "published", _("Published")
        CLOSED = "closed", _("Closed")
        REJECTED = "rejected", _("Rejected")

    class ExperienceLevel(models.TextChoices):
        ENTRY = "entry", _("Entry Level")
        JUNIOR = "junior", _("Junior")
        MID = "mid", _("Mid Level")
        SENIOR = "senior", _("Senior")
        LEAD = "lead", _("Lead / Manager")
        EXECUTIVE = "executive", _("Executive")

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="posted_jobs")
    assigned_recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_jobs",
    )
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name="jobs")

    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    work_mode = models.CharField(max_length=20, choices=WorkMode.choices, default=WorkMode.ONSITE)
    experience_level = models.CharField(max_length=20, choices=ExperienceLevel.choices, default=ExperienceLevel.MID)

    description = models.TextField()
    responsibilities = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    qualifications = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    skills = models.CharField(max_length=400, blank=True, help_text="Comma separated skill tags")

    location = models.CharField(max_length=160, blank=True)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=10, default="USD")
    salary_period = models.CharField(max_length=20, default="month")

    education_required = models.CharField(max_length=120, blank=True)
    min_experience_years = models.PositiveIntegerField(default=0)
    vacancies = models.PositiveIntegerField(default=1)
    gender = models.CharField(max_length=20, blank=True)
    min_age = models.PositiveIntegerField(null=True, blank=True)
    max_age = models.PositiveIntegerField(null=True, blank=True)

    deadline = models.DateField(null=True, blank=True)
    attachment = models.FileField(upload_to="jobs/attachments/", blank=True, null=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PUBLISHED, db_index=True)
    is_featured = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-is_featured", "-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "job_type"]),
            models.Index(fields=["is_featured", "is_urgent"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:180]
            slug, i = base, 1
            while Job.all_objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("jobs:detail", kwargs={"slug": self.slug})

    @property
    def skill_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    @property
    def is_expired(self):
        return bool(self.deadline and self.deadline < timezone.now().date())

    @property
    def salary_display(self):
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,.0f} - {self.salary_max:,.0f}/{self.salary_period}"
        if self.salary_min:
            return f"{self.salary_currency} {self.salary_min:,.0f}+/{self.salary_period}"
        return "Negotiable"

    @property
    def applications_count(self):
        return self.applications.count()


class JobApplication(BaseModel):
    class Status(models.TextChoices):
        APPLIED = "applied", _("Applied")
        REVIEWING = "reviewing", _("Under Review")
        SHORTLISTED = "shortlisted", _("Shortlisted")
        INTERVIEW = "interview", _("Interview")
        OFFER = "offer", _("Offer")
        HIRED = "hired", _("Hired")
        REJECTED = "rejected", _("Rejected")
        WITHDRAWN = "withdrawn", _("Withdrawn")

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    cover_letter = models.TextField(blank=True)
    resume_file = models.FileField(upload_to="applications/resumes/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLIED, db_index=True)

    ai_match_score = models.PositiveIntegerField(default=0, help_text="0-100 AI candidate match score")
    rating = models.PositiveIntegerField(default=0, help_text="Recruiter rating 0-5")
    recruiter_notes = models.TextField(blank=True)
    is_shortlisted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("job", "candidate")

    def __str__(self):
        return f"{self.candidate} -> {self.job}"


class ApplicationEvent(TimeStampedModel):
    """Timeline entries for an application (status changes, notes)."""

    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name="events")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    label = models.CharField(max_length=160)
    detail = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.label


class SavedJob(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_jobs")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="saved_by")

    class Meta:
        unique_together = ("user", "job")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} saved {self.job}"
