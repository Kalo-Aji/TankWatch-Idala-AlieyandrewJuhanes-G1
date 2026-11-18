from decimal import Decimal

from django import forms
from django.core.validators import MaxValueValidator


class GasConsumptionForm(forms.Form):
    amount_kg = forms.DecimalField(
        label="How much gas did you consume?",
        min_value=Decimal("0.01"),
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "placeholder": "e.g. 2.00",
            }
        ),
    )

    def __init__(self, *args, remaining_kg, **kwargs):
        super().__init__(*args, **kwargs)
        amount_field = self.fields["amount_kg"]
        amount_field.max_value = remaining_kg
        amount_field.validators.append(MaxValueValidator(remaining_kg))
        amount_field.widget.attrs["max"] = str(remaining_kg)


class ConsumptionRecordForm(GasConsumptionForm):
    amount_kg = forms.DecimalField(
        label="Consumption amount (kg)",
        min_value=Decimal("0.01"),
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.01",
                "placeholder": "e.g. 2.00",
            }
        ),
    )
