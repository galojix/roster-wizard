from django.urls import path

from .views import (
    UserListView,
    UserUpdateView,
    UserDetailView,
    UserDeleteView,
    UserCreateView,
)

urlpatterns = [
    path(
        "users/<int:pk>/update/", UserUpdateView.as_view(), name="user_update"
    ),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path(
        "users/<int:pk>/delete/", UserDeleteView.as_view(), name="user_delete"
    ),
    path("users/create/", UserCreateView.as_view(), name="user_create"),
    path("users/", UserListView.as_view(), name="user_list"),
]
