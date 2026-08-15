from django.views.generic import ListView

from .models import GalleryItem


class GalleryListView(ListView):
    model = GalleryItem
    template_name = 'gallery/list.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_queryset(self):
        return GalleryItem.objects.filter(is_public=True)
