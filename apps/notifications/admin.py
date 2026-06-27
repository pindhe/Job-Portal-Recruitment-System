from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "channel", "is_read", "created_at")
    list_filter = ("channel", "is_read")
    search_fields = ("title", "recipient__email")
