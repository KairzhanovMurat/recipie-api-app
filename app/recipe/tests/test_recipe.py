from django.test import TestCase
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from .. import serializers
from core import models

RECIPE_URL = reverse('recipe:recipe-list')


def create_recipe(user, **kwargs):
    defaults = {
        'title': 'sample title',
        'description': 'test desc',
        'time_mins': 5,
        'price': Decimal('5.75'),
        'link': 'https://testlink.com/recipe.pdf'
    }

    defaults.update(kwargs)
    recipe = models.Recipe.objects.create(user=user, **defaults)
    return recipe


class TestPublicRecipeAPI(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_unauthorized_request(self):
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateRecipeAPI(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='testpass'
        )
        self.client.force_authenticate(self.user)

    def test_get_recipes(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = models.Recipes.objects.all().order_by('-id')
        serializer = serializers.RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_limited_recipe_list(self):
        other_user = get_user_model().objects.create_user(
            'second@mail.nd',
            'test')

        create_recipe(user=self.user)
        create_recipe(user=other_user)
        res = self.client.get(RECIPE_URL)
        recipes = models.Recipe.objects.filter(user=self.user)
        serializer = serializers.RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
