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
        "customuser/<int:pk>/update/",
        CustomUserUpdateView.as_view(),
        name="customuser_update",
    ),
    path(
        "customuser/<int:pk>/",
        CustomUserDetailView.as_view(),
        name="customuser_detail",
    ),
    path(
        "customuser/<int:pk>/delete/",
        CustomUserDeleteView.as_view(),
        name="customuser_delete",
    ),
    path(
        "customuser/create/",
        CustomUserCreateView.as_view(),
        name="customuser_create",
    ),
    path("customuser/", CustomUserListView.as_view(), name="customuser_list"),
]
