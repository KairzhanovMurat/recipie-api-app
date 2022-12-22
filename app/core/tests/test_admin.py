from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class TestAdmin(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.admin = get_user_model().objects.create_superuser('test@sest.test', '123')
        self.client.force_login(self.admin)
        self.user = get_user_model().objects.create_user('user@user.com', '123')

    def test_list_users(self):
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_edit_user_page(self):
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_add_user(self):
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
