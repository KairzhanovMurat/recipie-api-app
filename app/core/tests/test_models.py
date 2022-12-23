from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):

    def test_user_model(self):
        email = 'test@email.com'
        password = 'changeme'
        test_user = get_user_model().objects.\
            create_user(email=email, password=password)

        self.assertEqual(test_user.email, email)
        self.assertTrue(test_user.check_password(password))

    def test_normalized_email(self):
        test_emails = [
            ['ezample@mail.COM', 'ezample@mail.com'],
            ['EZAMPLE1@MAIL.com', 'EZAMPLE1@mail.com'],
            ['Ezample2@mail.com', 'Ezample2@mail.com'],
            ['EZAMPLE3@MAIL.COM', 'EZAMPLE3@mail.com'],
        ]
        for email, expected in test_emails:
            user = get_user_model().objects.create_user(email, 'pass')
            self.assertEqual(user.email, expected)

    def test_empty_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email='', password='pass')

    def test_superuser(self):
        user = get_user_model().objects.\
            create_superuser(email='test@test.com', password='123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
