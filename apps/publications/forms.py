from django import forms

from .models import Publication


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ('title', 'pen_name', 'wing', 'category', 'content', 'excerpt', 'cover_image', 'tags')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'v-input'}),
            'pen_name': forms.TextInput(attrs={'class': 'v-input'}),
            'wing': forms.Select(attrs={'class': 'v-input'}),
            'category': forms.Select(attrs={'class': 'v-input'}),
            'content': forms.Textarea(attrs={'class': 'v-input', 'rows': 16}),
            'excerpt': forms.Textarea(attrs={'class': 'v-input', 'rows': 3}),
            'cover_image': forms.FileInput(attrs={'class': 'v-input'}),
            'tags': forms.TextInput(attrs={'class': 'v-input', 'placeholder': 'poetry, telugu, love'}),
        }


class PublicationReviewForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ('status', 'review_notes')
        widgets = {
            'status': forms.Select(attrs={'class': 'v-input'}),
            'review_notes': forms.Textarea(attrs={'class': 'v-input', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            (Publication.Status.UNDER_REVIEW, 'Under Review'),
            (Publication.Status.APPROVED, 'Approved'),
            (Publication.Status.REJECTED, 'Rejected'),
            (Publication.Status.PUBLISHED, 'Published'),
        ]
