"""URLs."""

from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("dbmanage/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("rosters/", include("rosters.urls")),
    path("users/", include("users.urls")),
    path("", include("pages.urls")),
]
