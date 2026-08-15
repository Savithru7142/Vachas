from django import forms

from .models import Resource


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ('title', 'description', 'file', 'audience', 'wing')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'v-input'}),
            'description': forms.Textarea(attrs={'class': 'v-input', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'v-input'}),
            'audience': forms.Select(attrs={'class': 'v-input'}),
            'wing': forms.Select(attrs={'class': 'v-input'}),
        }
