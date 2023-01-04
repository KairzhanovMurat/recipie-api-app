from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Ingredient
from recipe.serializers import IngredientSerializer
from .test_recipe import create_recipe

ING_URL = reverse('recipe:ingredient-list')


def get_ing_detail_url(ing_id):
    return reverse('recipe:ingredient-detail', args=[ing_id])


def create_new_user(email='second@mail.nd', password='test', **kwargs):
    return get_user_model().objects.create_user(email, password, **kwargs)


class TestPublicIngredientsAPI(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_unauthenticated_request(self):
        res = self.client.get(ING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateTagsAPI(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_new_user()
        self.client.force_authenticate(self.user)

    def create_ing(self, name: str) -> Ingredient:
        return Ingredient.objects.create(user=self.user, name=name)

    def test_get_tags(self):
        self.create_ing('first')
        self.create_ing('second')

        res = self.client.get(ING_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ings = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ings, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_single_tag_for_auth_user(self):
        unknown = create_new_user(email='unknown@email.com')
        Ingredient.objects.create(user=unknown, name='anon')
        ing = self.create_ing('known')
        res = self.client.get(ING_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(res.data))
        self.assertEqual(res.data[0]['name'], ing.name)
        self.assertEqual(res.data[0]['id'], ing.id)

    def test_patch_request(self):
        tag = self.create_ing('test_ing')
        patch_data = {'name': 'updated'}
        res = self.client.patch(get_ing_detail_url(tag.id), patch_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, patch_data['name'])

    def test_delete_ing(self):
        ing = self.create_ing('to delete')
        res = self.client.delete(get_ing_detail_url(ing.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(user=self.user).exists())

    def test_assigned_ingredients_only(self):
        ing1 = self.create_ing(name='ing1')
        ing2 = self.create_ing(name='ing2')
        rec = create_recipe(user=self.user)
        rec.ingredients.add(ing1)
        res = self.client.get(ING_URL, {
            'assigned_only': 1}
                              )
        self.assertIn(IngredientSerializer(ing1).data, res.data)
        self.assertNotIn(IngredientSerializer(ing2).data, res.data)

    def test_assigned_only_unique(self):
        ing1 = self.create_ing(name='ing1')
        self.create_ing(name='ing2')
        rec1 = create_recipe(user=self.user)
        rec2 = create_recipe(user=self.user, title='super')
        rec1.ingredients.add(ing1)
        rec2.ingredients.add(ing1)
        res = self.client.get(ING_URL, {
            'assigned_only': 1}
                              )
        self.assertEqual(1, len(res.data))
