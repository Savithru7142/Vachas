from django.urls import path

from apps.accounts.views import ProfileView
from apps.core import views_member as views
from apps.publications.views import (
    MemberSubmissionCreateView,
    MemberSubmissionListView,
    member_submission_detail,
)

app_name = 'member'

urlpatterns = [
    path('', views.MemberDashboardView.as_view(), name='dashboard'),
    path('tasks/', views.MemberTasksView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', views.member_task_update, name='task_detail'),
    path('submissions/', MemberSubmissionListView.as_view(), name='submissions'),
    path('submissions/new/', MemberSubmissionCreateView.as_view(), name='submission_create'),
    path('submissions/<int:pk>/', member_submission_detail, name='submission_detail'),
    path('events/', views.MemberEventsView.as_view(), name='events'),
    path('publications/', views.MemberPublicationsView.as_view(), name='publications'),
    path('announcements/', views.MemberAnnouncementsView.as_view(), name='announcements'),
    path('gallery/', views.MemberGalleryView.as_view(), name='gallery'),
    path('resources/', views.MemberResourcesView.as_view(), name='resources'),
    path('resources/<uuid:uuid>/download/', views.member_resource_download, name='resource_download'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
