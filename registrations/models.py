from django.db import models
from django.utils import timezone


class Account(models.Model):
    """تسجيل الطالب في الدورة"""
    PAYMENT_TYPE_CASH = 'نقدي'
    PAYMENT_TYPE_INSTALLMENT = 'تقسيط'
    PAYMENT_TYPE_CREDIT = 'آجل'
    
    PAYMENT_TYPE_CHOICES = [
        (PAYMENT_TYPE_CASH, 'نقدي'),
        (PAYMENT_TYPE_INSTALLMENT, 'تقسيط'),
        (PAYMENT_TYPE_CREDIT, 'آجل'),
    ]
    
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='accounts', verbose_name='الدورة')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='accounts', verbose_name='الطالب')
    
    code = models.PositiveIntegerField(verbose_name='الكود')
    register_date = models.DateTimeField(default=timezone.now, verbose_name='تاريخ التسجيل')
    
    course_payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default=PAYMENT_TYPE_CASH, verbose_name='نوع الدفع')
    course_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='سعر الدورة')
    course_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='قيمة الخصم')
    course_profit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='نسبة الربح')
    course_credit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='مبلغ الائتمان')
    
    note = models.TextField(blank=True, verbose_name='ملاحظات')
    
    # Tracking
    last_person = models.ForeignKey('accounts.Person', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='آخر تعديل')
    last_update = models.DateTimeField(auto_now=True, verbose_name='تاريخ التعديل')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تسجيل'
        verbose_name_plural = 'التسجيلات'
        ordering = ['-created_at']
        unique_together = ['course', 'code']

    def __str__(self):
        return f"{self.get_key()} - {self.student.get_full_name()}"

    def get_key(self):
        """Generate unique key: Year-Branch-Master-Course-Account"""
        year_shortcut = str(self.register_date.year)[-2:]
        return f"{year_shortcut}-{self.course.master.branch.code}-{self.course.master.code}-{self.course.code}-{self.code}"

    def get_key_rtl(self):
        """RTL key: Account-Course-Master-Branch-Year"""
        year_shortcut = str(self.register_date.year)[-2:]
        return f"{self.code}-{self.course.code}-{self.course.master.code}-{self.course.master.branch.code}-{year_shortcut}"

    def get_required_price(self):
        """Calculate required price based on payment type"""
        if self.course_payment_type == self.PAYMENT_TYPE_CASH:
            return float(self.course_price - (self.course_price * self.course_discount_amount / 100))
        else:
            return float(self.course_price + (self.course_price * self.course_profit_amount / 100))

    def get_paid_price(self):
        """Calculate total paid amount"""
        from finance.models import Payment
        return sum(
            payment.amount_number 
            for payment in self.payments.filter(type='ايرادات اساسية')
        )

    def get_remain_price(self):
        """Calculate remaining amount"""
        return self.get_required_price() - self.get_paid_price()


class AttachType(models.Model):
    """نوع المرفق"""
    name = models.CharField(max_length=255, verbose_name='الاسم')
    code = models.CharField(max_length=50, unique=True, verbose_name='الكود')
    description = models.TextField(blank=True, verbose_name='الوصف')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'نوع مرفق'
        verbose_name_plural = 'أنواع المرفقات'
        ordering = ['name']

    def __str__(self):
        return self.name


class Attach(models.Model):
    """المرفق"""
    attach_type = models.ForeignKey(AttachType, on_delete=models.CASCADE, related_name='attaches', verbose_name='نوع المرفق')
    person = models.ForeignKey('accounts.Person', on_delete=models.CASCADE, related_name='attaches', verbose_name='المستخدم')
    
    title = models.CharField(max_length=255, verbose_name='العنوان')
    file_data = models.TextField(verbose_name='بيانات الملف (Base64)')
    file_name = models.CharField(max_length=255, verbose_name='اسم الملف')
    file_type = models.CharField(max_length=100, verbose_name='نوع الملف')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'مرفق'
        verbose_name_plural = 'المرفقات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class AccountAttach(models.Model):
    """مرفقات التسجيل"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_attaches', verbose_name='التسجيل')
    attach = models.ForeignKey(Attach, on_delete=models.CASCADE, related_name='account_attaches', verbose_name='المرفق')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'مرفق تسجيل'
        verbose_name_plural = 'مرفقات التسجيلات'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.account.get_key()} - {self.attach.title}"


class AccountCondition(models.Model):
    """شروط التسجيل"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_conditions', verbose_name='التسجيل')
    person = models.ForeignKey('accounts.Person', on_delete=models.CASCADE, related_name='account_conditions', verbose_name='المستخدم')
    
    title = models.CharField(max_length=255, verbose_name='العنوان')
    content = models.TextField(verbose_name='المحتوى')
    fulfilled = models.BooleanField(default=False, verbose_name='تم الاستيفاء')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'شرط تسجيل'
        verbose_name_plural = 'شروط التسجيلات'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.account.get_key()} - {self.title}"


class AccountNote(models.Model):
    """ملاحظات التسجيل"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_notes', verbose_name='التسجيل')
    person = models.ForeignKey('accounts.Person', on_delete=models.CASCADE, related_name='account_notes', verbose_name='المستخدم')
    
    content = models.TextField(verbose_name='المحتوى')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'ملاحظة تسجيل'
        verbose_name_plural = 'ملاحظات التسجيلات'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.account.get_key()} - {self.content[:50]}"
