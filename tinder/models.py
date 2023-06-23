from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField

from .constants import ROLES


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
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='user/avatar', blank=True)
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
    service = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    host = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    accepted_bid = models.OneToOneField(
        'Bid',
        on_delete=models.SET_NULL,
        related_name='accepted_in_order',
        null=True,
        blank=True
    )
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class Bid(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='bids')
    maid = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField(blank=True)

    class Meta:
        verbose_name = "Предложение"
        verbose_name_plural = "Предложения"


class Review(models.Model):
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.PositiveIntegerField()
    text = models.TextField(blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"



class Photo(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='orders/photos/')

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фотографии"
