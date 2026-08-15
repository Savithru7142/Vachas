from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import ClubMembership, User
from apps.publications.models import Publication, PublicationCategory
from apps.wings.models import Wing


class PublicationReviewWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Member user
        self.member = User.objects.create_user(
            username='author_member',
            password='password123',
            first_name='Author',
            last_name='Member',
        )
        ClubMembership.objects.create(user=self.member, role=ClubMembership.Role.MEMBER, is_active=True)

        # Lead user
        self.lead = User.objects.create_user(
            username='club_lead',
            password='password123',
            first_name='Club',
            last_name='Lead',
        )
        ClubMembership.objects.create(user=self.lead, role=ClubMembership.Role.LEAD, is_active=True)

        # Wing & Category
        self.wing = Wing.objects.create(name='Poetry Wing', slug='poetry-wing', is_public=True)
        self.category = PublicationCategory.objects.create(name='Poem', slug='poem')

    def test_member_submission_flow(self):
        self.client.login(username='author_member', password='password123')
        
        # Member creates submission
        response = self.client.post(reverse('member:submission_create'), {
            'title': 'Whispers of Dawn',
            'pen_name': 'PoeticSoul',
            'wing': self.wing.pk,
            'category': self.category.pk,
            'content': 'The morning sun awakens the sleepy valleys.\nA gentle breeze whispers hope.',
            'excerpt': 'The morning sun awakens the sleepy valleys.',
            'tags': 'dawn, poetry, sunrise',
        })
        self.assertEqual(response.status_code, 302)
        
        pub = Publication.objects.get(title='Whispers of Dawn')
        self.assertEqual(pub.status, Publication.Status.SUBMITTED)
        self.assertEqual(pub.author, self.member)
        self.assertEqual(pub.pen_name, 'PoeticSoul')

        # Member sees it in submission list
        list_response = self.client.get(reverse('member:submissions'))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, 'Whispers of Dawn')
        self.assertContains(list_response, 'Submitted')

    def test_lead_dashboard_visibility_and_review(self):
        pub = Publication.objects.create(
            title='Echoes of Silence',
            author=self.member,
            pen_name='SilentEcho',
            wing=self.wing,
            category=self.category,
            content='Words unspoken echo through the chambers of thought.',
            status=Publication.Status.SUBMITTED,
        )

        self.client.login(username='club_lead', password='password123')

        # 1. Lead Dashboard home shows pending submission
        dash_response = self.client.get(reverse('lead:dashboard'))
        self.assertEqual(dash_response.status_code, 200)
        self.assertContains(dash_response, 'Echoes of Silence')
        self.assertContains(dash_response, 'Submissions & Publications')
        self.assertContains(dash_response, reverse('lead:publications'))

        # 2. Lead Publications review list shows the submission
        pub_list_response = self.client.get(reverse('lead:publications'))
        self.assertEqual(pub_list_response.status_code, 200)
        self.assertContains(pub_list_response, 'Echoes of Silence')
        self.assertContains(pub_list_response, 'SilentEcho')
        self.assertContains(pub_list_response, 'Submitted')

        # 3. Filter by status
        filter_sub_response = self.client.get(reverse('lead:publications') + '?status=SUBMITTED')
        self.assertEqual(filter_sub_response.status_code, 200)
        self.assertContains(filter_sub_response, 'Echoes of Silence')

        # 4. Lead opens review page
        review_page_response = self.client.get(reverse('lead:publication_review', args=[pub.pk]))
        self.assertEqual(review_page_response.status_code, 200)
        self.assertContains(review_page_response, 'Echoes of Silence')
        self.assertContains(review_page_response, 'Words unspoken echo')
        self.assertContains(review_page_response, 'Accept & Publish')

        # 5. Lead accepts and publishes the submission
        review_post_response = self.client.post(reverse('lead:publication_review', args=[pub.pk]), {
            'action': 'publish',
            'review_notes': 'Beautiful piece of writing! Approved for public display.',
        })
        self.assertEqual(review_post_response.status_code, 302)

        pub.refresh_from_db()
        self.assertEqual(pub.status, Publication.Status.PUBLISHED)
        self.assertIsNotNone(pub.published_at)
        self.assertEqual(pub.reviewed_by, self.lead)
        self.assertEqual(pub.review_notes, 'Beautiful piece of writing! Approved for public display.')

    def test_quick_status_actions(self):
        pub = Publication.objects.create(
            title='Midnight Reflections',
            author=self.member,
            content='Thoughts under the moonlit sky.',
            status=Publication.Status.SUBMITTED,
        )

        self.client.login(username='club_lead', password='password123')

        # Quick approve
        response = self.client.post(reverse('lead:publication_quick_status', args=[pub.pk, 'approve']))
        self.assertEqual(response.status_code, 302)
        pub.refresh_from_db()
        self.assertEqual(pub.status, Publication.Status.APPROVED)
        self.assertEqual(pub.reviewed_by, self.lead)

        # Quick publish
        response = self.client.post(reverse('lead:publication_quick_status', args=[pub.pk, 'publish']))
        self.assertEqual(response.status_code, 302)
        pub.refresh_from_db()
        self.assertEqual(pub.status, Publication.Status.PUBLISHED)
        self.assertIsNotNone(pub.published_at)

        # Quick reject
        response = self.client.post(reverse('lead:publication_quick_status', args=[pub.pk, 'reject']))
        self.assertEqual(response.status_code, 302)
        pub.refresh_from_db()
        self.assertEqual(pub.status, Publication.Status.REJECTED)

    def test_public_and_member_visibility_after_publish(self):
        pub = Publication.objects.create(
            title='Spring Blossoms',
            author=self.member,
            pen_name='BloomWriter',
            wing=self.wing,
            category=self.category,
            content='Flowers bloom in vibrant colors across the hills.',
            excerpt='Flowers bloom in vibrant colors.',
            status=Publication.Status.PUBLISHED,
            published_at=timezone.now(),
            reviewed_by=self.lead,
        )

        # Public list & detail
        pub_response = self.client.get(reverse('publications:list'))
        self.assertEqual(pub_response.status_code, 200)
        self.assertContains(pub_response, 'Spring Blossoms')

        detail_response = self.client.get(reverse('publications:detail', args=[pub.slug]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'Spring Blossoms')
        self.assertContains(detail_response, 'Flowers bloom in vibrant colors')

        # Member list
        self.client.login(username='author_member', password='password123')
        member_response = self.client.get(reverse('member:submissions'))
        self.assertEqual(member_response.status_code, 200)
        self.assertContains(member_response, 'Spring Blossoms')
        self.assertContains(member_response, 'Published')
