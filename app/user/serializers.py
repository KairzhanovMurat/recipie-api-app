from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['name', 'email', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5
            }
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class TokenAuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_style': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        password = attrs.get('password')
        email = attrs.get('email')
        user = authenticate(
            request=self.context.get('request'),
            password=password,
            email=email
        )
        if not user:
            msg = _('unable to authenticate user with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
