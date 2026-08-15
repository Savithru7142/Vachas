from django.test import Client, TestCase
from django.urls import reverse

from apps.accounts.models import ClubMembership, User
from apps.accounts.permissions import get_dashboard_url
from apps.gallery.models import GalleryItem


class PermissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.member = User.objects.create_user('testmember', password='pass')
        ClubMembership.objects.create(user=self.member, role=ClubMembership.Role.MEMBER)
        self.lead = User.objects.create_user('testlead', password='pass')
        ClubMembership.objects.create(user=self.lead, role=ClubMembership.Role.LEAD)
        self.general = User.objects.create_user('general', password='pass')

    def test_member_registration_route_and_role(self):
        payload = {
            'username': 'newmember',
            'first_name': 'New',
            'last_name': 'Member',
            'display_name': 'New Member',
            'email': 'member@example.com',
            'role': ClubMembership.Role.MEMBER,
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = self.client.post(reverse('accounts:register_member'), payload)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newmember')
        self.assertEqual(user.club_membership.role, ClubMembership.Role.MEMBER)

    def test_lead_registration_without_invite_code(self):
        payload = {
            'username': 'newlead',
            'first_name': 'New',
            'last_name': 'Lead',
            'display_name': 'New Lead',
            'email': 'lead@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'role': ClubMembership.Role.LEAD,
        }
        response = self.client.post(reverse('accounts:register'), payload)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newlead')
        self.assertEqual(user.club_membership.role, ClubMembership.Role.LEAD)

    def test_public_member_signup_without_role_field_defaults_to_member(self):
        payload = {
            'username': 'newmember2',
            'first_name': 'Another',
            'last_name': 'Member',
            'display_name': 'Another Member',
            'email': 'member2@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = self.client.post(reverse('accounts:register'), payload)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newmember2')
        self.assertEqual(user.club_membership.role, ClubMembership.Role.MEMBER)

    def test_dashboard_route_for_member_and_lead(self):
        self.assertEqual(get_dashboard_url(self.lead), 'lead:dashboard')
        self.assertEqual(get_dashboard_url(self.member), 'member:dashboard')

    def test_member_cannot_access_lead_dashboard(self):
        self.client.login(username='testmember', password='pass')
        response = self.client.get(reverse('lead:dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_member_can_access_member_dashboard(self):
        self.client.login(username='testmember', password='pass')
        response = self.client.get(reverse('member:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_lead_can_access_lead_dashboard(self):
        self.client.login(username='testlead', password='pass')
        response = self.client.get(reverse('lead:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_lead_members_page_has_add_user_link(self):
        self.client.login(username='testlead', password='pass')
        response = self.client.get(reverse('lead:members'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add User')
        self.assertContains(response, reverse('lead:member_add'))

    def test_lead_can_open_add_user_form(self):
        self.client.login(username='testlead', password='pass')
        response = self.client.get(reverse('lead:member_add'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add User')
        self.assertContains(response, 'Password')

    def test_lead_can_open_gallery_edit_page(self):
        item = GalleryItem.objects.create(
            title='Sample',
            image='gallery/sample.jpg',
            uploaded_by=self.lead,
            is_public=True,
        )
        self.client.login(username='testlead', password='pass')
        response = self.client.get(reverse('lead:gallery_edit', args=[item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Photo')

    def test_public_home_accessible(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_events_list_accessible(self):
        response = self.client.get(reverse('events:list'))
        self.assertEqual(response.status_code, 200)

    def test_gallery_accessible(self):
        response = self.client.get(reverse('gallery:list'))
        self.assertEqual(response.status_code, 200)
