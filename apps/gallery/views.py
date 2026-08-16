from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView

from .models import GalleryItem


class GalleryListView(ListView):
    model = GalleryItem
    template_name = 'gallery/list.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_queryset(self):
        return GalleryItem.objects.filter(is_public=True)


@login_required
def delete_gallery_item(request, pk):
    if request.method != 'POST':
        return redirect('gallery:list')

    item = get_object_or_404(GalleryItem, pk=pk)

    # Delete the image from Cloudinary/storage first
    if item.image:
        item.image.delete(save=False)

    # Delete the database record
    item.delete()

    messages.success(request, 'Gallery photo deleted successfully.')

    # Change this redirect if your dashboard uses a different URL name
    return redirect('lead:gallery')