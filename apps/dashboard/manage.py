"""Generic in-system admin CRUD.

A single registry drives styled list / create / update / delete pages for the
platform's content models, so admins can manage everything without the Django
admin. New models can be exposed by adding one entry to ``MANAGE_REGISTRY``.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import (
    CheckboxInput,
    ClearableFileInput,
    Select,
    SelectMultiple,
    Textarea,
    modelform_factory,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.cms.models import (
    BlogCategory,
    BlogPost,
    ContactMessage,
    FAQ,
    NewsletterSubscriber,
    Page,
    Partner,
    Testimonial,
)
from apps.companies.models import Company
from apps.jobs.models import JobCategory
from apps.payments.models import Coupon, Plan


# key -> configuration for the generic CRUD engine
MANAGE_REGISTRY = {
    "blog-posts": {
        "model": BlogPost,
        "label": "Blog Post",
        "label_plural": "Blog Posts",
        "icon": "newspaper",
        "group": "Content",
        "fields": ["title", "category", "excerpt", "content", "cover", "is_published"],
        "list": [("title", "Title"), ("category", "Category"), ("is_published", "Published"), ("created_at", "Created")],
        "search": ["title", "excerpt"],
    },
    "blog-categories": {
        "model": BlogCategory,
        "label": "Blog Category",
        "label_plural": "Blog Categories",
        "icon": "folder",
        "group": "Content",
        "fields": ["name"],
        "list": [("name", "Name"), ("slug", "Slug")],
        "search": ["name"],
    },
    "pages": {
        "model": Page,
        "label": "Page",
        "label_plural": "Pages",
        "icon": "file-text",
        "group": "Content",
        "fields": ["title", "content", "meta_description", "is_published"],
        "list": [("title", "Title"), ("slug", "Slug"), ("is_published", "Published")],
        "search": ["title"],
    },
    "faqs": {
        "model": FAQ,
        "label": "FAQ",
        "label_plural": "FAQs",
        "icon": "help-circle",
        "group": "Content",
        "fields": ["question", "answer", "order", "is_active"],
        "list": [("question", "Question"), ("order", "Order"), ("is_active", "Active")],
        "search": ["question"],
    },
    "testimonials": {
        "model": Testimonial,
        "label": "Testimonial",
        "label_plural": "Testimonials",
        "icon": "quote",
        "group": "Content",
        "fields": ["name", "role", "company", "avatar", "quote", "rating", "is_active"],
        "list": [("name", "Name"), ("company", "Company"), ("rating", "Rating"), ("is_active", "Active")],
        "search": ["name", "company"],
    },
    "partners": {
        "model": Partner,
        "label": "Partner",
        "label_plural": "Partners",
        "icon": "handshake",
        "group": "Content",
        "fields": ["name", "logo", "website", "is_active"],
        "list": [("name", "Name"), ("website", "Website"), ("is_active", "Active")],
        "search": ["name"],
    },
    "job-categories": {
        "model": JobCategory,
        "label": "Job Category",
        "label_plural": "Job Categories",
        "icon": "layers",
        "group": "Catalog",
        "fields": ["name", "icon", "description"],
        "list": [("name", "Name"), ("slug", "Slug")],
        "search": ["name"],
    },
    "companies": {
        "model": Company,
        "label": "Company",
        "label_plural": "Companies",
        "icon": "building-2",
        "group": "Catalog",
        "fields": ["name", "org_type", "tagline", "industry", "location", "website", "email", "phone", "logo", "is_verified", "is_featured"],
        "list": [("name", "Name"), ("industry", "Industry"), ("is_verified", "Verified"), ("is_featured", "Featured")],
        "search": ["name", "industry"],
    },
    "plans": {
        "model": Plan,
        "label": "Plan",
        "label_plural": "Plans",
        "icon": "gem",
        "group": "Monetization",
        "fields": ["name", "price", "currency", "billing_cycle", "job_post_limit", "featured_job_limit",
                   "resume_views_limit", "has_ai_tools", "has_analytics", "description", "is_active", "is_popular", "order"],
        "list": [("name", "Name"), ("price", "Price"), ("billing_cycle", "Cycle"), ("is_active", "Active"), ("is_popular", "Popular")],
        "search": ["name"],
    },
    "coupons": {
        "model": Coupon,
        "label": "Coupon",
        "label_plural": "Coupons",
        "icon": "ticket",
        "group": "Monetization",
        "fields": ["code", "percent_off", "amount_off", "valid_until", "max_uses", "is_active"],
        "list": [("code", "Code"), ("percent_off", "% Off"), ("max_uses", "Max Uses"), ("is_active", "Active")],
        "search": ["code"],
    },
    "contact-messages": {
        "model": ContactMessage,
        "label": "Contact Message",
        "label_plural": "Contact Messages",
        "icon": "mail",
        "group": "Inbox",
        "fields": ["name", "email", "subject", "message", "is_handled"],
        "list": [("name", "Name"), ("email", "Email"), ("subject", "Subject"), ("is_handled", "Handled"), ("created_at", "Received")],
        "search": ["name", "email", "subject"],
        "can_create": False,
    },
    "newsletter": {
        "model": NewsletterSubscriber,
        "label": "Subscriber",
        "label_plural": "Newsletter Subscribers",
        "icon": "mail-check",
        "group": "Inbox",
        "fields": ["email", "is_active"],
        "list": [("email", "Email"), ("is_active", "Active"), ("created_at", "Subscribed")],
        "search": ["email"],
    },
}

INPUT_CLS = ("w-full rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 "
             "px-4 py-2.5 text-slate-800 dark:text-slate-100 focus:border-primary focus:ring-2 "
             "focus:ring-primary/30 outline-none transition")


def manage_menu_items():
    """Return registry entries for the sidebar/menu, preserving order."""
    return [
        {"key": key, "label": cfg["label_plural"], "icon": cfg["icon"], "group": cfg["group"]}
        for key, cfg in MANAGE_REGISTRY.items()
    ]


def _get_config(key):
    cfg = MANAGE_REGISTRY.get(key)
    if not cfg:
        return None
    return cfg


def _style_form(form):
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, CheckboxInput):
            widget.attrs.setdefault("class", "w-5 h-5 rounded border-slate-300 text-primary focus:ring-primary/30")
        elif isinstance(widget, (Select, SelectMultiple)):
            widget.attrs.setdefault("class", INPUT_CLS)
        elif isinstance(widget, ClearableFileInput):
            widget.attrs.setdefault("class", "block w-full text-sm text-slate-500 file:mr-3 file:py-2 file:px-4 "
                                              "file:rounded-lg file:border-0 file:bg-primary/10 file:text-primary file:font-semibold")
        else:
            widget.attrs.setdefault("class", INPUT_CLS)
            if isinstance(widget, Textarea):
                widget.attrs.setdefault("rows", 5)
    return form


def _cell(obj, field):
    """Render a display-friendly cell for the list table."""
    display_attr = f"get_{field}_display"
    if hasattr(obj, display_attr):
        value = getattr(obj, display_attr)()
    else:
        value = getattr(obj, field, "")
    if isinstance(value, bool):
        return {"type": "bool", "value": value}
    if hasattr(value, "strftime"):
        return {"type": "text", "value": value.strftime("%b %d, %Y")}
    return {"type": "text", "value": "" if value is None else str(value)}


def _guard(request):
    return getattr(request.user, "is_admin_side", False)


@login_required
def manage_list(request, key):
    if not _guard(request):
        return redirect("dashboard:home")
    cfg = _get_config(key)
    if not cfg:
        messages.error(request, "Unknown content type.")
        return redirect("dashboard:admin")

    model = cfg["model"]
    qs = model._default_manager.all().order_by("-pk")
    q = request.GET.get("q", "").strip()
    if q and cfg.get("search"):
        cond = Q()
        for sf in cfg["search"]:
            cond |= Q(**{f"{sf}__icontains": q})
        qs = qs.filter(cond)

    paginator = Paginator(qs, 15)
    page = paginator.get_page(request.GET.get("page"))
    rows = [
        {"pk": obj.pk, "cells": [_cell(obj, f) for f, _ in cfg["list"]]}
        for obj in page.object_list
    ]
    context = {
        "key": key,
        "cfg": cfg,
        "columns": [label for _, label in cfg["list"]],
        "rows": rows,
        "page_obj": page,
        "is_paginated": page.has_other_pages(),
        "q": q,
        "total": paginator.count,
        "can_create": cfg.get("can_create", True),
    }
    return render(request, "dashboard/admin/manage_list.html", context)


@login_required
def manage_create(request, key):
    if not _guard(request):
        return redirect("dashboard:home")
    cfg = _get_config(key)
    if not cfg or not cfg.get("can_create", True):
        return redirect("dashboard:admin")

    Form = modelform_factory(cfg["model"], fields=cfg["fields"])
    form = _style_form(Form(request.POST or None, request.FILES or None))
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{cfg['label']} created.")
        return redirect("dashboard:manage_list", key=key)
    return render(request, "dashboard/admin/manage_form.html", {"key": key, "cfg": cfg, "form": form, "is_new": True})


@login_required
def manage_update(request, key, pk):
    if not _guard(request):
        return redirect("dashboard:home")
    cfg = _get_config(key)
    if not cfg:
        return redirect("dashboard:admin")

    obj = get_object_or_404(cfg["model"]._default_manager.all(), pk=pk)
    Form = modelform_factory(cfg["model"], fields=cfg["fields"])
    form = _style_form(Form(request.POST or None, request.FILES or None, instance=obj))
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{cfg['label']} updated.")
        return redirect("dashboard:manage_list", key=key)
    return render(request, "dashboard/admin/manage_form.html",
                  {"key": key, "cfg": cfg, "form": form, "is_new": False, "obj": obj})


@login_required
def manage_delete(request, key, pk):
    if not _guard(request):
        return redirect("dashboard:home")
    cfg = _get_config(key)
    if not cfg:
        return redirect("dashboard:admin")

    obj = get_object_or_404(cfg["model"]._default_manager.all(), pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, f"{cfg['label']} deleted.")
        return redirect("dashboard:manage_list", key=key)
    return render(request, "dashboard/admin/manage_confirm_delete.html",
                  {"key": key, "cfg": cfg, "obj": obj})
