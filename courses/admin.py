from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'program_type', 'name', 'branch', 'instructor', 'start_date', 'end_date', 'last_update']
    list_filter = ['program_type', 'branch']
    search_fields = ['code', 'name', 'instructor']
