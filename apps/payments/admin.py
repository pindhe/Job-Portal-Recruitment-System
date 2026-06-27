from django.contrib import admin

from .models import Coupon, Invoice, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "currency", "billing_cycle", "is_active", "is_popular", "order")
    list_editable = ("is_active", "is_popular", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "started_at", "expires_at", "auto_renew")
    list_filter = ("status", "plan")
    search_fields = ("user__email",)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "user", "amount", "status", "gateway", "created_at")
    list_filter = ("status", "gateway")
    search_fields = ("number", "user__email", "reference")


admin.site.register(Coupon)
