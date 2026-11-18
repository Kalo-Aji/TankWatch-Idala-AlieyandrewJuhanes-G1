from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views import View
from django.views.generic import TemplateView

from accounts.models import CustomUser
from dashboard.features.member_dashboard.forms import (
    ConsumptionRecordForm,
    GasConsumptionForm,
)
from dashboard.features.member_dashboard.models import (
    ConsumptionRecord,
    MemberTank,
)
from dashboard.features.shared.access import RoleRequiredMixin


class MemberDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "dashboard/member_dashboard.html"
    allowed_roles = [CustomUser.Role.MEMBER, CustomUser.Role.STUDENT]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tank = context.get("tank")
        if tank is None:
            tank, _ = MemberTank.objects.get_or_create(user=self.request.user)

        consumption_form = context.get("consumption_form")
        if consumption_form is None:
            consumption_form = GasConsumptionForm(remaining_kg=tank.remaining_kg)

        today = timezone.localdate()
        context["tank"] = tank
        context["remaining_percent"] = tank.level_percent
        context["daily_usage"] = (
            ConsumptionRecord.objects.filter(
                user=self.request.user,
                created_at__date=today,
            ).aggregate(total=Sum("amount_kg"))["total"]
            or Decimal("0.00")
        )
        context["consumption_records"] = ConsumptionRecord.objects.filter(
            user=self.request.user
        )
        context["consumption_form"] = consumption_form
        context["role_title"] = "LPG Supply Monitor / Subscriber"
        context["assigned_tank"] = f"{tank.capacity_kg:.2f} kg LPG Cylinder"
        return context

    def post(self, request, *args, **kwargs):
        tank, _ = MemberTank.objects.get_or_create(user=request.user)

        with transaction.atomic():
            tank = MemberTank.objects.select_for_update().get(pk=tank.pk)
            form = GasConsumptionForm(
                request.POST,
                remaining_kg=tank.remaining_kg,
            )
            if form.is_valid():
                amount = form.cleaned_data["amount_kg"]
                tank.remaining_kg -= amount
                tank.save(update_fields=["remaining_kg"])
                ConsumptionRecord.objects.create(
                    user=request.user,
                    amount_kg=amount,
                )
                messages.success(
                    request,
                    f"{amount:.2f} kg of gas consumption recorded.",
                )
                return redirect("member_dashboard")

        return self.render_to_response(
            self.get_context_data(tank=tank, consumption_form=form)
        )


class ConsumptionRecordUpdateView(RoleRequiredMixin, View):
    allowed_roles = [CustomUser.Role.MEMBER, CustomUser.Role.STUDENT]
    template_name = "dashboard/edit_consumption.html"

    def get(self, request, *args, **kwargs):
        record = get_object_or_404(
            ConsumptionRecord,
            pk=kwargs["pk"],
            user=request.user,
        )
        tank, _ = MemberTank.objects.get_or_create(user=request.user)
        allowed_amount = min(tank.capacity_kg, tank.remaining_kg + record.amount_kg)
        form = ConsumptionRecordForm(
            remaining_kg=allowed_amount,
            initial={"amount_kg": record.amount_kg},
        )
        return render(
            request,
            self.template_name,
            {"record": record, "tank": tank, "form": form},
        )

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            tank, _ = MemberTank.objects.get_or_create(user=request.user)
            tank = MemberTank.objects.select_for_update().get(pk=tank.pk)
            record = get_object_or_404(
                ConsumptionRecord.objects.select_for_update(),
                pk=kwargs["pk"],
                user=request.user,
            )
            allowed_amount = min(
                tank.capacity_kg,
                tank.remaining_kg + record.amount_kg,
            )
            form = ConsumptionRecordForm(
                request.POST,
                remaining_kg=allowed_amount,
            )
            if form.is_valid():
                new_amount = form.cleaned_data["amount_kg"]
                tank.remaining_kg = min(
                    tank.capacity_kg,
                    tank.remaining_kg + record.amount_kg - new_amount,
                )
                tank.save(update_fields=["remaining_kg"])
                record.amount_kg = new_amount
                record.save(update_fields=["amount_kg"])
                messages.success(request, "Consumption record updated successfully.")
                return redirect("member_dashboard")

        return render(
            request,
            self.template_name,
            {
                "record": record,
                "tank": tank,
                "form": form,
            },
        )


class ConsumptionRecordDeleteView(RoleRequiredMixin, View):
    allowed_roles = [CustomUser.Role.MEMBER, CustomUser.Role.STUDENT]

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            tank, _ = MemberTank.objects.get_or_create(user=request.user)
            tank = MemberTank.objects.select_for_update().get(pk=tank.pk)
            record = get_object_or_404(
                ConsumptionRecord.objects.select_for_update(),
                pk=kwargs["pk"],
                user=request.user,
            )
            tank.remaining_kg = min(
                tank.capacity_kg,
                tank.remaining_kg + record.amount_kg,
            )
            tank.save(update_fields=["remaining_kg"])
            record.delete()

        messages.success(request, "Consumption record deleted and tank balance restored.")
        return redirect("member_dashboard")


@method_decorator(never_cache, name="dispatch")
class MemberTankStatusView(RoleRequiredMixin, View):
    allowed_roles = [CustomUser.Role.MEMBER, CustomUser.Role.STUDENT]

    def get(self, request, *args, **kwargs):
        tank, _ = MemberTank.objects.get_or_create(user=request.user)
        return JsonResponse(
            {
                "level_percent": float(tank.level_percent),
                "remaining_kg": f"{tank.remaining_kg:.2f}",
                "capacity_kg": f"{tank.capacity_kg:.2f}",
            }
        )
