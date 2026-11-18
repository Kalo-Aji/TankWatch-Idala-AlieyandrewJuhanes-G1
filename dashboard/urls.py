from django.urls import include, path

urlpatterns = [
    path("", include("dashboard.features.dashboard_dispatch.urls")),
    path("", include("dashboard.features.admin_dashboard.urls")),
    path("", include("dashboard.features.operator_dashboard.urls")),
    path("", include("dashboard.features.member_dashboard.urls")),
]
