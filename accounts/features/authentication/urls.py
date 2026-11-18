from django.urls import path

from accounts.features.authentication.views import (
    BootstrapLoginView,
    CustomLogoutView,
)

urlpatterns = [
    path("login/", BootstrapLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
]
