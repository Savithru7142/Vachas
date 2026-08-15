from django.shortcuts import redirect


def dashboard_namespace(request):
    ns = 'core_team'
    if getattr(request, 'resolver_match', None) and request.resolver_match.namespace:
        ns = request.resolver_match.namespace
    if ns not in ('member', 'core_team', 'lead'):
        ns = 'core_team'
    return ns


def dash_redirect(request, view_name, *args):
    ns = dashboard_namespace(request)
    if args:
        return redirect(f'{ns}:{view_name}', *args)
    return redirect(f'{ns}:{view_name}')
