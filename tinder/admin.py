from django.contrib import admin
from .models import CustomUser, Order, Bid, Review, Photo


admin.site.register([CustomUser, Order, Bid, Review, Photo])