from django.db import models


class Master(models.Model):
    """التخصص / الدبلوم"""
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='masters', verbose_name='الفرع')
    master_category = models.ForeignKey('core.MasterCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='masters', verbose_name='التصنيف')
    
    code = models.PositiveIntegerField(verbose_name='الكود')
    name = models.CharField(max_length=255, verbose_name='اسم التخصص')
    period = models.CharField(max_length=100, blank=True, verbose_name='الفترة')
    
    # Tracking
    last_person = models.ForeignKey('accounts.Person', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='آخر تعديل')
    last_update = models.DateTimeField(auto_now=True, verbose_name='تاريخ التعديل')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تخصص'
        verbose_name_plural = 'التخصصات'
        ordering = ['-created_at']
        unique_together = ['branch', 'code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Course(models.Model):
    """الدورة / الفصل"""
    LEVEL_CHOICES = [
        ('مبتدئ', 'مبتدئ'),
        ('متوسط', 'متوسط'),
        ('متقدم', 'متقدم'),
        ('الكل', 'جميع المستويات'),
    ]
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='courses', verbose_name='التخصص')
    
    code = models.PositiveIntegerField(verbose_name='الكود')
    instructor = models.CharField(max_length=255, blank=True, verbose_name='المحاضر')
    company_name = models.CharField(max_length=255, blank=True, verbose_name='اسم الشركة')
    max_student_count = models.PositiveIntegerField(default=1, verbose_name='الحد الأقصى للطلاب')
    target_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='الكل', verbose_name='المستوى المستهدف')
    
    start_date = models.DateField(null=True, blank=True, verbose_name='تاريخ البداية')
    end_date = models.DateField(null=True, blank=True, verbose_name='تاريخ النهاية')
    
    # Tracking
    last_person = models.ForeignKey('accounts.Person', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='آخر تعديل')
    last_update = models.DateTimeField(auto_now=True, verbose_name='تاريخ التعديل')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'دورة'
        verbose_name_plural = 'الدورات'
        ordering = ['-created_at']
        unique_together = ['master', 'code']

    def __str__(self):
        return f"{self.code} - {self.master.name}"

    def get_full_key(self):
        """Generate unique key: Branch-Master-Course"""
        return f"{self.master.branch.code}-{self.master.code}-{self.code}"
