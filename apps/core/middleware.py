"""Audit logging middleware capturing mutating requests."""
from django.utils.deprecation import MiddlewareMixin

SKIP_PREFIXES = ("/static/", "/media/", "/admin/jsi18n")
TRACKED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class AuditLogMiddleware(MiddlewareMixin):
    """Persist an :class:`AuditLog` entry for state-changing requests."""

    def process_response(self, request, response):
        try:
            if request.method in TRACKED_METHODS and not request.path.startswith(SKIP_PREFIXES):
                from apps.core.models import AuditLog

                AuditLog.objects.create(
                    user=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
                    method=request.method,
                    path=request.path[:255],
                    status_code=getattr(response, "status_code", 0),
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
                )
        except Exception:
            # Auditing must never break the request lifecycle.
            pass
        return response
