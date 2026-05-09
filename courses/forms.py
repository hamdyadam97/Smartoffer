from django import forms
from .models import Master, Course


class MasterForm(forms.ModelForm):
    class Meta:
        model = Master
        fields = ['branch', 'master_category', 'code', 'name', 'period']
        widgets = {
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'master_category': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.NumberInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'period': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['master', 'code', 'instructor', 'company_name', 'max_student_count', 'target_level', 'start_date', 'end_date']
        widgets = {
            'master': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.NumberInput(attrs={'class': 'form-control'}),
            'instructor': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'max_student_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'target_level': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
