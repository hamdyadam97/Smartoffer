from django.contrib import admin
from .models import Master, Course


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['code', 'program_type', 'name', 'hours', 'last_update']
    list_filter = ['program_type']
    search_fields = ['name', 'code']
    fieldsets = (
        (None, {
            'fields': ('program_type', 'code', 'name', 'period', 'hours')
        }),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'master', 'branch', 'instructor', 'start_date', 'end_date', 'last_update']
    list_filter = ['branch', 'master']
    search_fields = ['code', 'name', 'instructor']
