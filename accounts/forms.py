from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import Person, Team, BranchAccess, Role, EmployeeRole, EmployeePerformance, Permission, Permission


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['branch', 'name', 'code', 'description', 'default_role', 'default_branch']
        widgets = {
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'default_role': forms.Select(attrs={'class': 'form-select'}),
            'default_branch': forms.Select(attrs={'class': 'form-select'}),
        }


class PersonCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='تأكيد كلمة المرور',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Person
        fields = [
            'email', 'first_name', 'second_name', 'third_name', 'forth_name',
            'mobile', 'phone', 'address', 'photo', 'team', 'branch',
            'is_staff', 'is_active', 'is_superuser', 'options'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'second_name': forms.TextInput(attrs={'class': 'form-control'}),
            'third_name': forms.TextInput(attrs={'class': 'form-control'}),
            'forth_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'team': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'options': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('كلمتا المرور غير متطابقتين')
        return password2

    def save(self, commit=True):
        person = super().save(commit=False)
        person.set_password(self.cleaned_data['password1'])
        if commit:
            person.save()
        return person


class PersonChangeForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            'email', 'first_name', 'second_name', 'third_name', 'forth_name',
            'mobile', 'phone', 'address', 'photo', 'team', 'branch',
            'is_staff', 'is_active', 'is_superuser', 'options'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'second_name': forms.TextInput(attrs={'class': 'form-control'}),
            'third_name': forms.TextInput(attrs={'class': 'form-control'}),
            'forth_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'team': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'options': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class BranchAccessForm(forms.ModelForm):
    class Meta:
        model = BranchAccess
        fields = ['person', 'branch']
        widgets = {
            'person': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
        }


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description', 'permissions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: مدير تنفيذي'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'permissions': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permissions'].queryset = Permission.objects.all().order_by('app_label', 'model_name', 'action')
        self.fields['permissions'].required = False


class EmployeeRoleForm(forms.ModelForm):
    class Meta:
        model = EmployeeRole
        fields = ['person', 'role', 'branch']
        widgets = {
            'person': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
        }


class EmployeePerformanceForm(forms.ModelForm):
    class Meta:
        model = EmployeePerformance
        fields = [
            'person', 'branch', 'period_month', 'period_year',
            'offers_sent', 'offers_opened', 'offers_interacted', 'subscriptions'
        ]
        widgets = {
            'person': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'period_month': forms.NumberInput(attrs={'class': 'form-control'}),
            'period_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'offers_sent': forms.NumberInput(attrs={'class': 'form-control'}),
            'offers_opened': forms.NumberInput(attrs={'class': 'form-control'}),
            'offers_interacted': forms.NumberInput(attrs={'class': 'form-control'}),
            'subscriptions': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['codename', 'name', 'app_label', 'model_name', 'action']
        widgets = {
            'codename': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'app_label': forms.TextInput(attrs={'class': 'form-control'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control'}),
            'action': forms.Select(attrs={'class': 'form-select'}),
        }
