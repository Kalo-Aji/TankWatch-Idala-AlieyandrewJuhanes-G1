from django.urls import path

from dashboard.features.operator_dashboard.views import OperatorDashboardView

urlpatterns = [
    path(
        "dashboard/operator/",
        OperatorDashboardView.as_view(),
        name="operator_dashboard",
    ),
]
