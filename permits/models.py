import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone


class Permit(models.Model):
    """المشهد (إذن الدراسة) اللي بيتطلع للطالب كـ PDF."""
    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'نشط'),
        (STATUS_EXPIRED, 'منتهي'),
        (STATUS_CANCELLED, 'ملغي'),
    ]
    STUDY_MODE_CHOICES = [
        ('offline', 'حضوري'),
        ('online', 'أونلاين'),
    ]

    number = models.CharField(max_length=50, unique=True, editable=False, verbose_name='رقم المشهد')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='permits', verbose_name='الطالب')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='permits', verbose_name='الفرع')
    course = models.ForeignKey('courses.Course', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='permits', verbose_name='التخصص')
    # اسم البرنامج وقت الإصدار: بيفضل ثابت حتى لو التخصص اتعدل أو اتمسح
    program_name = models.CharField(max_length=255, blank=True, verbose_name='اسم البرنامج')
    offer = models.ForeignKey('offers.StudentOffer', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='permits', verbose_name='العرض المرتبط')
    study_mode = models.CharField(max_length=20, choices=STUDY_MODE_CHOICES, blank=True, verbose_name='طريقة الدراسة')
    issue_date = models.DateField(default=timezone.localdate, verbose_name='تاريخ الإصدار')
    expiry_date = models.DateField(verbose_name='تاريخ الانتهاء')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE, db_index=True, verbose_name='الحالة')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    issued_by = models.ForeignKey('accounts.Person', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='issued_permits', verbose_name='أصدره')
    # الإصدار من البوابة العامة عن طريق رابط إحالة موظف
    issued_from_public = models.BooleanField(default=False, verbose_name='من البوابة العامة')
    referral_employee = models.ForeignKey('accounts.Person', on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='referred_permits', verbose_name='موظف الإحالة')
    referral_code = models.CharField(max_length=20, blank=True, verbose_name='كود الإحالة')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'مشهد'
        verbose_name_plural = 'المشاهد'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['student', 'status']), models.Index(fields=['branch', 'status'])]

    def __str__(self):
        return f'{self.number} - {self.student}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self.generate_number()
        if not self.program_name and self.course_id:
            self.program_name = self.course.get_display_name()
        if not self.expiry_date:
            end = self.course.end_date if self.course_id else None
            self.expiry_date = end or (self.issue_date or timezone.localdate()) + timedelta(days=365)
        super().save(*args, **kwargs)

    @classmethod
    def generate_number(cls):
        year = timezone.localdate().year
        while True:
            number = f'PERM-{year}-{secrets.randbelow(900000) + 100000}'
            if not cls.objects.filter(number=number).exists():
                return number

    @property
    def effective_status(self):
        """النشط اللي تاريخه عدّى بيتعرض منتهي من غير ما نغير المتخزن."""
        if self.status == self.STATUS_ACTIVE and self.expiry_date and timezone.localdate() > self.expiry_date:
            return self.STATUS_EXPIRED
        return self.status

    def get_effective_status_display(self):
        return dict(self.STATUS_CHOICES)[self.effective_status]

    @property
    def is_active(self):
        return self.effective_status == self.STATUS_ACTIVE

    @classmethod
    def active(cls):
        return cls.objects.filter(status=cls.STATUS_ACTIVE, expiry_date__gte=timezone.localdate())


class PermitTemplate(models.Model):
    """قالب الـ PDF بتاع المشهد لكل فرع (HTML)."""
    FONT_CHOICES = [
        ('cairo', 'Cairo (عربي حديث)'),
        ('amiri', 'Amiri (كلاسيكي رسمي)'),
        ('droidnaskh', 'Droid Naskh (نسخ)'),
        ('arial', 'Arial'),
    ]
    ORIENTATION_CHOICES = [('portrait', 'طولي'), ('landscape', 'عرضي')]

    branch = models.OneToOneField('core.Branch', on_delete=models.CASCADE, related_name='permit_template', verbose_name='الفرع')
    header_content = models.TextField(blank=True, verbose_name='رأس الصفحة (HTML)')
    body_content = models.TextField(blank=True, verbose_name='المحتوى (HTML)')
    footer_content = models.TextField(blank=True, verbose_name='تذييل الصفحة (HTML)')
    custom_css = models.TextField(blank=True, verbose_name='CSS إضافي')
    font_family = models.CharField(max_length=20, choices=FONT_CHOICES, default='cairo', verbose_name='الخط')
    page_size = models.CharField(max_length=20, default='A4', verbose_name='مقاس الصفحة')
    orientation = models.CharField(max_length=20, choices=ORIENTATION_CHOICES, default='portrait', verbose_name='الاتجاه')
    background_image = models.ImageField(upload_to='permit_backgrounds/', blank=True, verbose_name='خلفية الصفحة')
    stamp_image = models.ImageField(upload_to='permit_stamps/', blank=True, verbose_name='الختم')
    registration_officer = models.CharField(max_length=255, blank=True, verbose_name='مسؤول التسجيل')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'قالب مشهد'
        verbose_name_plural = 'قوالب المشاهد'

    def __str__(self):
        return f'قالب مشهد {self.branch.name}'
