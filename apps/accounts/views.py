from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView

from apps.accounts.models import ClubMembership
from apps.accounts.permissions import get_dashboard_url, log_audit

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import Profile, User


class VachasLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy(get_dashboard_url(self.request.user))

    def form_valid(self, form):
        response = super().form_valid(form)
        log_audit(self.request, 'login_success', 'User', self.request.user.pk)
        return response


class VachasLogoutView(LogoutView):
    next_page = reverse_lazy('core:home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            log_audit(request, 'logout', 'User', request.user.pk)
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('core:home')
    account_role = None
    account_label = 'Account'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(get_dashboard_url(request.user))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['role'] = self.account_role
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account_label'] = self.account_label
        context['account_type'] = self.account_role
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        role_label = 'Lead' if self.object.club_membership and self.object.club_membership.role == ClubMembership.Role.LEAD else 'Member'
        messages.success(
            self.request,
            f'Welcome to THE VACHAS! Your {role_label.lower()} account is ready.',
        )
        log_audit(self.request, 'register', 'User', self.object.pk)
        return response


class MemberRegisterView(RegisterView):
    account_role = ClubMembership.Role.MEMBER
    account_label = 'Member'


class LeadRegisterView(RegisterView):
    account_role = ClubMembership.Role.LEAD
    account_label = 'Lead'


class ProfileView(UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        if self.request.user.is_lead:
            return ['accounts/profile_lead.html']
        return ['accounts/my_profile.html']

    def get_success_url(self):
        if self.request.user.is_lead:
            return reverse('lead:profile')
        return reverse('accounts:my_profile')

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)


def profile_redirect(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if request.user.is_lead:
        return redirect('lead:profile')
    return redirect('accounts:my_profile')


class VachasPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')


class VachasPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class VachasPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class VachasPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
