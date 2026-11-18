from django.urls import path

from dashboard.features.admin_console.tank_fleet.views import (
    CustomAdminTankFleetView,
    CustomAdminTankStatusView,
)

urlpatterns = [
    path("tanks/status/", CustomAdminTankStatusView.as_view(), name="tank_status"),
    path("tanks/", CustomAdminTankFleetView.as_view(), name="tanks"),
]
