from django.urls import path
from .views import RegisterView, ConfirmView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('confirm/', ConfirmView.as_view(), name='confirm'),
]
