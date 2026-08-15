from django import forms

from apps.accounts.models import User

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'wing', 'priority', 'deadline', 'status', 'assigned_to', 'attachment')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'v-input'}),
            'description': forms.Textarea(attrs={'class': 'v-input', 'rows': 4}),
            'wing': forms.Select(attrs={'class': 'v-input'}),
            'priority': forms.Select(attrs={'class': 'v-input'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'v-input', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'v-input'}),
            'assigned_to': forms.Select(attrs={'class': 'v-input'}),
            'attachment': forms.FileInput(attrs={'class': 'v-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(
            club_membership__is_active=True
        )


class TaskStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('status',)
        widgets = {'status': forms.Select(attrs={'class': 'v-input'})}
