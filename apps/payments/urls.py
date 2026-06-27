from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("", views.pricing, name="pricing"),
    path("subscribe/<slug:slug>/", views.subscribe, name="subscribe"),
]
