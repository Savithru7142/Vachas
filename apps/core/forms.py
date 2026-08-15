from django import forms

from .models import Achievement, ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'subject', 'message')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'v-input'}),
            'email': forms.EmailInput(attrs={'class': 'v-input'}),
            'subject': forms.TextInput(attrs={'class': 'v-input'}),
            'message': forms.Textarea(attrs={'class': 'v-input', 'rows': 6}),
        }


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ('title', 'description', 'year', 'image', 'is_public', 'display_order')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'v-input'}),
            'description': forms.Textarea(attrs={'class': 'v-input', 'rows': 4}),
            'year': forms.NumberInput(attrs={'class': 'v-input'}),
            'image': forms.FileInput(attrs={'class': 'v-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'v-checkbox'}),
            'display_order': forms.NumberInput(attrs={'class': 'v-input'}),
        }
