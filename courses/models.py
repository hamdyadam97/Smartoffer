from django.db import models


class Course(models.Model):
    """التخصص: دبلوم أو دورة، بكل بياناته (الاسم، الفرع، المحاضر، التواريخ...)."""
    PROGRAM_TYPE_CHOICES = [
        ('دبلوم', 'دبلوم'),
        ('دورة', 'دورة'),
    ]
    LEVEL_CHOICES = [
        ('مبتدئ', 'مبتدئ'),
        ('متوسط', 'متوسط'),
        ('متقدم', 'متقدم'),
        ('الكل', 'جميع المستويات'),
    ]
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES, default='دبلوم', db_index=True, verbose_name='النوع')
    name = models.CharField(max_length=255, db_index=True, verbose_name='الاسم')
    # فاضي = متاح لكل الفروع
    branch = models.ForeignKey('core.Branch', on_delete=models.PROTECT, null=True, blank=True, related_name='courses', verbose_name='الفرع')

    code = models.PositiveIntegerField(db_index=True, blank=True, null=True, verbose_name='الكود')
    instructor = models.CharField(max_length=255, blank=True, db_index=True, verbose_name='المحاضر')
    company_name = models.CharField(max_length=255, blank=True, verbose_name='اسم الشركة')
    max_student_count = models.PositiveIntegerField(default=1, verbose_name='الحد الأقصى للطلاب')
    target_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='الكل', db_index=True, verbose_name='المستوى المستهدف')
    period = models.CharField(max_length=100, blank=True, verbose_name='المدة')
    hours = models.PositiveIntegerField(null=True, blank=True, db_index=True, verbose_name='عدد الساعات')

    start_date = models.DateField(null=True, blank=True, db_index=True, verbose_name='تاريخ البداية')
    end_date = models.DateField(null=True, blank=True, verbose_name='تاريخ النهاية')

    # Tracking
    last_person = models.ForeignKey('accounts.Person', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='آخر تعديل')
    last_update = models.DateTimeField(auto_now=True, verbose_name='تاريخ التعديل')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تخصص'
        verbose_name_plural = 'التخصصات'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.code is None or self.code == '':
            last = Course.objects.aggregate(models.Max('code'))['code__max']
            self.code = (last or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.get_display_name()}"

    def get_display_name(self):
        """الاسم الكامل اللي بيظهر في العروض: النوع + الاسم (مثلاً: دبلوم موارد بشرية)."""
        return f"{self.program_type} {self.name}"

    @classmethod
    def split_type_prefix(cls, name):
        """لو الاسم بادئ بـ«دبلوم» أو «دورة»، بنرجع (النوع، الاسم من غيره). غير كده (None، الاسم)."""
        name = (name or '').strip()
        prefixes = {'دبلوم': 'دبلوم', 'دورة': 'دورة', 'دوره': 'دورة'}
        for prefix, program_type in prefixes.items():
            if name.startswith(prefix + ' ') and name[len(prefix):].strip():
                return program_type, name[len(prefix):].strip()
        return None, name

    def get_full_key(self):
        """Generate unique key: Branch-Course"""
        return f"{self.branch.code if self.branch else 0}-{self.code}"
