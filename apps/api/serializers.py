from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.companies.models import Company
from apps.jobs.models import Job, JobApplication, JobCategory, SavedJob
from apps.notifications.models import Notification

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "full_name", "role", "phone", "avatar", "email_verified"]
        read_only_fields = ["email_verified", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "role", "password"]

    def validate_role(self, value):
        if value not in {"candidate", "employer", "recruiter"}:
            raise serializers.ValidationError("Invalid role for self-registration.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CompanySerializer(serializers.ModelSerializer):
    open_jobs_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Company
        fields = ["id", "name", "slug", "org_type", "tagline", "industry", "location", "logo", "is_verified", "open_jobs_count"]


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ["id", "name", "slug", "icon"]


class JobListSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    category = JobCategorySerializer(read_only=True)
    salary_display = serializers.CharField(read_only=True)

    class Meta:
        model = Job
        fields = [
            "id", "title", "slug", "company", "category", "job_type", "work_mode",
            "experience_level", "location", "salary_display", "is_featured", "is_urgent",
            "published_at",
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    category = JobCategorySerializer(read_only=True)
    salary_display = serializers.CharField(read_only=True)
    skill_list = serializers.ListField(read_only=True)
    applications_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Job
        fields = [
            "id", "title", "slug", "company", "category", "job_type", "work_mode",
            "experience_level", "description", "responsibilities", "requirements",
            "qualifications", "benefits", "skill_list", "location", "salary_display",
            "salary_min", "salary_max", "vacancies", "deadline", "is_featured", "is_urgent",
            "views_count", "applications_count", "published_at",
        ]


class JobApplicationSerializer(serializers.ModelSerializer):
    job = JobListSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.filter(status="published"), source="job", write_only=True
    )

    class Meta:
        model = JobApplication
        fields = ["id", "job", "job_id", "cover_letter", "status", "ai_match_score", "created_at"]
        read_only_fields = ["status", "ai_match_score"]

    def create(self, validated_data):
        validated_data["candidate"] = self.context["request"].user
        return super().create(validated_data)


class SavedJobSerializer(serializers.ModelSerializer):
    job = JobListSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all(), source="job", write_only=True)

    class Meta:
        model = SavedJob
        fields = ["id", "job", "job_id", "created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "body", "url", "icon", "is_read", "created_at"]
