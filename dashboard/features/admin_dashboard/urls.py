from django.urls import path

from dashboard.features.admin_dashboard.views import AdminDashboardView

urlpatterns = [
    path("dashboard/admin/", AdminDashboardView.as_view(), name="admin_dashboard"),
]
