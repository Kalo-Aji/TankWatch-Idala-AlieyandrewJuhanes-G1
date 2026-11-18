from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, FormView, ListView, UpdateView

from accounts.features.user_management.forms import (
    AdminUserCreationForm,
    AdminUserEditForm,
)
from accounts.models import CustomUser
from dashboard.features.admin_console.user_management.forms import (
    TankLevelAdjustmentForm,
)
from dashboard.features.member_dashboard.models import MemberTank
from dashboard.features.shared.access import AdminOnlyMixin


MEMBER_ROLES = [CustomUser.Role.MEMBER, CustomUser.Role.STUDENT]


class CustomAdminUserListView(AdminOnlyMixin, ListView):
    model = CustomUser
    template_name = "admin_custom/user_list.html"
    context_object_name = "users"
    paginate_by = 12

    def get_queryset(self):
        queryset = CustomUser.objects.select_related("member_tank").order_by(
            "-date_joined"
        )
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
    form_class = AdminUserCreationForm
    template_name = "admin_custom/user_form.html"
    success_url = reverse_lazy("custom_admin:user_list")

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request,
            f"User account @{user.username} has been created successfully with role {user.get_role_display()}.",
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
            f"User account @{user.username} has been updated successfully.",
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
            messages.error(
                request,
                "Security check: You cannot deactivate your own current administrator account.",
            )
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
            messages.error(
                request,
                "Security check: You cannot delete your own current administrator account.",
            )
            return redirect("custom_admin:user_list")

        username = user.username
        user.delete()
        messages.success(request, f"User account @{username} was permanently removed.")
        return redirect("custom_admin:user_list")


class CustomAdminTankLevelView(AdminOnlyMixin, FormView):
    form_class = TankLevelAdjustmentForm
    template_name = "admin_custom/tank_level_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.member = get_object_or_404(
            CustomUser,
            pk=kwargs["pk"],
            role__in=MEMBER_ROLES,
        )
        self.tank, _ = MemberTank.objects.get_or_create(user=self.member)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial["level_percent"] = self.tank.level_percent.quantize(
            Decimal("0.1"),
            rounding=ROUND_HALF_UP,
        )
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member"] = self.member
        context["tank"] = self.tank
        return context

    def form_valid(self, form):
        with transaction.atomic():
            tank = MemberTank.objects.select_for_update().get(pk=self.tank.pk)
            level_percent = form.cleaned_data["level_percent"]
            tank.remaining_kg = (
                tank.capacity_kg
                * level_percent
                / Decimal("100")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            tank.save(update_fields=["remaining_kg"])

        messages.success(
            self.request,
            f"@{self.member.username}'s tank level was set to "
            f"{level_percent:.1f}%.",
        )
        return redirect("custom_admin:user_list")
