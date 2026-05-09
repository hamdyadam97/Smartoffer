from django import forms
from .models import StudentOffer, OfferRecipient, OfferNote


class StudentOfferForm(forms.ModelForm):
    class Meta:
        model = StudentOffer
        exclude = ['created_by', 'created_at', 'updated_at', 'sent_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'target_level': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class OfferRecipientForm(forms.ModelForm):
    class Meta:
        model = OfferRecipient
        exclude = ['sent_at', 'opened_at', 'interacted_at']
        widgets = {
            'offer': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'channel': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class OfferNoteForm(forms.ModelForm):
    class Meta:
        model = OfferNote
        exclude = ['person', 'created_at']
        widgets = {
            'offer': forms.Select(attrs={'class': 'form-select'}),
            'note_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
