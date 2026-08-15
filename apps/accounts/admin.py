from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserCreationForm

from .models import AuditLog, ClubMembership, Profile, User


class UserCreationWithRoleForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=ClubMembership.Role.choices,
        initial=ClubMembership.Role.MEMBER,
        required=True,
        label='Club role',
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_form = UserCreationWithRoleForm
    list_display = ('username', 'email', 'is_developer', 'is_staff', 'is_active', 'club_role_display')
    list_filter = ('is_developer', 'is_staff', 'is_active')
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('System Access', {'fields': ('is_developer',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    def club_role_display(self, obj):
        membership = getattr(obj, 'club_membership', None)
        if membership:
            return membership.get_role_display()
        return 'No role'
    club_role_display.short_description = 'Club Role'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        role = form.cleaned_data.get('role') or ClubMembership.Role.MEMBER
        membership, _ = ClubMembership.objects.get_or_create(user=obj)
        membership.role = role
        membership.is_active = True
        membership.save()


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'pen_name')
    search_fields = ('user__username', 'display_name', 'pen_name')


@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_active', 'appointed_at')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'actor', 'target_model', 'created_at')
    list_filter = ('action', 'target_model')
    readonly_fields = ('actor', 'action', 'target_model', 'target_id', 'ip_address', 'metadata', 'created_at')
