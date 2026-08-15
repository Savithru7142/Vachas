from django.urls import path

from . import views

app_name = 'developer'

urlpatterns = [
    path('', views.developer_dashboard, name='dashboard'),
    path('users/', views.DeveloperUsersView.as_view(), name='users'),
    path('users/<int:pk>/edit/', views.developer_edit_user, name='user_edit'),
    path('users/<int:pk>/approve/', views.developer_approve_member, name='user_approve'),
    path('audit-logs/', views.developer_audit_logs, name='audit_logs'),
]
