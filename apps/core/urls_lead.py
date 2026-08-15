from django.urls import path

from apps.accounts.views import ProfileView
from apps.core import views_lead as views
from apps.events.views import (
    LeadEventCreateView,
    LeadEventEditView,
    LeadEventListView,
    LeadEventRegistrationsView,
)
from apps.publications.views import (
    LeadPublicationReviewListView,
    lead_publication_delete,
    lead_publication_quick_status,
    review_publication,
)

app_name = 'lead'

urlpatterns = [
    path('', views.LeadDashboardView.as_view(), name='dashboard'),
    path('members/', views.LeadMembersView.as_view(), name='members'),
    path('members/add/', views.lead_add_user, name='member_add'),
    path('members/<int:pk>/edit/', views.lead_edit_user, name='member_edit'),
    path('members/<int:pk>/approve/', views.lead_approve_member, name='member_approve'),
    path('members/<int:pk>/delete/', views.lead_delete_user, name='member_delete'),
    path('publications/', LeadPublicationReviewListView.as_view(), name='publications'),
    path('publications/<int:pk>/review/', review_publication, name='publication_review'),
    path('publications/<int:pk>/quick-status/<str:status>/', lead_publication_quick_status, name='publication_quick_status'),
    path('publications/<int:pk>/delete/', lead_publication_delete, name='publication_delete'),
    path('announcements/', views.LeadAnnouncementsListView.as_view(), name='announcements'),
    path('announcements/new/', views.lead_announcement_create, name='announcement_create'),
    path('announcements/<int:pk>/edit/', views.lead_announcement_edit, name='announcement_edit'),
    path('announcements/<int:pk>/delete/', views.lead_announcement_delete, name='announcement_delete'),
    path('events/', LeadEventListView.as_view(), name='events'),
    path('events/completed/', views.LeadCompletedEventsView.as_view(), name='events_completed'),
    path('events/new/', LeadEventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/edit/', LeadEventEditView.as_view(), name='event_edit'),
    path('events/<int:pk>/delete/', views.lead_event_delete, name='event_delete'),
    path('events/<int:pk>/registrations/', LeadEventRegistrationsView.as_view(), name='event_registrations'),
    path('gallery/', views.LeadGalleryView.as_view(), name='gallery'),
    path('gallery/upload/', views.LeadGalleryUploadView.as_view(), name='gallery_upload'),
    path('gallery/<int:pk>/edit/', views.lead_gallery_edit, name='gallery_edit'),
    path('contact/', views.LeadContactMessagesView.as_view(), name='contact'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
