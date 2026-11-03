from django import forms

from accounts.mixins import filter_by_branch

from .models import Master, Course


class MasterForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            perm = 'add_master' if self.instance.pk is None else 'change_master'
            allowed_branches = user.get_branches_for_perm(perm)
            allowed_ids = [b.pk for b in allowed_branches]
            self.fields['branch'].queryset = self.fields['branch'].queryset.filter(
                pk__in=allowed_ids
            )

    class Meta:
        model = Master
        fields = ['branch', 'program_type', 'code', 'name', 'period', 'hours']
        widgets = {
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'program_type': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'يتم التوليد تلقائيًا إذا تركته فارغًا'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'period': forms.TextInput(attrs={'class': 'form-control'}),
            'hours': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CourseForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            perm = 'add_course' if self.instance.pk is None else 'change_course'
            self.fields['master'].queryset = filter_by_branch(
                self.fields['master'].queryset,
                user,
                'branch',
                perm=perm,
            )

    class Meta:
        model = Course
        fields = ['master', 'code', 'name', 'instructor', 'company_name', 'max_student_count', 'target_level', 'hours', 'start_date', 'end_date']
        widgets = {
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
