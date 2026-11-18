from django.urls import path

from accounts.features.registration.views import SignUpView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
]
