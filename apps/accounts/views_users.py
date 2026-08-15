from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.forms import UserAccountForm
from apps.accounts.models import ClubMembership, User
from apps.accounts.permissions import log_audit
from apps.accounts.user_management import (
    can_edit_user,
    filter_users_queryset,
    users_list_context,
    validate_user_account_save,
)


class ManagedUsersListMixin:
    model = User
    context_object_name = 'users'

    def get_queryset(self):
        return filter_users_queryset(self.request)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(users_list_context(self.request))
        return ctx


def edit_managed_user(request, pk, *, members_url, dashboard_base):
    user = get_object_or_404(User.objects.select_related('profile', 'club_membership'), pk=pk)
    if not can_edit_user(request.user, user):
        raise PermissionDenied

    if request.method == 'POST':
        form = UserAccountForm(request.POST, user=user, editor=request.user)
        if form.is_valid():
            error = validate_user_account_save(request.user, user, form.cleaned_data)
            if error:
                messages.error(request, error)
            else:
                form.save(appointed_by=request.user)
                log_audit(request, 'user_account_updated', 'User', user.pk)
                messages.success(request, f'Updated account for {user.display_name}.')
                return redirect(members_url)
    else:
        form = UserAccountForm(user=user, editor=request.user)

    return render(request, 'dashboard/shared/user_edit.html', {
        'form': form,
        'edit_user': user,
        'members_url': members_url,
        'dashboard_base': dashboard_base,
    })


def approve_managed_user(request, pk, *, members_url):
    user = get_object_or_404(User, pk=pk)
    if not can_edit_user(request.user, user):
        raise PermissionDenied
    if request.method == 'POST':
        membership, _ = ClubMembership.objects.get_or_create(
            user=user,
            defaults={'role': ClubMembership.Role.MEMBER, 'is_active': False},
        )
        membership.is_active = True
        membership.appointed_by = request.user
        membership.save()
        log_audit(request, 'membership_approved', 'ClubMembership', membership.pk)
        messages.success(request, f'Approved {user.display_name} as a member.')
    return redirect(members_url)
