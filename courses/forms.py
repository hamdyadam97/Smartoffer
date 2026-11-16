from django import forms

from .models import Master, Course


class MasterForm(forms.ModelForm):
    """التخصص مشترك بين كل الفروع، فمفيش اختيار فرع."""

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        # «دبلوم موارد بشرية» بتتسجل: النوع دبلوم + الاسم «موارد بشرية»
        program_type, name = Master.split_type_prefix(cleaned_data.get('name'))
        if program_type:
            cleaned_data['program_type'] = program_type
            cleaned_data['name'] = name
        return cleaned_data

    class Meta:
        model = Master
        fields = ['program_type', 'code', 'name', 'period', 'hours']
        widgets = {
            'program_type': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'يتم التوليد تلقائيًا إذا تركته فارغًا'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: موارد بشرية (من غير كلمة دبلوم أو دورة)'}),
            'period': forms.TextInput(attrs={'class': 'form-control'}),
            'hours': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CourseForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None and not user.is_executive():
            perm = 'add_course' if self.instance.pk is None else 'change_course'
            allowed_ids = [b.pk for b in user.get_branches_for_perm(perm)]
            self.fields['branch'].queryset = self.fields['branch'].queryset.filter(pk__in=allowed_ids)

    class Meta:
        model = Course
        fields = ['branch', 'master', 'code', 'name', 'instructor', 'company_name', 'max_student_count', 'target_level', 'hours', 'start_date', 'end_date']
        widgets = {
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'master': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'يتم التوليد تلقائيًا إذا تركته فارغًا'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'instructor': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'max_student_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'target_level': forms.Select(attrs={'class': 'form-select'}),
            'hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
