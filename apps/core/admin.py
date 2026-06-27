from django.contrib import admin

from .models import AuditLog, SiteSetting


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "method", "path", "status_code", "ip_address")
    list_filter = ("method", "status_code")
    search_fields = ("path", "user__email", "ip_address")
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "group", "value", "updated_at")
    list_filter = ("group",)
    search_fields = ("key", "value")
