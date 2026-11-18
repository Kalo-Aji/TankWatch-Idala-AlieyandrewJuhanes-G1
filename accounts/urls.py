from django.urls import include, path

urlpatterns = [
    path("", include("accounts.features.authentication.urls")),
    path("", include("accounts.features.registration.urls")),
    path("", include("accounts.features.profile.urls")),
]
