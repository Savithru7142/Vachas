"""Central permission helpers for THE VACHAS — Club Lead and Members only."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from apps.accounts.models import ClubMembership


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_audit(request, action, target_model='', target_id='', metadata=None):
    from apps.accounts.models import AuditLog

    AuditLog.objects.create(
        actor=request.user if request.user.is_authenticated else None,
        action=action,
        target_model=target_model,
        target_id=str(target_id),
        ip_address=get_client_ip(request),
        metadata=metadata or {},
    )


def user_has_club_role(user, *roles):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return ClubMembership.Role.LEAD in roles
    if not hasattr(user, 'club_membership') or not user.club_membership.is_active:
        return False
    return user.club_membership.role in roles


def user_can_access_lead_dashboard(user):
    return user_has_club_role(user, ClubMembership.Role.LEAD)


def user_can_access_core_dashboard(user):
    return user_can_access_lead_dashboard(user)


def user_can_review_publications(user):
    return user_can_access_lead_dashboard(user)


def user_can_access_member_dashboard(user):
    return user_has_club_role(user, ClubMembership.Role.MEMBER, ClubMembership.Role.LEAD)


def user_is_club_member(user):
    return user_can_access_member_dashboard(user)


def _lead_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not user_can_access_lead_dashboard(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def _member_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not user_can_access_member_dashboard(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def _core_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not user_can_access_member_dashboard(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


lead_required = _lead_required
member_required = _member_required
core_required = _core_required


class LeadRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not user_can_access_lead_dashboard(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class MemberRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not user_can_access_member_dashboard(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


def user_can_access_developer_dashboard(user):
    if not user.is_authenticated:
        return False
    return user.is_staff or user.is_superuser


def _developer_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not user_can_access_developer_dashboard(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


developer_required = _developer_required


class DeveloperRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not user_can_access_developer_dashboard(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class CoreRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not user_can_access_member_dashboard(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


def get_dashboard_url(user):
    if not user or not user.is_authenticated:
        return 'accounts:login'
    if user.is_lead:
        return 'lead:dashboard'
    if user.is_member:
        return 'member:dashboard'
    return 'core:home'
