from django.urls import path

from . import views

app_name = 'wings'

urlpatterns = [
    path('', views.WingListView.as_view(), name='list'),
    path('<slug:slug>/', views.wing_detail, name='detail'),
]
