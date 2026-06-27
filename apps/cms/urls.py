from django.urls import path

from . import views

app_name = "public"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("pricing-info/", views.pricing, name="pricing"),
    path("faqs/", views.faqs, name="faqs"),
    path("career/cv-tips/", views.cv_guide, name="cv_guide"),
    path("career/interview-tips/", views.interview_guide, name="interview_guide"),
    path("contact/", views.contact, name="contact"),
    path("newsletter/", views.newsletter_subscribe, name="newsletter"),
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("page/<slug:slug>/", views.page_detail, name="page"),
]
