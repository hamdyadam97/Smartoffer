from django.db import models


class ReportSnapshot(models.Model):
    """لقطة تقرير"""
    REPORT_TYPE_CHOICES = [
        ('summary', 'ملخص عام'),
        ('offers', 'تقرير العروض'),
        ('branches', 'تقرير الفروع'),
        ('employees', 'تقرير الموظفين'),
        ('students', 'تقرير الطلاب'),
    ]

    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, verbose_name='نوع التقرير')
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='reports', verbose_name='الفرع')
    period = models.CharField(max_length=50, blank=True, verbose_name='الفترة')
    generated_by = models.ForeignKey('accounts.Person', on_delete=models.CASCADE, related_name='generated_reports', verbose_name='تم الإنشاء بواسطة')
    data_json = models.JSONField(default=dict, verbose_name='بيانات التقرير')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تقرير'
        verbose_name_plural = 'التقارير'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.period}"
