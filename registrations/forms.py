from django import forms
from .models import Account, AttachType, Attach, AccountAttach, AccountCondition, AccountNote


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'course', 'student', 'code', 'register_date',
            'course_payment_type', 'course_price', 'course_discount_amount',
            'course_profit_amount', 'course_credit_amount', 'note',
        ]
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.NumberInput(attrs={'class': 'form-control'}),
            'register_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'course_payment_type': forms.Select(attrs={'class': 'form-select'}),
            'course_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'course_discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'course_profit_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'course_credit_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AttachTypeForm(forms.ModelForm):
    class Meta:
        model = AttachType
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AttachForm(forms.ModelForm):
    class Meta:
        model = Attach
        fields = ['attach_type', 'title', 'file_data', 'file_name', 'file_type']
        widgets = {
            'attach_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file_data': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file_name': forms.TextInput(attrs={'class': 'form-control'}),
            'file_type': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AccountAttachForm(forms.ModelForm):
    class Meta:
        model = AccountAttach
        fields = ['account', 'attach']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-select'}),
            'attach': forms.Select(attrs={'class': 'form-select'}),
        }


class AccountConditionForm(forms.ModelForm):
    class Meta:
        model = AccountCondition
        fields = ['account', 'title', 'content', 'fulfilled']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fulfilled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AccountNoteForm(forms.ModelForm):
    class Meta:
        model = AccountNote
        fields = ['account', 'content']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
