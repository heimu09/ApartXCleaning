from rest_framework import serializers
from .models import CustomUser


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

class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email', '')
        password = data.get('password', '')

        if email and password:
            user = CustomUser.objects.filter(email=email).first()
            if user:
                if user.check_password(password):
                    data['user'] = user
                else:
                    msg = 'Unable to login with provided credentials.'
                    raise serializers.ValidationError(msg)
            else:
                msg = 'User not found.'
                raise serializers.ValidationError(msg)
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg)
        return data


class LoginConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()
