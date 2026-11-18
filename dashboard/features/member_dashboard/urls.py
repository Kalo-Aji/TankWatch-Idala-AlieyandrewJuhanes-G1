from django.urls import path

from dashboard.features.member_dashboard.views import (
    ConsumptionRecordDeleteView,
    ConsumptionRecordUpdateView,
    MemberDashboardView,
    MemberTankStatusView,
)

urlpatterns = [
    path(
        "dashboard/member/tank-status/",
        MemberTankStatusView.as_view(),
        name="member_tank_status",
    ),
    path(
        "dashboard/member/consumption/<int:pk>/edit/",
        ConsumptionRecordUpdateView.as_view(),
        name="consumption_edit",
    ),
    path(
        "dashboard/member/consumption/<int:pk>/delete/",
        ConsumptionRecordDeleteView.as_view(),
        name="consumption_delete",
    ),
    path(
        "dashboard/member/",
        MemberDashboardView.as_view(),
        name="member_dashboard",
    ),
]
