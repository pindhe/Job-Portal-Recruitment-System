from django.contrib import admin

from .models import (
    BlogCategory,
    BlogPost,
    ContactMessage,
    FAQ,
    NewsletterSubscriber,
    Page,
    Partner,
    Testimonial,
)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "updated_at")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "is_published", "views_count", "created_at")
    list_filter = ("is_published", "category")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "is_handled", "created_at")
    list_filter = ("is_handled",)


admin.site.register([BlogCategory, Testimonial, Partner, NewsletterSubscriber])
