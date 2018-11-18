from django.urls import path

from .views import (
    UserListView,
    UserUpdateView,
    UserDetailView,
    UserDeleteView,
    UserCreateView,
)

urlpatterns = [
    path("users/<int:pk>/edit/", UserUpdateView.as_view(), name="user_edit"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path(
        "users/<int:pk>/delete/", UserDeleteView.as_view(), name="user_delete"
    ),
    path("users/new/", UserCreateView.as_view(), name="user_new"),
    path("users/", UserListView.as_view(), name="user_list"),
]
