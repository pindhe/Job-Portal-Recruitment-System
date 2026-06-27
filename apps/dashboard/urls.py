from django.urls import path

from . import manage, views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),

    # Candidate
    path("candidate/", views.candidate_dashboard, name="candidate"),
    path("resume/", views.resume_builder, name="resume_builder"),
    path("resume/preview/", views.resume_preview, name="resume_preview"),
    path("applied/", views.applied_jobs, name="applied_jobs"),
    path("saved/", views.saved_jobs, name="saved_jobs"),

    # Employer
    path("employer/", views.employer_dashboard, name="employer"),
    path("employer/jobs/", views.employer_jobs, name="employer_jobs"),
    path("employer/jobs/new/", views.job_create, name="job_create"),
    path("employer/jobs/<int:pk>/edit/", views.job_edit, name="job_edit"),
    path("employer/jobs/<int:pk>/applicants/", views.job_applicants, name="job_applicants"),
    path("applications/<int:pk>/status/", views.update_application_status, name="update_application_status"),
    path("employer/company/", views.company_edit, name="company_edit"),
    path("billing/", views.billing, name="billing"),

    # Recruiter
    path("recruiter/", views.recruiter_dashboard, name="recruiter"),

    # Admin
    path("admin-panel/", views.admin_dashboard, name="admin"),
    path("admin-panel/users/", views.admin_users, name="admin_users"),
    path("admin-panel/jobs/", views.admin_jobs, name="admin_jobs"),
    path("admin-panel/jobs/<int:pk>/approve/", views.admin_job_approve, name="admin_job_approve"),

    # Generic content management (CRUD)
    path("admin-panel/manage/<str:key>/", manage.manage_list, name="manage_list"),
    path("admin-panel/manage/<str:key>/new/", manage.manage_create, name="manage_create"),
    path("admin-panel/manage/<str:key>/<int:pk>/edit/", manage.manage_update, name="manage_update"),
    path("admin-panel/manage/<str:key>/<int:pk>/delete/", manage.manage_delete, name="manage_delete"),
]
