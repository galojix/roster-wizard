"""URLs."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordChangeView,
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("dbmanage/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path(
        "password_change/",
        PasswordChangeView.as_view(
            template_name="account/password_change.html"
        ),
        name="password_change",
    ),
    path(
        "password_change_done/",
        PasswordChangeDoneView.as_view(
            template_name="account/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path("rosters/", include("rosters.urls")),
    path("api/v1/", include("api.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("api/v1/dj-rest-auth/", include("dj_rest_auth.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("users/", include("users.urls")),
    path("", include("pages.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
