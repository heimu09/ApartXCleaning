from rest_framework import permissions, status, exceptions, generics, response, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_redis import get_redis_connection
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.mail import send_mail

from random import randint
import json
import os

from .serializers import RegisterSerializer, ConfirmSerializer, LoginConfirmSerializer, LoginRequestSerializer
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
        print(avatar)
        
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
        conn.set(email, json.dumps(user_info), ex=86400)
        conn.set(email + '_confirmation_code', confirmation_code, ex=120)
        send_mail('Confirmation code', 'Your confirmation code is {}'.format(confirmation_code), settings.EMAIL_HOST_USER, [email], fail_silently=False)
        
        return Response({"message": "Confirmation code has been sent to your email."}, status=status.HTTP_200_OK)


class ConfirmRegisterView(generics.GenericAPIView):
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
        
        temp_path = os.path.join(settings.MEDIA_ROOT, 'tmp/{}'.format(os.path.basename(user_info['avatar'])))
        new_path = os.path.join(settings.MEDIA_ROOT, 'user/avatar/{}'.format(os.path.basename(user_info['avatar'])))
        print(temp_path, new_path, user_info['avatar'])
        os.rename(temp_path, new_path)

        user_info['avatar'] = 'user/avatar/{}'.format(os.path.basename(user_info['avatar']))

        user = CustomUser.objects.create_user(email=user_info['email'], password=user_info['password'],
                                              first_name=user_info['first_name'],
                                              last_name=user_info['last_name'], avatar=user_info['avatar'],
                                              phone_number=user_info['phone_number'])
        conn.delete(email)
        conn.delete(email + '_confirmation_code')
        return Response({"message": "Your account has been successfully created."}, status=status.HTTP_201_CREATED)


class RequestLoginView(generics.GenericAPIView):
    serializer_class = LoginRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = CustomUser.objects.get(email=email)
            if not user.check_password(password):
                return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        conn = get_redis_connection("default")
        login_code = str(randint(100000, 999999))
        conn.set(email + '_login_code', login_code, ex=120)
        send_mail('Login code', 'Your login code is {}'.format(login_code), settings.EMAIL_HOST_USER, [email], fail_silently=False)

        return Response({"message": "Login code has been sent to your email."}, status=status.HTTP_200_OK)


class ConfirmLoginView(generics.GenericAPIView):
    serializer_class = LoginConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        conn = get_redis_connection("default")
        stored_code = conn.get(email + '_login_code')

        if not stored_code:
            return Response({"error": "Login code expired. Please try logging in again."}, status=status.HTTP_400_BAD_REQUEST)

        if str(int(stored_code)) != code:
            return Response({"error": "Login code does not match. Please try again."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        token = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        # Deleting the code after successful login
        conn.delete(email + '_login_code')

        return Response({"message": "Logged in successfully.", "token": token}, status=status.HTTP_200_OK)
