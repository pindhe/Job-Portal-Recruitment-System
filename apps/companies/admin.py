from django.contrib import admin

from .models import Branch, Company, CompanyMember, Department


class BranchInline(admin.TabularInline):
    model = Branch
    extra = 0


class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 0


class MemberInline(admin.TabularInline):
    model = CompanyMember
    extra = 0


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "org_type", "industry", "is_verified", "is_featured", "created_at")
    list_filter = ("org_type", "is_verified", "is_featured", "size")
    search_fields = ("name", "industry", "location")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [BranchInline, DepartmentInline, MemberInline]


admin.site.register([Branch, Department, CompanyMember])
