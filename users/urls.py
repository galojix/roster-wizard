"""URLs."""
from django.urls import path

from .views import (
    CustomUserListView,
    CustomUserUpdateView,
    CustomUserDetailView,
    CustomUserDeleteView,
    CustomUserCreateView,
)

urlpatterns = [
    path(
        "custom_user/<int:pk>/update/",
        CustomUserUpdateView.as_view(),
        name="custom_user_update",
    ),
    path(
        "custom_user/<int:pk>/",
        CustomUserDetailView.as_view(),
        name="custom_user_detail",
    ),
    path(
        "custom_user/<int:pk>/delete/",
        CustomUserDeleteView.as_view(),
        name="custom_user_delete",
    ),
    path(
        "custom_user/create/",
        CustomUserCreateView.as_view(),
        name="custom_user_create",
    ),
    path(
        "custom_user/", CustomUserListView.as_view(), name="custom_user_list"
    ),
]
