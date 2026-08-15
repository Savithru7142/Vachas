from django import template
from django.urls import NoReverseMatch, reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def dash_url(context, view_name, arg=None):
    """Build dashboard URL using current namespace (member, core_team, lead)."""
    request = context.get('request')
    ns = 'core_team'
    if request and getattr(request, 'resolver_match', None) and request.resolver_match.namespace:
        ns = request.resolver_match.namespace
    if ns not in ('member', 'core_team', 'lead'):
        ns = 'core_team'
    try:
        if arg is not None:
            return reverse(f'{ns}:{view_name}', args=[arg])
        return reverse(f'{ns}:{view_name}')
    except NoReverseMatch:
        return '#'
