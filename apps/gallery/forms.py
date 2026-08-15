from django import forms

from .models import GalleryItem


class GalleryItemForm(forms.ModelForm):
    class Meta:
        model = GalleryItem
        fields = ('title', 'caption', 'image', 'event', 'wing', 'is_public', 'display_order')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'v-input'}),
            'caption': forms.Textarea(attrs={'class': 'v-input', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'v-input'}),
            'event': forms.Select(attrs={'class': 'v-input'}),
            'wing': forms.Select(attrs={'class': 'v-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'v-checkbox'}),
            'display_order': forms.NumberInput(attrs={'class': 'v-input'}),
        }
