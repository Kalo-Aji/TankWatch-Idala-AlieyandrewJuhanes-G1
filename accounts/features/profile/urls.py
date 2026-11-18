from django.urls import path

from accounts.features.profile.views import ProfileUpdateView

urlpatterns = [
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
]
