from django.urls import path

from . import views


app_name = 'gallery'

urlpatterns = [
    path('', views.GalleryListView.as_view(), name='list'),
    path(
        'delete/<int:pk>/',
        views.delete_gallery_item,
        name='delete',
    ),
]