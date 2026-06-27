"""Candidate profile and resume building blocks."""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel, TimeStampedModel


class CandidateProfile(BaseModel):
    class Availability(models.TextChoices):
        IMMEDIATE = "immediate", _("Immediately")
        TWO_WEEKS = "2_weeks", _("Within 2 weeks")
        MONTH = "1_month", _("Within a month")
        NOT_LOOKING = "not_looking", _("Not actively looking")

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidate_profile")
    headline = models.CharField(max_length=160, blank=True)
    summary = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)

    current_title = models.CharField(max_length=120, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    expected_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    availability = models.CharField(max_length=20, choices=Availability.choices, default=Availability.IMMEDIATE)
    open_to_remote = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)

    resume_file = models.FileField(upload_to="resumes/", blank=True, null=True)
    cover_letter = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.full_name} profile"

    @property
    def completion(self):
        """Percentage profile completeness, used in the dashboard ring."""
        checks = [
            bool(self.headline),
            bool(self.summary),
            bool(self.location),
            bool(self.current_title),
            self.skills.exists(),
            self.education.exists(),
            self.experience.exists(),
            bool(self.resume_file),
        ]
        return int(sum(checks) / len(checks) * 100)


class Skill(TimeStampedModel):
    profile = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=80)
    level = models.PositiveIntegerField(default=70, help_text="0-100 proficiency")

    class Meta:
        ordering = ["-level", "name"]

    def __str__(self):
        return self.name


class Education(TimeStampedModel):
    profile = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="education")
    institution = models.CharField(max_length=150)
    degree = models.CharField(max_length=120)
    field_of_study = models.CharField(max_length=120, blank=True)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-end_year"]

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Experience(TimeStampedModel):
    profile = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="experience")
    company = models.CharField(max_length=150)
    title = models.CharField(max_length=120)
    location = models.CharField(max_length=120, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} @ {self.company}"


class Certificate(TimeStampedModel):
    profile = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="certificates")
    name = models.CharField(max_length=150)
    issuer = models.CharField(max_length=150, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    credential_url = models.URLField(blank=True)
    file = models.FileField(upload_to="certificates/", blank=True, null=True)

    def __str__(self):
        return self.name


class Language(TimeStampedModel):
    profile = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="languages")
    name = models.CharField(max_length=60)
    proficiency = models.CharField(max_length=40, default="Fluent")

    def __str__(self):
        return self.name


class Project(TimeStampedModel):
    profile = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=150)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title
