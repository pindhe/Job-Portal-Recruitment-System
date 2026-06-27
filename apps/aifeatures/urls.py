from django.urls import path

from . import views

app_name = "ai"

urlpatterns = [
    path("resume-checker/", views.resume_checker_view, name="resume_checker"),
    path("cover-letter/", views.cover_letter_view, name="cover_letter"),
    path("career-advisor/", views.career_advisor_view, name="career_advisor"),
]
