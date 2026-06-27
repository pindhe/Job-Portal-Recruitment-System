from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.candidates.forms import (
    CandidateProfileForm,
    CertificateFormSet,
    EducationFormSet,
    ExperienceFormSet,
    LanguageFormSet,
    ProjectFormSet,
    SkillFormSet,
)
from apps.candidates.models import CandidateProfile
from apps.companies.models import Company, CompanyMember
from apps.jobs.forms import JobForm
from apps.jobs.models import Job, JobApplication, SavedJob
from apps.notifications.services import notify
from apps.payments.models import Invoice, Subscription

User = get_user_model()


@login_required
def home(request):
    """Route the user to the correct dashboard based on role."""
    return redirect(request.user.dashboard_url_name)


# ---------------------------------------------------------------------------
# Candidate
# ---------------------------------------------------------------------------
@login_required
def candidate_dashboard(request):
    profile, _ = CandidateProfile.objects.get_or_create(user=request.user)
    applications = request.user.applications.select_related("job", "job__company")
    saved = SavedJob.objects.filter(user=request.user).select_related("job")
    recommended = Job.objects.filter(status=Job.Status.PUBLISHED).exclude(
        applications__candidate=request.user
    )[:5]
    context = {
        "profile": profile,
        "completion": profile.completion,
        "applications": applications[:5],
        "applications_count": applications.count(),
        "saved_count": saved.count(),
        "interview_count": applications.filter(status=JobApplication.Status.INTERVIEW).count(),
        "shortlisted_count": applications.filter(status=JobApplication.Status.SHORTLISTED).count(),
        "recommended": recommended,
        "status_breakdown": list(
            applications.values("status").annotate(n=Count("id")).order_by()
        ),
    }
    return render(request, "dashboard/candidate/overview.html", context)


@login_required
def resume_builder(request):
    profile, _ = CandidateProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = CandidateProfileForm(request.POST, request.FILES, instance=profile)
        skills = SkillFormSet(request.POST, instance=profile, prefix="skills")
        education = EducationFormSet(request.POST, instance=profile, prefix="education")
        experience = ExperienceFormSet(request.POST, request.FILES, instance=profile, prefix="experience")
        certs = CertificateFormSet(request.POST, instance=profile, prefix="certs")
        langs = LanguageFormSet(request.POST, instance=profile, prefix="langs")
        projects = ProjectFormSet(request.POST, instance=profile, prefix="projects")
        forms_valid = all(f.is_valid() for f in [form, skills, education, experience, certs, langs, projects])
        if forms_valid:
            form.save()
            for fs in [skills, education, experience, certs, langs, projects]:
                fs.save()
            messages.success(request, "Resume saved successfully.")
            return redirect("dashboard:resume_builder")
        messages.error(request, "Please correct the errors below.")
    else:
        form = CandidateProfileForm(instance=profile)
        skills = SkillFormSet(instance=profile, prefix="skills")
        education = EducationFormSet(instance=profile, prefix="education")
        experience = ExperienceFormSet(instance=profile, prefix="experience")
        certs = CertificateFormSet(instance=profile, prefix="certs")
        langs = LanguageFormSet(instance=profile, prefix="langs")
        projects = ProjectFormSet(instance=profile, prefix="projects")

    return render(
        request,
        "dashboard/candidate/resume_builder.html",
        {
            "form": form,
            "skills": skills,
            "education": education,
            "experience": experience,
            "certs": certs,
            "langs": langs,
            "projects": projects,
            "profile": profile,
        },
    )


@login_required
def resume_preview(request):
    profile = get_object_or_404(CandidateProfile, user=request.user)
    return render(request, "dashboard/candidate/resume_preview.html", {"profile": profile})


@login_required
def applied_jobs(request):
    applications = request.user.applications.select_related("job", "job__company").order_by("-created_at")
    return render(request, "dashboard/candidate/applied_jobs.html", {"applications": applications})


@login_required
def saved_jobs(request):
    saved = SavedJob.objects.filter(user=request.user).select_related("job", "job__company")
    return render(request, "dashboard/candidate/saved_jobs.html", {"saved": saved})


# ---------------------------------------------------------------------------
# Employer
# ---------------------------------------------------------------------------
def _user_companies(user):
    company_ids = set(
        CompanyMember.objects.filter(user=user).values_list("company_id", flat=True)
    )
    company_ids |= set(Company.objects.filter(owner=user).values_list("id", flat=True))
    return Company.objects.filter(id__in=company_ids)


@login_required
def employer_dashboard(request):
    companies = _user_companies(request.user)
    jobs = Job.objects.filter(company__in=companies)
    applications = JobApplication.objects.filter(job__company__in=companies)
    context = {
        "companies": companies,
        "jobs_count": jobs.count(),
        "published_count": jobs.filter(status=Job.Status.PUBLISHED).count(),
        "draft_count": jobs.filter(status=Job.Status.DRAFT).count(),
        "applications_count": applications.count(),
        "shortlisted_count": applications.filter(is_shortlisted=True).count(),
        "hired_count": applications.filter(status=JobApplication.Status.HIRED).count(),
        "recent_jobs": jobs.order_by("-created_at")[:5],
        "recent_applications": applications.select_related("candidate", "job").order_by("-created_at")[:6],
        "pipeline": list(applications.values("status").annotate(n=Count("id")).order_by()),
    }
    return render(request, "dashboard/employer/overview.html", context)


@login_required
def employer_jobs(request):
    companies = _user_companies(request.user)
    jobs = Job.objects.filter(company__in=companies).annotate(apps=Count("applications")).order_by("-created_at")
    status = request.GET.get("status")
    if status:
        jobs = jobs.filter(status=status)
    return render(request, "dashboard/employer/jobs.html", {"jobs": jobs})


@login_required
def job_create(request):
    companies = _user_companies(request.user)
    if not companies.exists():
        messages.info(request, "Create your company profile first.")
        return redirect("dashboard:company_edit")
    form = JobForm(request.POST or None, request.FILES or None, company_qs=companies)
    if request.method == "POST" and form.is_valid():
        job = form.save(commit=False)
        job.posted_by = request.user
        job.save()
        messages.success(request, "Job posted successfully.")
        return redirect("dashboard:employer_jobs")
    return render(request, "dashboard/employer/job_form.html", {"form": form, "is_new": True})


@login_required
def job_edit(request, pk):
    companies = _user_companies(request.user)
    job = get_object_or_404(Job, pk=pk, company__in=companies)
    form = JobForm(request.POST or None, request.FILES or None, instance=job, company_qs=companies)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Job updated.")
        return redirect("dashboard:employer_jobs")
    return render(request, "dashboard/employer/job_form.html", {"form": form, "is_new": False, "job": job})


@login_required
def job_applicants(request, pk):
    companies = _user_companies(request.user)
    job = get_object_or_404(Job, pk=pk, company__in=companies)
    from apps.aifeatures.services import rank_candidates

    applications = list(job.applications.select_related("candidate", "candidate__candidate_profile"))
    applications = rank_candidates(job, applications)
    return render(
        request,
        "dashboard/employer/applicants.html",
        {"job": job, "applications": applications},
    )


@login_required
def update_application_status(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    companies = _user_companies(request.user)
    if application.job.company not in companies and not request.user.is_admin_side:
        messages.error(request, "Not allowed.")
        return redirect("dashboard:home")
    if request.method == "POST":
        new_status = request.POST.get("status")
        valid = dict(JobApplication.Status.choices)
        if new_status in valid:
            application.status = new_status
            application.is_shortlisted = new_status == JobApplication.Status.SHORTLISTED
            application.save(update_fields=["status", "is_shortlisted"])
            application.events.create(actor=request.user, label=f"Status: {valid[new_status]}")
            notify(
                application.candidate,
                title="Application update",
                body=f"Your application for {application.job.title} is now '{valid[new_status]}'.",
                url=application.job.get_absolute_url(),
            )
            messages.success(request, "Application status updated.")
    return redirect("dashboard:job_applicants", pk=application.job.pk)


@login_required
def company_edit(request):
    from apps.companies.models import Company

    company = Company.objects.filter(owner=request.user).first()
    from django import forms as djforms

    class CompanyForm(djforms.ModelForm):
        class Meta:
            model = Company
            fields = ["name", "org_type", "tagline", "about", "industry", "size",
                      "founded_year", "website", "email", "phone", "location", "logo", "cover"]

    form = CompanyForm(request.POST or None, request.FILES or None, instance=company)
    for f in form.fields.values():
        f.widget.attrs.setdefault(
            "class",
            "w-full rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-3 outline-none focus:ring-2 focus:ring-primary/30",
        )
    if request.method == "POST" and form.is_valid():
        c = form.save(commit=False)
        c.owner = request.user
        c.save()
        messages.success(request, "Company profile saved.")
        return redirect("dashboard:employer")
    return render(request, "dashboard/employer/company_form.html", {"form": form, "company": company})


@login_required
def billing(request):
    subscriptions = Subscription.objects.filter(user=request.user).select_related("plan")
    invoices = Invoice.objects.filter(user=request.user)
    return render(
        request,
        "dashboard/employer/billing.html",
        {"subscriptions": subscriptions, "invoices": invoices, "active": subscriptions.filter(status="active").first()},
    )


# ---------------------------------------------------------------------------
# Recruiter
# ---------------------------------------------------------------------------
@login_required
def recruiter_dashboard(request):
    assigned = Job.objects.filter(assigned_recruiter=request.user)
    applications = JobApplication.objects.filter(job__assigned_recruiter=request.user)
    context = {
        "assigned_jobs": assigned,
        "assigned_count": assigned.count(),
        "applications_count": applications.count(),
        "interview_count": applications.filter(status=JobApplication.Status.INTERVIEW).count(),
        "hired_count": applications.filter(status=JobApplication.Status.HIRED).count(),
        "pipeline": list(applications.values("status").annotate(n=Count("id")).order_by()),
        "recent_applications": applications.select_related("candidate", "job").order_by("-created_at")[:8],
    }
    return render(request, "dashboard/recruiter/overview.html", context)


# ---------------------------------------------------------------------------
# Admin / Super Admin
# ---------------------------------------------------------------------------
@login_required
def admin_dashboard(request):
    if not request.user.is_admin_side:
        messages.error(request, "Admin access required.")
        return redirect("dashboard:home")

    revenue = Invoice.objects.filter(status=Invoice.Status.PAID).aggregate(total=Sum("amount"))["total"] or 0
    context = {
        "users_count": User.objects.count(),
        "candidates_count": User.objects.filter(role="candidate").count(),
        "employers_count": User.objects.filter(role__in=["employer", "hr_manager"]).count(),
        "recruiters_count": User.objects.filter(role="recruiter").count(),
        "companies_count": Company.objects.count(),
        "jobs_count": Job.objects.count(),
        "applications_count": JobApplication.objects.count(),
        "subscriptions_count": Subscription.objects.filter(status="active").count(),
        "revenue": revenue,
        "recent_users": User.objects.order_by("-date_joined")[:8],
        "recent_jobs": Job.objects.select_related("company").order_by("-created_at")[:8],
        "pending_jobs": Job.objects.filter(status=Job.Status.PENDING)[:8],
        "role_breakdown": list(User.objects.values("role").annotate(n=Count("id")).order_by()),
        "monthly_jobs": _monthly_counts(Job),
        "monthly_users": _monthly_counts(User, "date_joined"),
    }
    return render(request, "dashboard/admin/overview.html", context)


def _monthly_counts(model, field="created_at"):
    """Last 6 months counts for chart rendering."""
    from django.db.models.functions import TruncMonth

    qs = (
        model.objects.annotate(m=TruncMonth(field))
        .values("m")
        .annotate(n=Count("id"))
        .order_by("m")
    )
    data = [(row["m"].strftime("%b") if row["m"] else "", row["n"]) for row in qs][-6:]
    return {"labels": [d[0] for d in data], "values": [d[1] for d in data]}


@login_required
def admin_users(request):
    if not request.user.is_admin_side:
        return redirect("dashboard:home")

    from apps.accounts.forms import AdminUserForm
    from apps.accounts.models import Role

    form = AdminUserForm()
    open_modal = False
    if request.method == "POST":
        form = AdminUserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, f"{new_user.get_role_display()} '{new_user.full_name}' created.")
            return redirect("dashboard:admin_users")
        open_modal = True
        messages.error(request, "Please correct the errors in the form.")

    users = User.objects.all().order_by("-date_joined")
    role = request.GET.get("role")
    q = request.GET.get("q")
    if role:
        users = users.filter(role=role)
    if q:
        users = users.filter(Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))

    return render(
        request,
        "dashboard/admin/users.html",
        {
            "users": users,
            "roles": Role.choices,
            "form": form,
            "open_modal": open_modal,
            "total_users": User.objects.count(),
        },
    )


@login_required
def admin_jobs(request):
    if not request.user.is_admin_side:
        return redirect("dashboard:home")
    jobs = Job.objects.select_related("company").order_by("-created_at")
    status = request.GET.get("status")
    if status:
        jobs = jobs.filter(status=status)
    base = Job.objects.all()
    counts = {
        "all": base.count(),
        "pending": base.filter(status=Job.Status.PENDING).count(),
        "published": base.filter(status=Job.Status.PUBLISHED).count(),
        "rejected": base.filter(status=Job.Status.REJECTED).count(),
        "draft": base.filter(status=Job.Status.DRAFT).count(),
    }
    return render(
        request,
        "dashboard/admin/jobs.html",
        {"jobs": jobs, "counts": counts, "current_status": status or ""},
    )


@login_required
def admin_job_approve(request, pk):
    if not request.user.is_admin_side:
        return redirect("dashboard:home")
    job = get_object_or_404(Job, pk=pk)
    job.status = Job.Status.PUBLISHED
    job.published_at = timezone.now()
    job.save(update_fields=["status", "published_at"])
    messages.success(request, f"'{job.title}' approved and published.")
    if job.posted_by:
        notify(
            job.posted_by,
            title="Job approved",
            body=f"Your job '{job.title}' has been approved and is now live.",
            url=job.get_absolute_url(),
        )
    return redirect(request.META.get("HTTP_REFERER", "dashboard:admin_jobs"))


@login_required
def admin_job_reject(request, pk):
    if not request.user.is_admin_side:
        return redirect("dashboard:home")
    job = get_object_or_404(Job, pk=pk)
    job.status = Job.Status.REJECTED
    job.save(update_fields=["status"])
    messages.success(request, f"'{job.title}' has been rejected.")
    if job.posted_by:
        notify(
            job.posted_by,
            title="Job rejected",
            body=f"Your job '{job.title}' was not approved. Please review and resubmit.",
            url=job.get_absolute_url(),
        )
    return redirect(request.META.get("HTTP_REFERER", "dashboard:admin_jobs"))
