"""URLs."""

from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("dbmanage/", admin.site.urls),
    # path('users/', include('users.urls')),
    path("users/", include("django.contrib.auth.urls")),
    path("rosters/", include("rosters.urls")),
    path("customusers/", include("users.urls")),
    path("", include("pages.urls")),
]
