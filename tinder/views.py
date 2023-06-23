from rest_framework import permissions, status, exceptions, generics, response, viewsets
from rest_framework.response import Response
from django_redis import get_redis_connection
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.mail import send_mail

from random import randint
import json
import os

from .serializers import RegisterSerializer, ConfirmSerializer
from .models import CustomUser


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return CustomUser.objects.none()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        phone_number = serializer.validated_data['phone_number']
        avatar = request.FILES.get('avatar')
        
        if avatar:
            temp_avatar = default_storage.save('tmp/{}'.format(avatar.name), ContentFile(avatar.read()))
            img_url = os.path.join(settings.MEDIA_URL, temp_avatar)

        else:
            return Response({"message": "The avatar is missing."}, status=status.HTTP_400_BAD_REQUEST)

        conn = get_redis_connection("default")
        user_info = {
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'avatar': img_url,
            'phone_number': phone_number
        }
        confirmation_code = str(randint(100000, 999999))
        conn.set(email, json.dumps(user_info), ex=60)
        conn.set(email + '_confirmation_code', confirmation_code, ex=120)
        send_mail('Confirmation code', 'Your confirmation code is {}'.format(confirmation_code), settings.EMAIL_HOST_USER, [email], fail_silently=False)
        
        return Response({"message": "Confirmation code has been sent to your email."}, status=status.HTTP_200_OK)


class ConfirmView(generics.GenericAPIView):
    serializer_class = ConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return CustomUser.objects.none()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        conn = get_redis_connection("default")
        user_info_json = conn.get(email)

        if user_info_json is None:
            return Response({"error": "No registration in progress for this email."}, status=status.HTTP_400_BAD_REQUEST)

        stored_code = conn.get(email + '_confirmation_code')

        if not stored_code:
            return Response({"error": "Confirmation code expired. Please register again."}, status=status.HTTP_400_BAD_REQUEST)

        if str(int(stored_code)) != code:
            return Response({"error": "Confirmation code does not match. Please try again."}, status=status.HTTP_400_BAD_REQUEST)

        user_info = json.loads(user_info_json)  
        user = CustomUser.objects.create_user(email=user_info['email'], password=user_info['password'],
                                              first_name=user_info['first_name'],
                                              last_name=user_info['last_name'], avatar=user_info['avatar'],
                                              phone_number=user_info['phone_number'])
        conn.delete(email)
        conn.delete(email + '_confirmation_code')
        return Response({"message": "Your account has been successfully created."}, status=status.HTTP_201_CREATED)
