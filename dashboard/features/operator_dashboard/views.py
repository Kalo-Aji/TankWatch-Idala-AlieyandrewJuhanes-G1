from django.views.generic import TemplateView

from accounts.models import CustomUser
from dashboard.features.shared.access import RoleRequiredMixin


class OperatorDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "dashboard/operator_dashboard.html"
    allowed_roles = [CustomUser.Role.OPERATOR]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tanks"] = [
            {"id": "LPG-01", "name": "Domestic Cooking Gas (50kg Bank)", "type": "LPG Cylinders", "capacity": "2,500 kg", "current_volume": "1,950 kg", "level": 78, "status": "Optimal", "badge": "success", "temp": "26.1°C", "ullage": "550 kg"},
            {"id": "LPG-02", "name": "Commercial Kitchen Supply", "type": "Bulk LPG Manifold", "capacity": "5,000 kg", "current_volume": "3,100 kg", "level": 62, "status": "Stable", "badge": "info", "temp": "25.4°C", "ullage": "1,900 kg"},
            {"id": "LPG-03", "name": "Laundry Boiler Gas Tank", "type": "Industrial LPG", "capacity": "10,000 kg", "current_volume": "8,600 kg", "level": 86, "status": "High Stock", "badge": "success", "temp": "27.0°C", "ullage": "1,400 kg"},
            {"id": "LPG-04", "name": "Residential Household Reserve", "type": "11kg Cylinders", "capacity": "550 kg", "current_volume": "132 kg", "level": 24, "status": "Low — Refill Soon", "badge": "warning", "temp": "25.8°C", "ullage": "418 kg"},
        ]
        context["active_alarms"] = 1
        context["pumps_active"] = 4
        context["role_title"] = "LPG Tank Monitoring Technician"
        return context
