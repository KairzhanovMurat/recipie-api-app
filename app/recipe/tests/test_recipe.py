from django.test import TestCase
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from .. import serializers
from core import models

RECIPE_URL = reverse('recipe:recipe-list')


def recipe_detail(res_id):
    return reverse('recipe:recipe-detail', args=[res_id])


def create_new_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


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
        self.user = create_new_user(
            email='test@test.com',
            password='testpass')

        self.client.force_authenticate(self.user)

    def test_get_recipes(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = models.Recipe.objects.all().order_by('-id')
        serializer = serializers.RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_limited_recipe_list(self):
        other_user = create_new_user(
            email='second@mail.nd',
            password='test')

        create_recipe(user=self.user)
        create_recipe(user=other_user)
        res = self.client.get(RECIPE_URL)
        recipes = models.Recipe.objects.filter(user=self.user)
        serializer = serializers.RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_recipe_detail(self):
        recipe = create_recipe(user=self.user)
        url = recipe_detail(recipe.id)
        res = self.client.get(url)
        serializer = serializers.RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        defaults = {
            'title': 'sample title',
            'description': 'test desc',
            'time_mins': 5,
            'price': Decimal('5.75'),
            'link': 'https://testlink.com/recipe.pdf'
        }

        res = self.client.post(RECIPE_URL, defaults)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = models.Recipe.objects.get(id=res.data['id'])
        for key, val in defaults.items():
            self.assertEqual(getattr(recipe, key), val)
        self.assertEqual(recipe.user, self.user)

    def test_patch_request(self):
        orig_link = 'https://testlink.com/recipe.pdf'
        recipe_data = {
            'user': self.user,
            'link': orig_link,
            'title': 'test title'
        }
        recipe = create_recipe(**recipe_data)
        patch_data = {'title': 'new title'}
        res = self.client.patch(recipe_detail(recipe.id), patch_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['link'], orig_link)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, patch_data['title'])
        self.assertEqual(recipe.user, self.user)

    def test_put_request(self):
        recipe = create_recipe(
            user=self.user,
            title='old',
            time_mins=10,
            price=Decimal('3.25'),
        )
        new_recipe_data = {
            'title': 'sample title',
            'description': 'test desc',
            'time_mins': 5,
            'price': Decimal('5.75'),
            'link': 'https://testlink.com/recipe.pdf'
        }
        res = self.client.put(recipe_detail(recipe.id), new_recipe_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key, val in new_recipe_data.items():
            self.assertEqual(getattr(recipe, key), val)
        self.assertEqual(recipe.user, self.user)

    def test_update_recipe_user(self):
        recipe = create_recipe(
            user=self.user,
            title='old',
            time_mins=10,
            price=Decimal('3.25'),
        )
        user = create_new_user(email='new@new.new',
                               password='new')
        patch_data = {'user': user}
        res = self.client.patch(recipe_detail(recipe.id), patch_data)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_del_recipe(self):
        recipe = create_recipe(user=self.user)
        res = self.client.delete(recipe_detail(recipe.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(models.Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_user_recipe(self):
        new_user = create_new_user(email='new@new.new',
                                   password='new')
        recipe = create_recipe(user=new_user)
        res = self.client.delete(recipe_detail(recipe.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(models.Recipe.objects.filter(id=recipe.id))
