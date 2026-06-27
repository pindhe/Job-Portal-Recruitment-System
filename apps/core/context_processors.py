from django.conf import settings


def site_settings(request):
    """Expose branding + theme tokens to every template."""
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "TalentSphere"),
        "THEME": getattr(settings, "THEME", {}),
        "LANGUAGES": getattr(settings, "LANGUAGES", []),
    }
