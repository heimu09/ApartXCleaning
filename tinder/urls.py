from django.urls import path
from .views import (RegisterView, ConfirmRegisterView, RequestLoginView,
                    ConfirmLoginView, RoleSelectionView, CustomUserListView,
                    CustomUserDetailView, OrderListView, OrderDetailView,
                    ProposalListView, ProposalDetailView, ReviewListView,
                    ReviewDetailView, UserProfileView, ChatListView,
                    ChatDetailView, MessageListView, MessageDetailView)
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
    path('select-role/', RoleSelectionView.as_view(), name='select-role'),
    path('users/', CustomUserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', CustomUserDetailView.as_view(), name='user-detail'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('proposals/', ProposalListView.as_view(), name='proposal-list'),
    path('proposals/<int:pk>/', ProposalDetailView.as_view(), name='proposal-detail'),
    path('reviews/', ReviewListView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('chats/', ChatListView.as_view()),
    path('chats/<int:pk>/', ChatDetailView.as_view()),
    path('messages/', MessageListView.as_view()),
    path('messages/<int:pk>/', MessageDetailView.as_view()),
]
