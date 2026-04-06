from django.db import models


class Company(models.Model):
    """الشركة"""
    name = models.CharField(max_length=255, verbose_name='اسم الشركة')
    sub_name = models.CharField(max_length=255, blank=True, verbose_name='الاسم الفرعي')
    address = models.TextField(blank=True, verbose_name='العنوان')
    phone1 = models.CharField(max_length=20, blank=True, verbose_name='التليفون 1')
    phone2 = models.CharField(max_length=20, blank=True, verbose_name='التليفون 2')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='الرقم البريدي')
    mobile = models.CharField(max_length=20, blank=True, verbose_name='المحمول')
    fax = models.CharField(max_length=20, blank=True, verbose_name='الفاكس')
    email = models.EmailField(blank=True, verbose_name='البريد الإلكتروني')
    website = models.URLField(blank=True, verbose_name='الموقع الإلكتروني')
    commercial_registration = models.CharField(max_length=50, blank=True, verbose_name='السجل التجاري')
    tax_code = models.CharField(max_length=50, blank=True, verbose_name='الرقم الضريبي')
    logo = models.TextField(blank=True, verbose_name='الشعار (Base64)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'شركة'
        verbose_name_plural = 'الشركات'
        ordering = ['name']

    def __str__(self):
        return self.name


class Branch(models.Model):
    """الفرع"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='branches', verbose_name='الشركة')
    code = models.PositiveIntegerField(unique=True, verbose_name='الكود')
    name = models.CharField(max_length=255, verbose_name='اسم الفرع')
    sub_name = models.CharField(max_length=255, blank=True, verbose_name='الاسم الفرعي')
    address = models.TextField(blank=True, verbose_name='العنوان')
    phone1 = models.CharField(max_length=20, blank=True, verbose_name='التليفون 1')
    phone2 = models.CharField(max_length=20, blank=True, verbose_name='التليفون 2')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='الرقم البريدي')
    mobile = models.CharField(max_length=20, blank=True, verbose_name='المحمول')
    fax = models.CharField(max_length=20, blank=True, verbose_name='الفاكس')
    email = models.EmailField(blank=True, verbose_name='البريد الإلكتروني')
    website = models.URLField(blank=True, verbose_name='الموقع الإلكتروني')
    commercial_registration = models.CharField(max_length=50, blank=True, verbose_name='السجل التجاري')
    licence_code = models.CharField(max_length=50, blank=True, verbose_name='رقم الترخيص')
    tax_code = models.CharField(max_length=50, blank=True, verbose_name='الرقم الضريبي')
    logo = models.TextField(blank=True, verbose_name='الشعار (Base64)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'فرع'
        verbose_name_plural = 'الفروع'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Bank(models.Model):
    """البنك"""
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='banks', verbose_name='الفرع')
    name = models.CharField(max_length=255, verbose_name='اسم البنك')
    account_number = models.CharField(max_length=100, verbose_name='رقم الحساب')
    iban = models.CharField(max_length=100, blank=True, verbose_name='IBAN')
    swift = models.CharField(max_length=50, blank=True, verbose_name='SWIFT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'بنك'
        verbose_name_plural = 'البنوك'
        ordering = ['name']

    def __str__(self):
        return self.name


class MasterCategory(models.Model):
    """تصنيف التخصص"""
    name = models.CharField(max_length=255, verbose_name='اسم التصنيف')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تصنيف التخصص'
        verbose_name_plural = 'تصنيفات التخصصات'
        ordering = ['name']

    def __str__(self):
        return self.name
