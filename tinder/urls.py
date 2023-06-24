from django.urls import path
from .views import RegisterView, ConfirmRegisterView, RequestLoginView, ConfirmLoginView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('request-register/', RegisterView.as_view(), name='request-register'),
    path('confirm-register/', ConfirmRegisterView.as_view(), name='confirm-register'),
    path('request-login/', RequestLoginView.as_view(), name='request-login'),
    path('confirm-login/', ConfirmLoginView.as_view(), name='confirm-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
