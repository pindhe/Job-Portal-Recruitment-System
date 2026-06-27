from django.contrib import admin

from .models import (
    Certificate,
    CandidateProfile,
    Education,
    Experience,
    Language,
    Project,
    Skill,
)


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "current_title", "experience_years", "location", "is_public")
    list_filter = ("availability", "open_to_remote", "is_public")
    search_fields = ("user__email", "headline", "current_title", "location")
    inlines = [SkillInline, EducationInline, ExperienceInline]


admin.site.register([Certificate, Language, Project])
