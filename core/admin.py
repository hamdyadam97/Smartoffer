from django.contrib import admin
from .models import Company, Branch, Bank, MasterCategory


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone1', 'created_at']
    search_fields = ['name', 'email', 'phone1']


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'company', 'phone1', 'created_at']
    list_filter = ['company']
    search_fields = ['name', 'code', 'email']


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'account_number', 'created_at']
    list_filter = ['branch']
    search_fields = ['name', 'account_number', 'iban']


@admin.register(MasterCategory)
class MasterCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
