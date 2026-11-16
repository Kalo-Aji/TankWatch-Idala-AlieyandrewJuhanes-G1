from django.urls import path
from .views import BootstrapLoginView, CustomLogoutView, ProfileUpdateView, SignUpView

urlpatterns = [
    path("login/", BootstrapLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
]
