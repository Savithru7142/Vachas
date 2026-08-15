from django import forms

from .models import Wing


class WingForm(forms.ModelForm):
    class Meta:
        model = Wing
        fields = (
            'name', 'slug', 'wing_type', 'language_code', 'description',
            'excerpt', 'coordinator', 'is_public', 'display_order',
        )
        widgets = {
            'name': forms.TextInput(attrs={'class': 'v-input'}),
            'slug': forms.TextInput(attrs={'class': 'v-input'}),
            'wing_type': forms.Select(attrs={'class': 'v-input'}),
            'language_code': forms.TextInput(attrs={'class': 'v-input'}),
            'description': forms.Textarea(attrs={'class': 'v-input', 'rows': 4}),
            'excerpt': forms.TextInput(attrs={'class': 'v-input'}),
            'coordinator': forms.Select(attrs={'class': 'v-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'v-checkbox'}),
            'display_order': forms.NumberInput(attrs={'class': 'v-input'}),
        }
