from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.jobs.models import Job

from . import services


@login_required
def resume_checker_view(request):
    result = None
    resume_text = ""
    job_description = ""
    if request.method == "POST":
        resume_text = request.POST.get("resume_text", "")
        job_description = request.POST.get("job_description", "")
        if not resume_text and hasattr(request.user, "candidate_profile"):
            p = request.user.candidate_profile
            resume_text = "\n".join(
                [p.summary, p.current_title]
                + [f"{e.title} {e.company} {e.description}" for e in p.experience.all()]
                + [s.name for s in p.skills.all()]
            )
        result = services.ats_score(resume_text, job_description)
    return render(
        request,
        "ai/resume_checker.html",
        {"result": result, "resume_text": resume_text, "job_description": job_description},
    )


@login_required
def cover_letter_view(request):
    letter = None
    if request.method == "POST":
        job_title = request.POST.get("job_title", "the role")
        company = request.POST.get("company", "your company")
        skills = [s.strip() for s in request.POST.get("skills", "").split(",") if s.strip()]
        letter = services.generate_cover_letter(request.user.full_name, job_title, company, skills)
    return render(request, "ai/cover_letter.html", {"letter": letter})


@login_required
def career_advisor_view(request):
    """Suggest jobs + skill gaps for the logged-in candidate."""
    recommendations = []
    if hasattr(request.user, "candidate_profile"):
        profile = request.user.candidate_profile
        jobs = Job.objects.filter(status=Job.Status.PUBLISHED)[:50]
        scored = [(services.compute_match_score(profile, j), j) for j in jobs]
        scored.sort(key=lambda x: x[0], reverse=True)
        recommendations = [
            {"job": j, "score": s, "gap": services.skill_gap_analysis(profile, j)}
            for s, j in scored[:6]
        ]
    return render(request, "ai/career_advisor.html", {"recommendations": recommendations})
