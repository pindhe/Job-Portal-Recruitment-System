from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.JobListView.as_view(), name="list"),
    path("<slug:slug>/", views.JobDetailView.as_view(), name="detail"),
    path("<slug:slug>/apply/", views.apply_job_view, name="apply"),
    path("<slug:slug>/save/", views.toggle_save_job, name="toggle_save"),
]
