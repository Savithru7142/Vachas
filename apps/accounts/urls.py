from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.VachasLoginView.as_view(), name='login'),
    path('logout/', views.VachasLogoutView.as_view(), name='logout'),
    path('register/', views.MemberRegisterView.as_view(), name='register'),
    path('register/member/', views.MemberRegisterView.as_view(), name='register_member'),
    path('register/lead/', views.LeadRegisterView.as_view(), name='register_lead'),
    path('profile/', views.profile_redirect, name='profile'),
    path('my-profile/', views.ProfileView.as_view(), name='my_profile'),
    path('password-reset/', views.VachasPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.VachasPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.VachasPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.VachasPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
