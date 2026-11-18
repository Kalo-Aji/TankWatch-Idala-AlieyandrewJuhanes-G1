from django.contrib import admin

from dashboard.features.member_dashboard.models import (
    ConsumptionRecord,
    MemberTank,
)


@admin.register(MemberTank)
class MemberTankAdmin(admin.ModelAdmin):
    list_display = ("user", "capacity_kg", "remaining_kg")
    search_fields = ("user__username",)


@admin.register(ConsumptionRecord)
class ConsumptionRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "amount_kg", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username",)
