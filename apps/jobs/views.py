from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from apps.aifeatures.services import compute_match_score
from apps.notifications.services import notify

from .forms import JobApplicationForm
from .models import Job, JobApplication, JobCategory, JobType, SavedJob, WorkMode


class JobListView(ListView):
    model = Job
    template_name = "jobs/list.html"
    context_object_name = "jobs"
    paginate_by = 10

    def get_queryset(self):
        qs = Job.objects.filter(status=Job.Status.PUBLISHED).select_related("company", "category")
        g = self.request.GET
        if q := g.get("q"):
            qs = qs.filter(
                Q(title__icontains=q) | Q(description__icontains=q) | Q(skills__icontains=q) | Q(company__name__icontains=q)
            )
        if loc := g.get("location"):
            qs = qs.filter(location__icontains=loc)
        if cat := g.get("category"):
            qs = qs.filter(category__slug=cat)
        if jt := g.get("job_type"):
            qs = qs.filter(job_type=jt)
        if wm := g.get("work_mode"):
            qs = qs.filter(work_mode=wm)
        if exp := g.get("experience_level"):
            qs = qs.filter(experience_level=exp)
        sort = g.get("sort")
        if sort == "salary":
            qs = qs.order_by("-salary_max")
        elif sort == "oldest":
            qs = qs.order_by("published_at")
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = JobCategory.objects.all()
        ctx["job_types"] = JobType.choices
        ctx["work_modes"] = WorkMode.choices
        ctx["params"] = self.request.GET
        return ctx


class JobDetailView(DetailView):
    model = Job
    template_name = "jobs/detail.html"
    context_object_name = "job"

    def get_queryset(self):
        return Job.objects.select_related("company", "category")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Job.objects.filter(pk=obj.pk).update(views_count=obj.views_count + 1)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        job = self.object
        ctx["related_jobs"] = (
            Job.objects.filter(status=Job.Status.PUBLISHED, category=job.category)
            .exclude(pk=job.pk)[:4]
        )
        user = self.request.user
        if user.is_authenticated:
            ctx["already_applied"] = job.applications.filter(candidate=user).exists()
            ctx["is_saved"] = job.saved_by.filter(user=user).exists()
            if getattr(user, "role", None) == "candidate" and hasattr(user, "candidate_profile"):
                ctx["my_match_score"] = compute_match_score(user.candidate_profile, job)
        return ctx


@login_required
def apply_job_view(request, slug):
    job = get_object_or_404(Job, slug=slug, status=Job.Status.PUBLISHED)
    if job.applications.filter(candidate=request.user).exists():
        messages.info(request, "You have already applied to this job.")
        return redirect(job.get_absolute_url())

    form = JobApplicationForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        application = form.save(commit=False)
        application.job = job
        application.candidate = request.user
        if hasattr(request.user, "candidate_profile"):
            application.ai_match_score = compute_match_score(request.user.candidate_profile, job)
            if not application.resume_file and request.user.candidate_profile.resume_file:
                application.resume_file = request.user.candidate_profile.resume_file
        application.save()
        application.events.create(actor=request.user, label="Application submitted")
        notify(
            job.posted_by,
            title="New application",
            body=f"{request.user.full_name} applied for {job.title}",
            url=job.get_absolute_url(),
        )
        messages.success(request, "Your application has been submitted!")
        return redirect("dashboard:applied_jobs")
    return render(request, "jobs/apply.html", {"job": job, "form": form})


@login_required
def toggle_save_job(request, slug):
    job = get_object_or_404(Job, slug=slug)
    saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    if not created:
        saved.delete()
        state = False
    else:
        state = True
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"saved": state})
    messages.success(request, "Saved to your list." if state else "Removed from saved jobs.")
    return redirect(job.get_absolute_url())
