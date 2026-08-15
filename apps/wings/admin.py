from django.contrib import admin

from .models import Wing, WingMembership


class WingMembershipInline(admin.TabularInline):
    model = WingMembership
    extra = 0


@admin.register(Wing)
class WingAdmin(admin.ModelAdmin):
    list_display = ('name', 'wing_type', 'language_code', 'is_public', 'display_order')
    list_filter = ('wing_type', 'is_public')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [WingMembershipInline]


@admin.register(WingMembership)
class WingMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'wing', 'role_in_wing', 'joined_at')
    list_filter = ('wing', 'role_in_wing')
