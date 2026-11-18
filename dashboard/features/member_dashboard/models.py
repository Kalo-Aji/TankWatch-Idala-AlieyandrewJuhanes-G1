from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class MemberTank(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_tank",
    )
    capacity_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("14.20"),
    )
    remaining_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("14.20"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    def __str__(self):
        return f"{self.user.username}'s LPG tank"

    @property
    def level_percent(self):
        if self.capacity_kg <= 0:
            return Decimal("0")
        return self.remaining_kg / self.capacity_kg * Decimal("100")


class ConsumptionRecord(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gas_consumption_records",
    )
    amount_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.amount_kg} kg consumed by {self.user.username}"
