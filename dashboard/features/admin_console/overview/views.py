import sys

import django
from django.conf import settings
from django.views.generic import TemplateView

from accounts.models import CustomUser
from dashboard.features.shared.access import AdminOnlyMixin


class CustomAdminHomeView(AdminOnlyMixin, TemplateView):
    template_name = "admin_custom/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_users = CustomUser.objects.all().order_by("-date_joined")
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
        context["active_users"] = all_users.filter(is_active=True).count()
        context["inactive_users"] = all_users.filter(is_active=False).count()
        context["recent_users"] = all_users[:8]
        context["django_version"] = django.get_version()
        context["python_version"] = sys.version.split()[0]
        context["db_engine"] = settings.DATABASES["default"]["ENGINE"].split(".")[-1]
        context["debug_mode"] = settings.DEBUG
        return context
