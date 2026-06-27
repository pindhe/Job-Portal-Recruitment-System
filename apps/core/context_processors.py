from django.conf import settings


def site_settings(request):
    """Expose branding + theme tokens + nav data to every template."""
    nav_categories = []
    popular_jobs = []
    try:
        from django.db.models import Count

        from apps.jobs.models import Job, JobCategory

        nav_categories = list(
            JobCategory.objects.annotate(n=Count("jobs")).order_by("-n", "name")[:8]
        )
        popular_jobs = list(
            Job.objects.filter(status=Job.Status.PUBLISHED)
            .select_related("company")
            .order_by("-is_featured", "-published_at")[:4]
        )
    except Exception:
        pass

    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "TalentSphere"),
        "THEME": getattr(settings, "THEME", {}),
        "LANGUAGES": getattr(settings, "LANGUAGES", []),
        "nav_categories": nav_categories,
        "nav_popular_jobs": popular_jobs,
    }
