from django.contrib import admin

from .models import Permit, PermitTemplate, ReferralCode


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'person', 'created_at')
    search_fields = ('code', 'person__email', 'person__first_name')
    raw_id_fields = ('person',)


@admin.register(Permit)
class PermitAdmin(admin.ModelAdmin):
    list_display = ('number', 'student', 'branch', 'program_name', 'issue_date', 'expiry_date', 'status')
    list_filter = ('status', 'branch')
    search_fields = ('number', 'program_name', 'student__contact__first_name', 'student__contact__identity_number')
    raw_id_fields = ('student', 'course', 'offer', 'issued_by', 'referral_employee')


@admin.register(PermitTemplate)
class PermitTemplateAdmin(admin.ModelAdmin):
    list_display = ('branch', 'font_family', 'orientation', 'updated_at')
