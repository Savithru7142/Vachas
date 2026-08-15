from django.urls import path

from apps.accounts.views import ProfileView
from apps.core import views_core as views
from apps.events.views import CoreEventCreateView, CoreEventEditView, CoreEventListView
from apps.publications.views import CorePublicationReviewListView, review_publication

app_name = 'core_team'

urlpatterns = [
    path('', views.CoreDashboardView.as_view(), name='dashboard'),
    path('members/', views.CoreMembersView.as_view(), name='members'),
    path('members/<int:pk>/edit/', views.core_edit_user, name='member_edit'),
    path('members/<int:pk>/approve/', views.core_approve_member, name='member_approve'),
    path('tasks/', views.CoreTasksView.as_view(), name='tasks'),
    path('tasks/new/', views.CoreTaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/edit/', views.core_task_edit, name='task_edit'),
    path('events/', CoreEventListView.as_view(), name='events'),
    path('events/new/', CoreEventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/edit/', CoreEventEditView.as_view(), name='event_edit'),
    path('publications/', CorePublicationReviewListView.as_view(), name='publications'),
    path('publications/<int:pk>/review/', review_publication, name='publication_review'),
    path('announcements/', views.CoreAnnouncementsView.as_view(), name='announcements'),
    path('announcements/new/', views.CoreAnnouncementCreateView.as_view(), name='announcement_create'),
    path('resources/', views.CoreResourcesView.as_view(), name='resources'),
    path('resources/upload/', views.CoreResourceUploadView.as_view(), name='resource_upload'),
    path('gallery/', views.CoreGalleryView.as_view(), name='gallery'),
    path('gallery/upload/', views.CoreGalleryUploadView.as_view(), name='gallery_upload'),
    path('achievements/', views.CoreAchievementsView.as_view(), name='achievements'),
    path('achievements/new/', views.CoreAchievementCreateView.as_view(), name='achievement_create'),
    path('analytics/', views.CoreAnalyticsView.as_view(), name='analytics'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
