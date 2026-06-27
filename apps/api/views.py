from django.contrib.auth import get_user_model
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.aifeatures import services as ai_services
from apps.companies.models import Company
from apps.jobs.models import Job, JobApplication, JobCategory, SavedJob

from .serializers import (
    CompanySerializer,
    JobApplicationSerializer,
    JobCategorySerializer,
    JobDetailSerializer,
    JobListSerializer,
    NotificationSerializer,
    RegisterSerializer,
    SavedJobSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user, context={"request": request}).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Job.objects.filter(status=Job.Status.PUBLISHED).select_related("company", "category")
    lookup_field = "slug"
    filterset_fields = ["job_type", "work_mode", "experience_level", "category__slug", "is_featured", "is_urgent"]
    search_fields = ["title", "description", "skills", "company__name", "location"]
    ordering_fields = ["published_at", "salary_max", "views_count"]

    def get_serializer_class(self):
        return JobDetailSerializer if self.action == "retrieve" else JobListSerializer

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def apply(self, request, slug=None):
        job = self.get_object()
        if job.applications.filter(candidate=request.user).exists():
            return Response({"detail": "Already applied."}, status=status.HTTP_400_BAD_REQUEST)
        application = JobApplication.objects.create(
            job=job,
            candidate=request.user,
            cover_letter=request.data.get("cover_letter", ""),
        )
        profile = getattr(request.user, "candidate_profile", None)
        if profile:
            application.ai_match_score = ai_services.compute_match_score(profile, job)
            application.save(update_fields=["ai_match_score"])
        return Response(JobApplicationSerializer(application, context={"request": request}).data, status=201)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def match_score(self, request, slug=None):
        job = self.get_object()
        profile = getattr(request.user, "candidate_profile", None)
        score = ai_services.compute_match_score(profile, job) if profile else 0
        return Response({"job": job.slug, "match_score": score})


class JobCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    pagination_class = None


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    lookup_field = "slug"
    search_fields = ["name", "industry", "location"]


class ApplicationViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(candidate=self.request.user).select_related("job", "job__company")


class SavedJobViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).select_related("job", "job__company")


class NotificationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.notifications.all()

    @action(detail=False, methods=["post"])
    def read_all(self, request):
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return Response({"detail": "All marked as read."})


class ATSCheckView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        resume_text = request.data.get("resume_text", "")
        job_description = request.data.get("job_description", "")
        return Response(ai_services.ats_score(resume_text, job_description))
