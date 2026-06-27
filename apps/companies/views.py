from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from apps.jobs.models import Job

from .models import Company


class CompanyListView(ListView):
    model = Company
    template_name = "companies/list.html"
    context_object_name = "companies"
    paginate_by = 12

    def get_queryset(self):
        qs = Company.objects.all().order_by("-is_featured", "-created_at")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_companies"] = Company.objects.count()
        ctx["verified_companies"] = Company.objects.filter(is_verified=True).count()
        ctx["open_jobs"] = Job.objects.filter(status=Job.Status.PUBLISHED).count()
        return ctx


class CompanyDetailView(DetailView):
    model = Company
    template_name = "companies/detail.html"
    context_object_name = "company"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["jobs"] = self.object.jobs.filter(status="published")[:10]
        return ctx
