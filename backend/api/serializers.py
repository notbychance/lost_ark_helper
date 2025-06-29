from django.utils import timezone
from rest_framework import serializers
from django.core.exceptions import ValidationError

import os

from .models import *
from .addons.functions import *


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'phone']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data['phone']
        )
        return user


class UserChangePasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, required=True)
    new_password_confirm = serializers.CharField(
        write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['password', 'new_password', 'new_password_confirm']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        # 1. Проверка совпадения нового пароля и подтверждения
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {"new_password_confirm": "Пароли не совпадают"}
            )

        # 2. Валидация сложности нового пароля
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)})

        return attrs

    def update(self, instance, validated_data):
        # Этот метод будет вызван во viewset при save()
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'avatar',
                  'is_leader', 'is_gamer', 'credentials']

    def validate_avatar(self, value):
        # Проверка размера файла (например, не более 2MB)
        max_size = 2 * 1024 * 1024  # 2MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Файл слишком большой. Максимальный размер: {max_size//(1024*1024)}MB")

        # Проверка типа файла
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError(
                "Неподдерживаемый формат файла. Используйте JPG, PNG или GIF")

        return value


class SocialMediaTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaType
        exclude = ['id']


class SocialMediaSerializer(serializers.ModelSerializer):
    type = SocialMediaTypeSerializer(source='media_type', read_only=True)

    class Meta:
        model = SocialMedia
        exclude = ['id']


class GroupCharacterSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    legacy_name = serializers.CharField(
        source='character.name', read_only=True)

    class Meta:
        model = GroupCharacters
        exclude = ['id']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        extra_kwargs = {
            'owner': {'write_only': True},
            'name': {'read_only': True},
            'invitation': {'read_only': True},
        }

    def create(self, validated_data):
        name = generate_unique_name()
        validated_data['name'] = name
        validated_data['invitation'] = generate_invite_code(name)
        return super().create(validated_data)
