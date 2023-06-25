from rest_framework import serializers
from .models import CustomUser, Order, Proposal, Review, Chat, Message, MessageImage
from .constants import ROLES
from rest_framework.exceptions import NotFound


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

class RoleSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['role']

    def validate_role(self, value):
        if value not in dict(ROLES):
            raise serializers.ValidationError('Invalid role selected.')
        return value


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('customer',)

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class MessageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageImage
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    images = MessageImageSerializer(many=True)
    class Meta:
        model = Message
        fields = '__all__'

class ChatSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    order_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Chat
        fields = ('id', 'user_id', 'order_id')

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            current_user = request.user
            user_to_chat_with_id = validated_data.pop('user_id')
            user_to_chat_with = CustomUser.objects.get(id=user_to_chat_with_id)

            order_id = validated_data.pop('order_id')
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                raise NotFound('Order with id {} does not exist.'.format(order_id))

            if current_user.role == 'Customer':
                chat = Chat.objects.create(customer=current_user, executor=user_to_chat_with, order=order)
            else:
                chat = Chat.objects.create(executor=current_user, customer=user_to_chat_with, order=order)
                
            return chat
        else:
            raise serializers.ValidationError("Error occurred during chat creation.")
