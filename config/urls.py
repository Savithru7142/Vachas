from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from apps.core.health import health_check


urlpatterns = [
    path('health/', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('auth/', include('apps.accounts.urls')),
    path('wings/', include('apps.wings.urls')),
    path('events/', include('apps.events.urls')),
    path('gallery/', include('apps.gallery.urls')),
    path('publications/', include(('apps.publications.urls', 'publications'))),
    path('announcements/', include('apps.announcements.urls')),
    path('member/', include('apps.core.urls_member')),
    path('lead/', include('apps.core.urls_lead')),
    path('core-team/', include('apps.core.urls_core')),
    path('developer/', include('apps.developer.urls')),
]

# Serve uploaded media files
urlpatterns += [
    re_path(
        r'^media/(?P<path>.*)$',
        serve,
        {'document_root': settings.MEDIA_ROOT},
    ),
]

admin.site.site_header = 'THE VACHAS Administration'
admin.site.site_title = 'THE VACHAS Admin'