from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import PersonManager


class Team(models.Model):
    """فريق العمل"""
    name = models.CharField(max_length=255, verbose_name='اسم الفريق')
    code = models.CharField(max_length=50, unique=True, verbose_name='كود الفريق')
    description = models.TextField(blank=True, verbose_name='الوصف')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'فريق'
        verbose_name_plural = 'فرق العمل'
        ordering = ['name']

    def __str__(self):
        return self.name


class Person(AbstractBaseUser, PermissionsMixin):
    """المستخدم / الموظف"""
    email = models.EmailField(unique=True, verbose_name='البريد الإلكتروني')
    
    # Contact Info (OneToOne)
    first_name = models.CharField(max_length=100, blank=True, verbose_name='الاسم الأول')
    second_name = models.CharField(max_length=100, blank=True, verbose_name='الاسم الثاني')
    third_name = models.CharField(max_length=100, blank=True, verbose_name='الاسم الثالث')
    forth_name = models.CharField(max_length=100, blank=True, verbose_name='الاسم الرابع')
    mobile = models.CharField(max_length=20, blank=True, verbose_name='المحمول')
    phone = models.CharField(max_length=20, blank=True, verbose_name='التليفون')
    address = models.TextField(blank=True, verbose_name='العنوان')
    photo = models.TextField(blank=True, verbose_name='الصورة (Base64)')
    
    # Settings
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members', verbose_name='الفريق')
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='persons', verbose_name='الفرع الرئيسي')
    
    # Status
    is_staff = models.BooleanField(default=False, verbose_name='موظف')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    is_superuser = models.BooleanField(default=False, verbose_name='مدير نظام')
    
    # Tracking
    last_login_date = models.DateTimeField(null=True, blank=True, verbose_name='آخر دخول')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='عنوان IP')
    options = models.JSONField(default=dict, blank=True, verbose_name='الإعدادات')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PersonManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'forth_name']

    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمين'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.second_name} {self.third_name} {self.forth_name}".strip()

    def get_short_name(self):
        return f"{self.first_name} {self.forth_name}".strip()

    def get_branches(self):
        """Get all accessible branches (main + accessed)"""
        from core.models import Branch
        branches = []
        if self.branch:
            branches.append(self.branch)
        branches.extend([access.branch for access in self.branch_accesses.all()])
        return list(set(branches))


class BranchAccess(models.Model):
    """صلاحية الوصول للفروع"""
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='branch_accesses', verbose_name='المستخدم')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='accesses', verbose_name='الفرع')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'صلاحية فرع'
        verbose_name_plural = 'صلاحيات الفروع'
        unique_together = ['person', 'branch']

    def __str__(self):
        return f"{self.person.get_short_name()} - {self.branch.name}"


class Role(models.Model):
    """دور/منصب الموظف"""
    ROLE_CHOICES = [
        ('مدير_فرع', 'مدير فرع'),
        ('موظف_عروض', 'موظف عروض'),
        ('موظف_متابعة', 'موظف متابعة'),
        ('مدير_نظام', 'مدير نظام'),
    ]
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True, verbose_name='الدور')
    description = models.TextField(blank=True, verbose_name='الوصف')
    permissions = models.JSONField(default=list, blank=True, verbose_name='الصلاحيات')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'دور'
        verbose_name_plural = 'الأدوار'

    def __str__(self):
        return self.get_name_display()


class EmployeeRole(models.Model):
    """ربط الموظف بدوره"""
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='roles', verbose_name='الموظف')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='employees', verbose_name='الدور')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='employee_roles', verbose_name='الفرع')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'دور موظف'
        verbose_name_plural = 'أدوار الموظفين'
        unique_together = ['person', 'role', 'branch']

    def __str__(self):
        return f"{self.person.get_short_name()} - {self.role.get_name_display()} ({self.branch.name})"


class EmployeePerformance(models.Model):
    """أداء الموظف الشهري"""
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='performances', verbose_name='الموظف')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='performances', verbose_name='الفرع')
    period_month = models.PositiveSmallIntegerField(verbose_name='الشهر')
    period_year = models.PositiveSmallIntegerField(verbose_name='السنة')
    offers_sent = models.PositiveIntegerField(default=0, verbose_name='العروض المرسلة')
    offers_opened = models.PositiveIntegerField(default=0, verbose_name='العروض المفتوحة')
    offers_interacted = models.PositiveIntegerField(default=0, verbose_name='التفاعلات')
    subscriptions = models.PositiveIntegerField(default=0, verbose_name='الاشتراكات')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'أداء موظف'
        verbose_name_plural = 'أداء الموظفين'
        unique_together = ['person', 'branch', 'period_month', 'period_year']
        ordering = ['-period_year', '-period_month']

    def __str__(self):
        return f"{self.person.get_short_name()} - {self.period_month}/{self.period_year}"
