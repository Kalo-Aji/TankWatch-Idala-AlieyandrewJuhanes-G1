from decimal import Decimal

from django import forms


class TankLevelAdjustmentForm(forms.Form):
    level_percent = forms.DecimalField(
        label="Tank level",
        min_value=Decimal("0"),
        max_value=Decimal("100"),
        max_digits=5,
        decimal_places=1,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": "0",
                "max": "100",
                "step": "0.1",
            }
        ),
    )
