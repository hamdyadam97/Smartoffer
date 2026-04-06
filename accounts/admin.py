from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Team, Person, BranchAccess


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']


class BranchAccessInline(admin.TabularInline):
    model = BranchAccess
    extra = 1


@admin.register(Person)
class PersonAdmin(UserAdmin):
    list_display = ['email', 'get_full_name', 'team', 'branch', 'is_active', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_active', 'team', 'branch']
    search_fields = ['email', 'first_name', 'forth_name', 'mobile']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('المعلومات الشخصية', {'fields': ('first_name', 'second_name', 'third_name', 'forth_name', 'mobile', 'phone', 'address', 'photo')}),
        ('الإعدادات', {'fields': ('team', 'branch', 'options')}),
        ('الصلاحيات', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تواريخ', {'fields': ('last_login_date', 'ip_address', 'last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    
    ordering = ['-created_at']
    inlines = [BranchAccessInline]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'الاسم الكامل'
