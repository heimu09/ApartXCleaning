from rest_framework import serializers
from .models import CustomUser
from django_redis import get_redis_connection
import json

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'avatar', 'phone_number', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует')
        return value


class ConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()
