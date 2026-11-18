from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Custom-built Admin Console from scratch
    path("admin/", include("dashboard.features.admin_console.urls")),
    # Standard Django admin kept on separate backup endpoint
    path("django-backend-admin/", admin.site.urls),
    # Accounts & Authentication
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    # Dashboards & Public root
    path("", include("dashboard.urls")),
]
