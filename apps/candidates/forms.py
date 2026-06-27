from django import forms
from django.forms import inlineformset_factory

from .models import (
    CandidateProfile,
    Certificate,
    Education,
    Experience,
    Language,
    Project,
    Skill,
)

INPUT = (
    "w-full rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 "
    "px-4 py-3 text-slate-800 dark:text-slate-100 focus:border-primary focus:ring-2 "
    "focus:ring-primary/30 outline-none transition"
)


def _style(form):
    for field in form.fields.values():
        w = field.widget
        if isinstance(w, forms.CheckboxInput):
            w.attrs.setdefault("class", "h-5 w-5 rounded text-primary")
        else:
            w.attrs.setdefault("class", INPUT)


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = [
            "headline", "summary", "location", "date_of_birth", "gender", "current_title",
            "experience_years", "expected_salary", "availability", "open_to_remote", "is_public",
            "website", "linkedin", "github", "resume_file",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 4}),
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)


SkillFormSet = inlineformset_factory(
    CandidateProfile, Skill, fields=["name", "level"], extra=1, can_delete=True
)
EducationFormSet = inlineformset_factory(
    CandidateProfile, Education,
    fields=["institution", "degree", "field_of_study", "start_year", "end_year"],
    extra=1, can_delete=True,
)
ExperienceFormSet = inlineformset_factory(
    CandidateProfile, Experience,
    fields=["company", "title", "location", "start_date", "end_date", "is_current", "description"],
    extra=1, can_delete=True,
    widgets={
        "start_date": forms.DateInput(attrs={"type": "date"}),
        "end_date": forms.DateInput(attrs={"type": "date"}),
    },
)
CertificateFormSet = inlineformset_factory(
    CandidateProfile, Certificate, fields=["name", "issuer", "issue_date", "credential_url"],
    extra=1, can_delete=True,
)
LanguageFormSet = inlineformset_factory(
    CandidateProfile, Language, fields=["name", "proficiency"], extra=1, can_delete=True
)
ProjectFormSet = inlineformset_factory(
    CandidateProfile, Project, fields=["title", "url", "description"], extra=1, can_delete=True
)
