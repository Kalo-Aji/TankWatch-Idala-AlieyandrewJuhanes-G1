from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from accounts.models import CustomUser
from dashboard.features.member_dashboard.models import MemberTank
from dashboard.features.shared.access import AdminOnlyMixin


MEMBER_ROLES = [CustomUser.Role.MEMBER, CustomUser.Role.STUDENT]


def get_member_tanks():
    member_ids = list(
        CustomUser.objects.filter(role__in=MEMBER_ROLES).values_list("id", flat=True)
    )
    existing_user_ids = set(
        MemberTank.objects.filter(user_id__in=member_ids).values_list(
            "user_id",
            flat=True,
        )
    )
    MemberTank.objects.bulk_create(
        [
            MemberTank(user_id=user_id)
            for user_id in member_ids
            if user_id not in existing_user_ids
        ],
        ignore_conflicts=True,
    )
    return (
        MemberTank.objects.filter(user__role__in=MEMBER_ROLES)
        .select_related("user")
        .order_by("user__username")
    )


def serialize_member_tanks(tanks):
    return [
        {
            "user_id": tank.user_id,
            "name": tank.user.get_full_name() or tank.user.username,
            "username": tank.user.username,
            "role": tank.user.get_role_display(),
            "level_percent": float(tank.level_percent),
            "remaining_kg": f"{tank.remaining_kg:.2f}",
            "capacity_kg": f"{tank.capacity_kg:.2f}",
        }
        for tank in tanks
    ]


class CustomAdminTankFleetView(AdminOnlyMixin, TemplateView):
    template_name = "admin_custom/tanks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member_tanks"] = get_member_tanks()
        return context


@method_decorator(never_cache, name="dispatch")
class CustomAdminTankStatusView(AdminOnlyMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(
            {"members": serialize_member_tanks(get_member_tanks())}
        )
