from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.companies.models import Company
from apps.jobs.models import Job, JobApplication, JobCategory

from .models import (
    BlogPost,
    ContactMessage,
    FAQ,
    NewsletterSubscriber,
    Page,
    Partner,
    Testimonial,
)


def home(request):
    published = Job.objects.filter(status=Job.Status.PUBLISHED)
    context = {
        "featured_jobs": published.filter(is_featured=True)[:6] or published[:6],
        "urgent_jobs": published.filter(is_urgent=True)[:4],
        "recent_jobs": published.select_related("company")[:8],
        "top_companies": Company.objects.filter(is_verified=True).annotate(
            n=Count("jobs")
        ).order_by("-n")[:8],
        "categories": JobCategory.objects.annotate(n=Count("jobs")).order_by("-n")[:12],
        "testimonials": Testimonial.objects.filter(is_active=True)[:6],
        "partners": Partner.objects.filter(is_active=True)[:12],
        "latest_posts": BlogPost.objects.filter(is_published=True)[:3],
        "faqs": FAQ.objects.filter(is_active=True)[:6],
        "stats": {
            "jobs": published.count(),
            "companies": Company.objects.count(),
            "candidates": __import__("django.contrib.auth", fromlist=["get_user_model"]).get_user_model().objects.filter(role="candidate").count(),
            "applications": JobApplication.objects.count(),
        },
    }
    return render(request, "public/home.html", context)


def about(request):
    return render(request, "public/about.html", {"partners": Partner.objects.filter(is_active=True)})


def pricing(request):
    from apps.payments.models import Plan

    return render(request, "public/pricing.html", {"plans": Plan.objects.filter(is_active=True)})


def faqs(request):
    return render(request, "public/faqs.html", {"faqs": FAQ.objects.filter(is_active=True)})


def cv_guide(request):
    return render(request, "public/cv_guide.html")


def interview_guide(request):
    return render(request, "public/interview_guide.html")


def contact(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST.get("name", ""),
            email=request.POST.get("email", ""),
            subject=request.POST.get("subject", ""),
            message=request.POST.get("message", ""),
        )
        messages.success(request, "Thanks! We'll get back to you shortly.")
        return redirect("public:contact")
    return render(request, "public/contact.html")


@require_POST
def newsletter_subscribe(request):
    email = request.POST.get("email", "").strip().lower()
    if email:
        NewsletterSubscriber.objects.get_or_create(email=email)
        messages.success(request, "You're subscribed to our newsletter!")
    return redirect(request.META.get("HTTP_REFERER", "public:home"))


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_published=True)
    return render(request, "public/page.html", {"page": page})


def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True).select_related("author", "category")
    return render(request, "public/blog_list.html", {"posts": posts})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    BlogPost.objects.filter(pk=post.pk).update(views_count=post.views_count + 1)
    related = BlogPost.objects.filter(is_published=True).exclude(pk=post.pk)[:3]
    return render(request, "public/blog_detail.html", {"post": post, "related": related})
