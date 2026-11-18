from django.urls import include, path

app_name = "custom_admin"

urlpatterns = [
    path("", include("dashboard.features.admin_console.overview.urls")),
    path("", include("dashboard.features.admin_console.user_management.urls")),
    path("", include("dashboard.features.admin_console.tank_fleet.urls")),
]
