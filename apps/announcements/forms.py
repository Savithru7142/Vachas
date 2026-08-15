from django import forms

from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ('title', 'body', 'audience', 'wing', 'is_pinned', 'is_published', 'expires_at')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'v-input'}),
            'body': forms.Textarea(attrs={'class': 'v-input', 'rows': 6}),
            'audience': forms.Select(attrs={'class': 'v-input'}),
            'wing': forms.Select(attrs={'class': 'v-input'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'v-checkbox'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'v-checkbox'}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'v-input', 'type': 'datetime-local'}),
        }
