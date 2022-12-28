from django.test import TestCase
from django.contrib.auth import get_user_model
from .. import models
from decimal import Decimal


def create_user(email='test@test.com', password='test', **kwargs):
    return get_user_model().objects.create_user(email, password, **kwargs)


class ModelTest(TestCase):

    def test_user_model(self):
        email = 'test@email.com'
        password = 'changeme'
        test_user = get_user_model().objects. \
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
        user = get_user_model().objects. \
            create_superuser(email='test@test.com', password='123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        user_data = {
            'email': 'test@mail.com',
            'password': 'testpass'
        }

        user = get_user_model().objects.create_user(**user_data)

        recipe = models.Recipe.objects.create(
            user=user,
            title='Title',
            time_mins=5,
            price=Decimal('5.50'),
            description='Test description'
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='test name')
        self.assertEqual(tag.name, str(tag))
