from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class StudentOffer(models.Model):
    """عرض الطالب"""
    STATUS_CHOICES = [
        ('مسودة', 'مسودة'),
        ('مجدولة', 'مجدولة'),
        ('مرسلة', 'مرسلة'),
        ('منتهية', 'منتهية'),
    ]
    TARGET_LEVEL_CHOICES = [
        ('مبتدئ', 'مبتدئ'),
        ('متوسط', 'متوسط'),
        ('متقدم', 'متقدم'),
        ('الكل', 'جميع المستويات'),
    ]

    title = models.CharField(max_length=255, verbose_name='عنوان العرض')
    content = models.TextField(verbose_name='محتوى العرض')
    branch = models.ForeignKey('core.Branch', on_delete=models.PROTECT, db_index=True, related_name='offers', verbose_name='الفرع')
    course = models.ForeignKey('courses.Course', on_delete=models.SET_NULL, null=True, blank=True, db_index=True, related_name='offers', verbose_name='الدورة')
    target_level = models.CharField(max_length=20, choices=TARGET_LEVEL_CHOICES, default='الكل', db_index=True, verbose_name='المستوى المستهدف')
    scheduled_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name='موعد الإرسال')
    sent_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name='تاريخ الإرسال الفعلي')
    slug = models.SlugField(unique=True, blank=True, null=True, db_index=True, verbose_name='الرابط')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='مسودة', db_index=True, verbose_name='الحالة')
    created_by = models.ForeignKey('accounts.Person', on_delete=models.CASCADE, db_index=True, related_name='created_offers', verbose_name='تم الإنشاء بواسطة')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'عرض طالب'
        verbose_name_plural = 'عروض الطلاب'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            while StudentOffer.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
            StudentOffer.objects.filter(pk=self.pk).update(slug=self.slug)

    def __str__(self):
        return self.title

    def send_now(self):
        self.status = 'مرسلة'
        self.sent_at = timezone.now()
        self.save()


class OfferRecipient(models.Model):
    """مستلم العرض"""
    CHANNEL_CHOICES = [
        ('email', 'البريد الإلكتروني'),
        ('whatsapp', 'واتساب'),
        ('app', 'إشعار التطبيق'),
    ]
    STATUS_CHOICES = [
        ('مرسل', 'مرسل'),
        ('مقروء', 'مقروء'),
        ('تفاعل', 'تم التفاعل'),
        ('اشترك', 'تم الاشتراك'),
        ('لم_يتفاعل', 'لم يتفاعل'),
    ]

    offer = models.ForeignKey(StudentOffer, on_delete=models.PROTECT, db_index=True, related_name='recipients', verbose_name='العرض')
    student = models.ForeignKey('students.Student', on_delete=models.PROTECT, db_index=True, related_name='offer_recipients', verbose_name='الطالب')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, db_index=True, verbose_name='قناة الإرسال')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='مرسل', db_index=True, verbose_name='حالة التفاعل')
    sent_at = models.DateTimeField(auto_now_add=True)
    opened_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الفتح')
    interacted_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ التفاعل')

    class Meta:
        verbose_name = 'مستلم عرض'
        verbose_name_plural = 'مستلمو العروض'
        unique_together = ['offer', 'student', 'channel']
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.offer.title}"


class OfferNote(models.Model):
    """ملاحظة على العرض"""
    offer = models.ForeignKey(StudentOffer, on_delete=models.CASCADE, related_name='notes', verbose_name='العرض')
    person = models.ForeignKey('accounts.Person', on_delete=models.CASCADE, related_name='offer_notes', verbose_name='الموظف')
    note_text = models.TextField(verbose_name='الملاحظة')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'ملاحظة عرض'
        verbose_name_plural = 'ملاحظات العروض'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.person.get_short_name()} - {self.offer.title}"
