from django.urls import path

from dashboard.features.dashboard_dispatch.views import DashboardDispatchView

urlpatterns = [
    path("", DashboardDispatchView.as_view(), name="dashboard_dispatch"),
    path("dashboard/", DashboardDispatchView.as_view(), name="dashboard"),
]
