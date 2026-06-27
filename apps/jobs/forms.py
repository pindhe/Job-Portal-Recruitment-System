from django import forms

from .models import Job, JobApplication

INPUT = (
    "w-full rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 "
    "px-4 py-3 text-slate-800 dark:text-slate-100 focus:border-primary focus:ring-2 "
    "focus:ring-primary/30 outline-none transition"
)


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "company", "category", "title", "job_type", "work_mode", "experience_level",
            "description", "responsibilities", "requirements", "qualifications", "benefits",
            "skills", "location", "salary_min", "salary_max", "salary_currency", "salary_period",
            "education_required", "min_experience_years", "vacancies", "gender", "min_age", "max_age",
            "deadline", "attachment", "status", "is_featured", "is_urgent",
        ]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date", "class": INPUT}),
            "description": forms.Textarea(attrs={"rows": 5, "class": INPUT}),
            "responsibilities": forms.Textarea(attrs={"rows": 3, "class": INPUT}),
            "requirements": forms.Textarea(attrs={"rows": 3, "class": INPUT}),
            "qualifications": forms.Textarea(attrs={"rows": 3, "class": INPUT}),
            "benefits": forms.Textarea(attrs={"rows": 3, "class": INPUT}),
        }

    def __init__(self, *args, **kwargs):
        company_qs = kwargs.pop("company_qs", None)
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs.setdefault("class", "h-5 w-5 rounded text-primary")
            elif "class" not in widget.attrs:
                widget.attrs["class"] = INPUT
        if company_qs is not None:
            self.fields["company"].queryset = company_qs


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ["cover_letter", "resume_file"]
        widgets = {
            "cover_letter": forms.Textarea(
                attrs={"rows": 6, "class": INPUT, "placeholder": "Tell the employer why you're a great fit..."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resume_file"].widget.attrs["class"] = INPUT
