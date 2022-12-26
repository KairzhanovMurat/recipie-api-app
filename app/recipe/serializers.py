from rest_framework import serializers
from core import models


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recipe
        fields = ['id', ' title', 'price', 'time_mins', 'link']
        read_only_fields = ['id']
