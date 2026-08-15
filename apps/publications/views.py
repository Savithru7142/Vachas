from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView

from apps.accounts.permissions import (
    CoreRequiredMixin,
    LeadRequiredMixin,
    MemberRequiredMixin,
    lead_required,
    log_audit,
    member_required,
    user_can_review_publications,
)

from .forms import PublicationForm, PublicationReviewForm
from .models import Publication


class PublicationListView(ListView):
    model = Publication
    template_name = 'publications/list.html'
    context_object_name = 'publications'
    paginate_by = 12

    def get_queryset(self):
        qs = Publication.objects.published().select_related('author', 'wing', 'category')
        wing = self.request.GET.get('wing')
        category = self.request.GET.get('category')
        if wing:
            qs = qs.filter(wing__slug=wing)
        if category:
            qs = qs.filter(category__slug=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.publications.models import PublicationCategory
        from apps.wings.models import Wing
        ctx['wings'] = Wing.objects.filter(is_public=True)
        ctx['categories'] = PublicationCategory.objects.all()
        ctx['current_wing'] = self.request.GET.get('wing', '')
        ctx['current_category'] = self.request.GET.get('category', '')
        return ctx


class PublicationDetailView(DetailView):
    model = Publication
    template_name = 'publications/detail.html'
    context_object_name = 'publication'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Publication.objects.published().select_related('author', 'wing', 'category')


class MemberSubmissionListView(MemberRequiredMixin, ListView):
    model = Publication
    template_name = 'dashboard/member/submissions.html'
    context_object_name = 'submissions'

    def get_queryset(self):
        return Publication.objects.for_author(self.request.user)


class MemberSubmissionCreateView(MemberRequiredMixin, ListView):
    template_name = 'dashboard/member/submission_form.html'

    def get(self, request):
        form = PublicationForm()
        return render(request, self.template_name, {'form': form, 'title': 'New Submission'})

    def post(self, request):
        form = PublicationForm(request.POST, request.FILES)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.author = request.user
            publication.status = Publication.Status.SUBMITTED
            publication.save()
            log_audit(request, 'publication_submitted', 'Publication', publication.pk)
            messages.success(request, 'Your submission has been sent for review.')
            return redirect('member:submissions')
        return render(request, self.template_name, {'form': form, 'title': 'New Submission'})


@member_required
def member_submission_detail(request, pk):
    publication = get_object_or_404(Publication, pk=pk, author=request.user)
    return render(request, 'dashboard/member/submission_detail.html', {'publication': publication})


class LeadPublicationReviewListView(LeadRequiredMixin, ListView):
    model = Publication
    template_name = 'dashboard/lead/publications.html'
    context_object_name = 'publications'

    def get_queryset(self):
        qs = Publication.objects.exclude(status=Publication.Status.DRAFT).select_related('author', 'wing', 'category').order_by('-created_at')
        status_filter = self.request.GET.get('status')
        if status_filter and status_filter.upper() in Publication.Status.values:
            qs = qs.filter(status=status_filter.upper())
        q = self.request.GET.get('q', '').strip()
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(author__username__icontains=q) |
                Q(author__first_name__icontains=q) |
                Q(author__last_name__icontains=q) |
                Q(pen_name__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        base_qs = Publication.objects.exclude(status=Publication.Status.DRAFT)
        ctx['status_filter'] = self.request.GET.get('status', 'ALL').upper()
        ctx['query'] = self.request.GET.get('q', '').strip()
        ctx['count_all'] = base_qs.count()
        ctx['count_submitted'] = base_qs.filter(status=Publication.Status.SUBMITTED).count()
        ctx['count_under_review'] = base_qs.filter(status=Publication.Status.UNDER_REVIEW).count()
        ctx['count_approved'] = base_qs.filter(status=Publication.Status.APPROVED).count()
        ctx['count_published'] = base_qs.filter(status=Publication.Status.PUBLISHED).count()
        ctx['count_rejected'] = base_qs.filter(status=Publication.Status.REJECTED).count()
        return ctx


@lead_required
def review_publication(request, pk):
    publication = get_object_or_404(Publication, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        review_notes = request.POST.get('review_notes', '').strip()

        if action == 'publish':
            publication.status = Publication.Status.PUBLISHED
            if not publication.published_at:
                publication.published_at = timezone.now()
            if review_notes:
                publication.review_notes = review_notes
            publication.reviewed_by = request.user
            publication.save()
            log_audit(request, 'publication_published', 'Publication', publication.pk)
            messages.success(request, f'"{publication.title}" has been published to the site.')
            return redirect('lead:publications')

        elif action == 'approve':
            publication.status = Publication.Status.APPROVED
            if review_notes:
                publication.review_notes = review_notes
            publication.reviewed_by = request.user
            publication.save()
            log_audit(request, 'publication_approved', 'Publication', publication.pk)
            messages.success(request, f'"{publication.title}" has been approved.')
            return redirect('lead:publications')

        elif action == 'under_review':
            publication.status = Publication.Status.UNDER_REVIEW
            if review_notes:
                publication.review_notes = review_notes
            publication.reviewed_by = request.user
            publication.save()
            log_audit(request, 'publication_under_review', 'Publication', publication.pk)
            messages.info(request, f'"{publication.title}" moved to Under Review.')
            return redirect('lead:publications')

        elif action == 'reject':
            publication.status = Publication.Status.REJECTED
            if review_notes:
                publication.review_notes = review_notes
            publication.reviewed_by = request.user
            publication.save()
            log_audit(request, 'publication_rejected', 'Publication', publication.pk)
            messages.warning(request, f'"{publication.title}" has been rejected.')
            return redirect('lead:publications')

        # Fallback to standard form submission
        form = PublicationReviewForm(request.POST, instance=publication)
        if form.is_valid():
            pub = form.save(commit=False)
            pub.reviewed_by = request.user
            if pub.status == Publication.Status.PUBLISHED and not pub.published_at:
                pub.published_at = timezone.now()
            pub.save()
            log_audit(request, f'publication_{pub.status.lower()}', 'Publication', pub.pk)
            messages.success(request, f'Publication marked as {pub.get_status_display()}.')
            from apps.core.dashboard_utils import dash_redirect
            return dash_redirect(request, 'publications')
    else:
        form = PublicationReviewForm(instance=publication)

    return render(request, 'dashboard/lead/publication_review.html', {
        'publication': publication,
        'form': form,
    })


@lead_required
def lead_publication_quick_status(request, pk, status):
    if request.method != 'POST':
        return redirect('lead:publications')

    publication = get_object_or_404(Publication, pk=pk)
    status_map = {
        'publish': Publication.Status.PUBLISHED,
        'approve': Publication.Status.APPROVED,
        'under_review': Publication.Status.UNDER_REVIEW,
        'reject': Publication.Status.REJECTED,
    }

    target_status = status_map.get(status.lower())
    if not target_status:
        messages.error(request, 'Invalid status action.')
        return redirect('lead:publications')

    publication.status = target_status
    publication.reviewed_by = request.user
    if target_status == Publication.Status.PUBLISHED and not publication.published_at:
        publication.published_at = timezone.now()
    publication.save()

    log_audit(request, f'publication_{target_status.lower()}', 'Publication', publication.pk)
    messages.success(request, f'"{publication.title}" status updated to {publication.get_status_display()}.')

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('lead:publications')


@lead_required
def lead_publication_delete(request, pk):
    if request.method != 'POST':
        return redirect('lead:publications')
    publication = get_object_or_404(Publication, pk=pk)
    title = publication.title
    publication.delete()
    log_audit(request, 'publication_deleted', 'Publication', pk)
    messages.success(request, f'Publication "{title}" deleted successfully.')
    return redirect('lead:publications')


# Backward compatibility alias
CorePublicationReviewListView = LeadPublicationReviewListView

