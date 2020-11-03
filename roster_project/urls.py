"""URLs."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings


urlpatterns = [
    path("dbmanage/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("rosters/", include("rosters.urls")),
    path("api/v1/", include("api.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("users/", include("users.urls")),
    path("", include("pages.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
