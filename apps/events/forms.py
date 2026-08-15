from django import forms

from .models import Event, EventRegistration


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            'title', 'description', 'date', 'start_time', 'end_time', 'venue',
            'wing', 'poster', 'rules', 'capacity', 'registration_deadline',
            'status', 'is_public',
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'v-input'}),
            'description': forms.Textarea(attrs={'class': 'v-input', 'rows': 6}),
            'date': forms.DateInput(attrs={'class': 'v-input', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'v-input', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'v-input', 'type': 'time'}),
            'venue': forms.TextInput(attrs={'class': 'v-input'}),
            'wing': forms.Select(attrs={'class': 'v-input'}),
            'poster': forms.FileInput(attrs={'class': 'v-input'}),
            'rules': forms.Textarea(attrs={'class': 'v-input', 'rows': 4}),
            'capacity': forms.NumberInput(attrs={'class': 'v-input'}),
            'registration_deadline': forms.DateTimeInput(attrs={'class': 'v-input', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'v-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'v-checkbox'}),
        }


class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ('guest_name', 'guest_email')
        widgets = {
            'guest_name': forms.TextInput(attrs={'class': 'v-input'}),
            'guest_email': forms.EmailInput(attrs={'class': 'v-input'}),
        }
