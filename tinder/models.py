from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, 
                    first_name=None, last_name=None, avatar=None, 
                    phone_number=None):
        if not email:
            raise ValueError('Email is required.')

        user = self.model(email=self.normalize_email(email), first_name=first_name,
                          last_name=last_name, avatar=avatar, phone_number=phone_number)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password):
        superuser = self.create_user(email=email, password=password)
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save(using=self._db)
        return superuser


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = [
    ('Customer', 'Заказчик'),
    ('Executor', 'Исполнитель')
    ]

    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    avatar = models.ImageField(upload_to='user/avatar', blank=True, null=True)
    phone_number = PhoneNumberField(unique=True, blank=True, null=True)

    role = models.CharField(choices=ROLES, blank=True, max_length=255)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        unique_together = ('email',)


class Order(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('in_progress', 'In progress'),
        ('completed', 'Completed'),
        ('proposal', 'Proposal'),
    ]
    service = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    executor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='executed_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    deadline = models.DateTimeField()
    adress_link = models.URLField(blank=True, null=True)
    adress = models.CharField(blank=False, null=False)


class Proposal(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='proposals')
    maid = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='proposals')


class Review(models.Model):
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_reviews')
    review_text = models.TextField()
    rating = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)


class Chat(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='chats')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='customer_chats')
    executor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='executor_chats')


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class MessageImage(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='chat_images/')
