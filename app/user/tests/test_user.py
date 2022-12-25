from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**kwargs):
    return get_user_model().objects.create(**kwargs)


class TestUser(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_user(self):
        data = {
            'name': 'Arlan',
            'email': 'arlan@mail.ru',
            'password': 'changeme'
        }
        res = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=data['email'])
        self.assertTrue(user.check_password(data['password']))
        self.assertNotIn('password', res.data)

    def test_already_exists(self):
        data = {
            'name': 'Arlan',
            'email': 'arlan@mail.ru',
            'password': 'changeme'
        }
        create_user(**data)
        res = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_too_short_pass(self):
        data = {
            'name': 'Arlan',
            'email': 'arlan@mail.ru',
            'password': 'c'
        }
        self.client.post(CREATE_USER_URL, data)
        exists = get_user_model().objects.filter(email=data['email']).exists()
        self.assertFalse(exists)

    # def test_create_token(self):
    #     user_details = {
    #         'name': 'Test name',
    #         'email': 'test@example.com',
    #         'password': 'test-user-password123'
    #     }
    #
    #     create_user(**user_details)
    #
    #     payload = {
    #         'email': user_details['email'],
    #         'password': user_details['password'],
    #     }
    #
    #     res = self.client.post(TOKEN_URL, payload)
    #
    #     self.assertIn('token', res.data)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_invalid_pass(self):
        data = {
            'name': 'Arlan',
            'email': 'arlan@mail.ru',
            'password': 'changeme'
        }

        create_user(**data)

        credentials_for_token = {
            'email': data['email'],
            'password': 'invalid'
        }
        res = self.client.post(TOKEN_URL, credentials_for_token)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_pass(self):
        credentials_for_token = {
            'email': 'arlan@mail.ru',
            'password': ''
        }

        res = self.client.post(TOKEN_URL, credentials_for_token)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_unauthorized(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITest(TestCase):

    def setUp(self) -> None:
        self.user = create_user(
            name='test',
            email='test@email.com',
            password='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_success_get_data(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.data, {'name': self.user.name,
                                    'email': self.user.email})

    def test_not_allowed(self):
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # def test_update(self):
    #     new_data = {
    #         'name': 'new name',
    #         'password': 'new_pass',
    #     }
    #
    #     res = self.client.patch(ME_URL, new_data)
    #     self.user.refresh_from_db()
    #     self.assertEqual(self.user.name, new_data['name'])
    #     self.assertTrue(self.user.check_password(new_data['password']))
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)

