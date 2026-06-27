from django.contrib import admin

from .models import (
    ApplicationEvent,
    Job,
    JobApplication,
    JobCategory,
    SavedJob,
)


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "job_type", "status", "is_featured", "is_urgent", "applications_count", "created_at")
    list_filter = ("status", "job_type", "work_mode", "experience_level", "is_featured", "is_urgent")
    search_fields = ("title", "company__name", "location", "skills")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("company",)
    list_editable = ("status", "is_featured", "is_urgent")


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "status", "ai_match_score", "rating", "is_shortlisted", "created_at")
    list_filter = ("status", "is_shortlisted")
    search_fields = ("candidate__email", "job__title")


admin.site.register([SavedJob, ApplicationEvent])
