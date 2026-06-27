"""Role based access control helpers for views and the API."""
from django.contrib.auth.mixins import AccessMixin
from rest_framework.permissions import BasePermission


class RoleRequiredMixin(AccessMixin):
    """Restrict a class-based view to a set of roles.

    Usage::

        class MyView(RoleRequiredMixin, ListView):
            allowed_roles = ["employer", "recruiter"]
    """

    allowed_roles: list[str] = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.allowed_roles and request.user.role not in self.allowed_roles and not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class HasRole(BasePermission):
    """DRF permission factory checking the authenticated user's role."""

    allowed_roles: list[str] = []

    def has_permission(self, request, view):
        roles = getattr(view, "allowed_roles", self.allowed_roles)
        if not request.user or not request.user.is_authenticated:
            return False
        if not roles:
            return True
        return request.user.role in roles or request.user.is_superuser
