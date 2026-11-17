from django import forms
from django.db.models import Q

from core.models import Branch
from courses.models import Course
from students.models import Student
from .models import Permit, PermitTemplate
from .services import issue_error


class PermitForm(forms.ModelForm):
    """إصدار مشهد: الطالب لازم يكون في فرع مسموح للموظف يطلع فيه مشاهد."""

    class Meta:
        model = Permit
        fields = ['student', 'course', 'study_mode', 'issue_date', 'expiry_date', 'notes']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'study_mode': forms.Select(attrs={'class': 'form-select'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        help_texts = {'expiry_date': 'لو سيبته فاضي: تاريخ نهاية التخصص، أو سنة من تاريخ الإصدار.'}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        branch_ids = [b.pk for b in user.get_branches_for_perm('add_permit')]
        self.fields['student'].queryset = (Student.objects.filter(branch__in=branch_ids)
                                           .select_related('contact', 'branch').order_by('contact__first_name'))
        self.fields['student'].label_from_instance = (
            lambda s: f'{s.contact.get_full_name()} - {s.contact.identity_number or s.contact.mobile or ""} ({s.branch.name})')
        self.fields['course'].queryset = Course.objects.filter(Q(branch__in=branch_ids) | Q(branch__isnull=True))
        self.fields['course'].required = True
        self.fields['course'].label_from_instance = lambda c: c.get_display_name() + (f' - {c.branch.name}' if c.branch_id else '')
        self.fields['expiry_date'].required = False
        self.fields['issue_date'].required = False

    def clean(self):
        cleaned = super().clean()
        student, course = cleaned.get('student'), cleaned.get('course')
        if student and course and course.branch_id and course.branch_id != student.branch_id:
            self.add_error('course', 'التخصص ده تبع فرع تاني غير فرع الطالب.')
        if student:
            error = issue_error(student, student.branch)
            if error:
                raise forms.ValidationError(error)
        return cleaned

    def save(self, commit=True):
        permit = super().save(commit=False)
        permit.branch = permit.student.branch
        permit.issued_by = self.user
        if not permit.issue_date:
            from django.utils import timezone
            permit.issue_date = timezone.localdate()
        if commit:
            permit.save()
        return permit


class PermitTemplateForm(forms.ModelForm):
    class Meta:
        model = PermitTemplate
        fields = ['branch', 'institute_name', 'font_family', 'page_size', 'orientation', 'registration_officer',
                  'background_image', 'stamp_image', 'header_content', 'body_content', 'footer_content', 'custom_css']
        widgets = {
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'font_family': forms.Select(attrs={'class': 'form-select'}),
            'page_size': forms.TextInput(attrs={'class': 'form-control'}),
            'orientation': forms.Select(attrs={'class': 'form-select'}),
            'registration_officer': forms.TextInput(attrs={'class': 'form-control'}),
            'institute_name': forms.TextInput(attrs={'class': 'form-control'}),
            'header_content': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 6, 'dir': 'ltr'}),
            'body_content': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 14, 'dir': 'ltr'}),
            'footer_content': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 6, 'dir': 'ltr'}),
            'custom_css': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 8, 'dir': 'ltr'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['branch'].disabled = True
        else:
            self.fields['branch'].queryset = Branch.objects.filter(permit_template__isnull=True)
