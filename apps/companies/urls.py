from django.urls import path

from . import views

app_name = "companies"

urlpatterns = [
    path("", views.CompanyListView.as_view(), name="list"),
    path("<slug:slug>/", views.CompanyDetailView.as_view(), name="detail"),
]
