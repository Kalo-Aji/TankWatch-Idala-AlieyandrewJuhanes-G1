from django.views.generic import TemplateView

from accounts.models import CustomUser
from dashboard.features.shared.access import RoleRequiredMixin


class AdminDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "dashboard/admin_dashboard.html"
    allowed_roles = [CustomUser.Role.ADMIN]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_users = CustomUser.objects.select_related("member_tank").order_by(
            "-date_joined"
        )
        context["total_users"] = all_users.count()
        context["admin_count"] = all_users.filter(
            role=CustomUser.Role.ADMIN
        ).count()
        context["operator_count"] = all_users.filter(
            role=CustomUser.Role.OPERATOR
        ).count()
        context["member_count"] = all_users.filter(
            role__in=[CustomUser.Role.MEMBER, CustomUser.Role.STUDENT]
        ).count()
        context["role_title"] = "System Administrator"
        return context
