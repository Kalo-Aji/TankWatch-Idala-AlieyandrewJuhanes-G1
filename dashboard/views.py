from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from accounts.models import CustomUser


class DashboardDispatchView(LoginRequiredMixin, View):
    """
    Directs each authenticated user to their role-specific dashboard.
    """
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_administrator():
            return redirect("admin_dashboard")
        elif user.is_operator():
            return redirect("operator_dashboard")
        else:
            return redirect("member_dashboard")


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Ensures that a user can only access dashboards intended for their role.
    If a user attempts to type another role's URL directly, access is blocked
    and they are redirected to their own dashboard with a clear error message.
    """
    allowed_roles = []

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.role in self.allowed_roles

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        messages.error(
            self.request,
            "Access Denied: You do not have permission to access that dashboard."
        )
        return redirect("dashboard_dispatch")


class AdminDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "dashboard/admin_dashboard.html"
    allowed_roles = [CustomUser.Role.ADMIN]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_users = CustomUser.objects.all().order_by("-date_joined")
        context["total_users"] = all_users.count()
        context["admin_count"] = all_users.filter(role=CustomUser.Role.ADMIN).count()
        context["operator_count"] = all_users.filter(role=CustomUser.Role.OPERATOR).count()
        context["member_count"] = all_users.filter(
            role__in=[CustomUser.Role.MEMBER, CustomUser.Role.STUDENT]
        ).count()
        context["recent_users"] = all_users[:10]
        context["role_title"] = "System Administrator"
        return context


class OperatorDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "dashboard/operator_dashboard.html"
    allowed_roles = [CustomUser.Role.OPERATOR]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # LPG Gas Tank Telemetry dataset for TankWatch
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


class MemberDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "dashboard/member_dashboard.html"
    allowed_roles = [CustomUser.Role.MEMBER, CustomUser.Role.STUDENT]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["role_title"] = "LPG Supply Monitor / Subscriber"
        context["assigned_tank"] = "LPG-03 — Laundry Boiler Gas Tank"
        context["daily_usage"] = "42 kg LPG Consumed Today"
        context["supply_status"] = "Pressure Normal / Valve Open"
        return context
