from django.contrib import admin
from .models import Master, Course


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['code', 'program_type', 'name', 'branch', 'hours', 'last_update']
    list_filter = ['branch', 'program_type']
    search_fields = ['name', 'code']
    fieldsets = (
        (None, {
            'fields': ('branch', 'program_type', 'code', 'name', 'period', 'hours')
        }),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'master', 'instructor', 'start_date', 'end_date', 'last_update']
    list_filter = ['master__branch', 'master']
    search_fields = ['code', 'name', 'instructor']
