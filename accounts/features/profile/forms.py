from django import forms

from accounts.features.shared.forms import add_bootstrap_classes
from accounts.models import CustomUser


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, label="First Name")
    last_name = forms.CharField(max_length=150, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    contact_number = forms.CharField(
        max_length=25,
        required=False,
        label="Contact Number",
    )

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email", "contact_number")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        if (
            CustomUser.objects.exclude(pk=self.instance.pk)
            .filter(email__iexact=email)
            .exists()
        ):
            raise forms.ValidationError(
                "This email address is already in use by another account."
            )
        return email
