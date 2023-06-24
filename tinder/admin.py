from django.contrib import admin
from .models import CustomUser, Order, Review


admin.site.register([CustomUser, Order, Review])