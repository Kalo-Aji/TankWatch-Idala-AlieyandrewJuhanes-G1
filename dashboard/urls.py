from django.urls import path
from .views import (
    AdminDashboardView,
    DashboardDispatchView,
    MemberDashboardView,
    OperatorDashboardView,
)

urlpatterns = [
    path("", DashboardDispatchView.as_view(), name="dashboard_dispatch"),
    path("dashboard/", DashboardDispatchView.as_view(), name="dashboard"),
    path("dashboard/admin/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("dashboard/operator/", OperatorDashboardView.as_view(), name="operator_dashboard"),
    path("dashboard/member/", MemberDashboardView.as_view(), name="member_dashboard"),
]
