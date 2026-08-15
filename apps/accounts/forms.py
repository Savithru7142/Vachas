from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import ClubMembership, Profile, User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'v-input',
            'placeholder': 'Username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'v-input',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })
    )


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        label='First name',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'v-input', 'placeholder': 'Your first name'}),
    )
    last_name = forms.CharField(
        label='Last name',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'v-input', 'placeholder': 'Your last name'}),
    )
    display_name = forms.CharField(
        label='Display name',
        max_length=150,
        required=True,
        help_text='How your name appears on the site.',
        widget=forms.TextInput(attrs={'class': 'v-input', 'placeholder': 'Name shown publicly'}),
    )
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'v-input', 'placeholder': 'you@example.com'}),
    )
    role = forms.ChoiceField(
        label='Account type',
        choices=ClubMembership.Role.choices,
        initial=ClubMembership.Role.MEMBER,
        required=False,
        widget=forms.Select(attrs={'class': 'v-input'}),
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'display_name', 'email', 'role', 'password1', 'password2')

    def __init__(self, *args, role=None, **kwargs):
        self.role = role or ClubMembership.Role.MEMBER
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'v-input', 'placeholder': 'Choose a username'})
        self.fields['password1'].widget.attrs.update({'class': 'v-input'})
        self.fields['password2'].widget.attrs.update({'class': 'v-input'})
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm password'
        self.fields['role'].initial = self.role

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        selected_role = self.cleaned_data.get('role') or self.role or ClubMembership.Role.MEMBER
        if commit:
            user.save()
            Profile.objects.update_or_create(
                user=user,
                defaults={'display_name': self.cleaned_data['display_name']},
            )
            ClubMembership.objects.update_or_create(
                user=user,
                defaults={
                    'role': selected_role,
                    'is_active': True,
                },
            )
        return user


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'v-input'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'v-input'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'v-input'}))

    class Meta:
        model = Profile
        fields = ('display_name', 'bio', 'pen_name', 'phone', 'avatar')
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'v-input'}),
            'bio': forms.Textarea(attrs={'class': 'v-input', 'rows': 4}),
            'pen_name': forms.TextInput(attrs={'class': 'v-input'}),
            'phone': forms.TextInput(attrs={'class': 'v-input'}),
            'avatar': forms.FileInput(attrs={'class': 'v-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.user.first_name
        self.fields['last_name'].initial = self.user.last_name
        self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.email = self.cleaned_data['email']
        self.user.save()
        profile.user = self.user
        if commit:
            profile.save()
        return profile


class UserAccountForm(forms.Form):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'v-input'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'v-input'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'v-input'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'v-input'}))
    display_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'v-input'}))
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'v-input', 'rows': 3}))
    pen_name = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={'class': 'v-input'}))
    phone = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={'class': 'v-input'}))
    role = forms.ChoiceField(choices=ClubMembership.Role.choices, widget=forms.Select(attrs={'class': 'v-input'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'v-checkbox'}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'v-input', 'rows': 2}))
    new_password = forms.CharField(
        required=False,
        label='New password',
        help_text='Leave blank to keep the current password.',
        widget=forms.PasswordInput(attrs={'class': 'v-input', 'autocomplete': 'new-password'}),
    )

    def __init__(self, *args, user=None, editor=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        profile = getattr(user, 'profile', None)
        membership = getattr(user, 'club_membership', None)
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
        self.fields['email'].initial = user.email
        self.fields['username'].initial = user.username
        if profile:
            self.fields['display_name'].initial = profile.display_name
            self.fields['bio'].initial = profile.bio
            self.fields['pen_name'].initial = profile.pen_name
            self.fields['phone'].initial = profile.phone
        if membership:
            self.fields['role'].initial = membership.role
            self.fields['is_active'].initial = membership.is_active
            self.fields['notes'].initial = membership.notes
        else:
            self.fields['role'].initial = ClubMembership.Role.MEMBER
            self.fields['is_active'].initial = False

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.exclude(pk=self.user.pk).filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(pk=self.user.pk).filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def save(self, appointed_by):
        user = self.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        user.save()

        profile, _ = Profile.objects.get_or_create(user=user)
        profile.display_name = self.cleaned_data['display_name']
        profile.bio = self.cleaned_data.get('bio', '')
        profile.pen_name = self.cleaned_data.get('pen_name', '')
        profile.phone = self.cleaned_data.get('phone', '')
        profile.save()

        membership, _ = ClubMembership.objects.get_or_create(
            user=user,
            defaults={'role': ClubMembership.Role.MEMBER, 'is_active': False},
        )
        membership.role = self.cleaned_data['role']
        membership.is_active = self.cleaned_data['is_active']
        membership.notes = self.cleaned_data.get('notes', '')
        membership.appointed_by = appointed_by
        membership.save()
        return user


LeadUserAccountForm = UserAccountForm
