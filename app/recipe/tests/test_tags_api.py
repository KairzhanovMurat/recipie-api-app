from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Tag, Recipe
from recipe.serializers import TagSerializer
from .test_recipe import create_recipe, create_tag

TAG_URL = reverse('recipe:tag-list')


def get_tag_detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


def create_new_user(email='second@mail.nd', password='test', **kwargs):
    return get_user_model().objects.create_user(email, password, **kwargs)




class TestPublicTagsAPI(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_unauthenticated_request(self):
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateTagsAPI(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_new_user()
        self.client.force_authenticate(self.user)

    def create_tag(self, name: str) -> Tag:
        return Tag.objects.create(user=self.user, name=name)

    def test_get_tags(self):
        self.create_tag('first')
        self.create_tag('second')

        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_single_tag_for_auth_user(self):
        unknown = create_new_user(email='unknown@email.com')
        Tag.objects.create(user=unknown, name='anon')
        tag = self.create_tag('known')
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(res.data))
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_patch_request(self):
        tag = self.create_tag('test_tag')
        patch_data = {'name': 'updated'}
        res = self.client.patch(get_tag_detail_url(tag.id), patch_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, patch_data['name'])

    def test_delete_tag(self):
        tag = self.create_tag('to delete')
        res = self.client.delete(get_tag_detail_url(tag.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(user=self.user).exists())

    def test_assigned_tags_only(self):
        tag1 = create_tag(user=self.user, name='tag1')
        tag2 = create_tag(user=self.user, name='tag2')
        rec = create_recipe(user=self.user)
        rec.tags.add(tag1)
        res = self.client.get(TAG_URL, {
            'assigned_only': 1}
                              )
        self.assertIn(TagSerializer(tag1).data, res.data)
        self.assertNotIn(TagSerializer(tag2).data, res.data)

    def test_assigned_only_unique(self):
        tag1 = create_tag(user=self.user, name='tag1')
        create_tag(user=self.user, name='tag2')
        rec1 = create_recipe(user=self.user)
        rec2 = create_recipe(user=self.user, title='super')
        rec1.tags.add(tag1)
        rec2.tags.add(tag1)
        res = self.client.get(TAG_URL, {
            'assigned_only': 1}
                              )
        self.assertEqual(1, len(res.data))
