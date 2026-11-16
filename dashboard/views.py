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
        # Mock telemetry dataset for TankWatch industrial telemetry
        context["tanks"] = [
            {"id": "TK-101", "name": "Main Water Reservoir", "type": "Potable Water", "level": 82, "status": "Normal", "badge": "success", "temp": "21.4°C"},
            {"id": "TK-102", "name": "Backup Retention Basin", "type": "Raw Water", "level": 45, "status": "Moderate", "badge": "warning", "temp": "23.1°C"},
            {"id": "TK-103", "name": "Chemical Purification Tank", "type": "Disinfectant", "level": 94, "status": "High Warning", "badge": "danger", "temp": "19.8°C"},
            {"id": "TK-104", "name": "Rainwater Harvest Vault", "type": "Harvested", "level": 63, "status": "Normal", "badge": "success", "temp": "20.2°C"},
        ]
        context["active_alarms"] = 1
        context["pumps_active"] = 3
        context["role_title"] = "Tank Operator & Staff"
        return context


class MemberDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "dashboard/member_dashboard.html"
    allowed_roles = [CustomUser.Role.MEMBER, CustomUser.Role.STUDENT]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["role_title"] = "Client / Member"
        context["assigned_tank"] = "Building B - Potable Tank (TK-101)"
        context["daily_usage"] = "142 Liters"
        context["supply_status"] = "Continuous / Optimal"
        return context
