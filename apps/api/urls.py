from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = "api"

router = DefaultRouter()
router.register("jobs", views.JobViewSet, basename="job")
router.register("categories", views.JobCategoryViewSet, basename="category")
router.register("companies", views.CompanyViewSet, basename="company")
router.register("applications", views.ApplicationViewSet, basename="application")
router.register("saved-jobs", views.SavedJobViewSet, basename="saved-job")
router.register("notifications", views.NotificationViewSet, basename="notification")

v1_patterns = [
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", views.MeView.as_view(), name="me"),
    path("ai/ats-check/", views.ATSCheckView.as_view(), name="ats_check"),
    path("", include(router.urls)),
]

urlpatterns = [
    path("v1/", include((v1_patterns, "v1"))),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="docs"),
]
