import sys
import django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from accounts.forms import AdminUserEditForm, CustomUserCreationForm
from accounts.models import CustomUser


class AdminOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Enforces that only users with the ADMIN role or superuser permissions
    can access the custom administration portal.
    """
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return user.role == CustomUser.Role.ADMIN or user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        messages.error(
            self.request,
            "Access Denied: You must be a System Administrator to access the Admin Console."
        )
        return redirect("dashboard_dispatch")


class CustomAdminHomeView(AdminOnlyMixin, TemplateView):
    template_name = "admin_custom/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_users = CustomUser.objects.all().order_by("-date_joined")
        
        context["total_users"] = all_users.count()
        context["admin_count"] = all_users.filter(role=CustomUser.Role.ADMIN).count()
        context["operator_count"] = all_users.filter(role=CustomUser.Role.OPERATOR).count()
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


class CustomAdminUserListView(AdminOnlyMixin, ListView):
    model = CustomUser
    template_name = "admin_custom/user_list.html"
    context_object_name = "users"
    paginate_by = 12

    def get_queryset(self):
        queryset = CustomUser.objects.all().order_by("-date_joined")
        query = self.request.GET.get("q", "").strip()
        role_filter = self.request.GET.get("role", "").strip()
        status_filter = self.request.GET.get("status", "").strip()

        if query:
            queryset = queryset.filter(
                Q(username__icontains=query)
                | Q(email__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(contact_number__icontains=query)
            )

        if role_filter:
            queryset = queryset.filter(role=role_filter)

        if status_filter == "active":
            queryset = queryset.filter(is_active=True)
        elif status_filter == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        context["current_role"] = self.request.GET.get("role", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["roles"] = CustomUser.Role.choices
        return context


class CustomAdminUserCreateView(AdminOnlyMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "admin_custom/user_form.html"
    success_url = reverse_lazy("custom_admin:user_list")

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request,
            f"User account @{user.username} has been created successfully with role {user.get_role_display()}."
        )
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action_title"] = "Create New User Account"
        return context


class CustomAdminUserUpdateView(AdminOnlyMixin, UpdateView):
    model = CustomUser
    form_class = AdminUserEditForm
    template_name = "admin_custom/user_form.html"
    success_url = reverse_lazy("custom_admin:user_list")

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request,
            f"User account @{user.username} has been updated successfully."
        )
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action_title"] = f"Edit User: @{self.object.username}"
        context["editing_user"] = self.object
        return context


class CustomAdminUserToggleStatusView(AdminOnlyMixin, View):
    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(CustomUser, pk=pk)
        if user == request.user:
            messages.error(request, "Security check: You cannot deactivate your own current administrator account.")
            return redirect("custom_admin:user_list")

        user.is_active = not user.is_active
        user.save()
        status_label = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User @{user.username} has been {status_label}.")
        return redirect("custom_admin:user_list")


class CustomAdminUserDeleteView(AdminOnlyMixin, View):
    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(CustomUser, pk=pk)
        if user == request.user:
            messages.error(request, "Security check: You cannot delete your own current administrator account.")
            return redirect("custom_admin:user_list")

        username = user.username
        user.delete()
        messages.success(request, f"User account @{username} was permanently removed.")
        return redirect("custom_admin:user_list")


class CustomAdminTankFleetView(AdminOnlyMixin, TemplateView):
    template_name = "admin_custom/tanks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tanks"] = [
            {"id": "LPG-01", "name": "Domestic Cooking Gas Cylinder Bank", "type": "50kg LPG Cylinders", "capacity": "2,500 kg", "level": 78, "status": "Optimal", "badge": "success"},
            {"id": "LPG-02", "name": "Commercial Kitchen Supply Tank", "type": "Bulk LPG Manifold", "capacity": "5,000 kg", "level": 62, "status": "Stable", "badge": "info"},
            {"id": "LPG-03", "name": "Industrial Laundry Boiler Gas", "type": "Industrial LPG Tank", "capacity": "10,000 kg", "level": 86, "status": "High Stock", "badge": "success"},
            {"id": "LPG-04", "name": "Residential LPG Cylinder Reserve", "type": "11kg Household Cylinders", "capacity": "550 kg", "level": 24, "status": "Low — Refill Soon", "badge": "warning"},
        ]
        return context


class CustomAdminSystemView(AdminOnlyMixin, TemplateView):
    template_name = "admin_custom/system.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["django_version"] = django.get_version()
        context["python_version"] = sys.version
        context["db_engine"] = settings.DATABASES["default"]["ENGINE"]
        context["debug_mode"] = settings.DEBUG
        context["allowed_hosts"] = settings.ALLOWED_HOSTS
        context["time_zone"] = settings.TIME_ZONE
        return context
