from django import forms

from accounts.features.registration.forms import CustomUserCreationForm
from accounts.features.shared.forms import add_bootstrap_classes
from accounts.models import CustomUser


class AdminUserCreationForm(CustomUserCreationForm):
    role = forms.ChoiceField(
        choices=[
            (CustomUser.Role.MEMBER, "Client / Member"),
            (CustomUser.Role.OPERATOR, "Tank Operator / Staff"),
            (CustomUser.Role.ADMIN, "System Administrator"),
        ],
        initial=CustomUser.Role.MEMBER,
        label="Account Role",
        help_text="Select the role for this account.",
    )


class AdminUserEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, label="First Name")
    last_name = forms.CharField(max_length=150, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    contact_number = forms.CharField(
        max_length=25,
        required=False,
        label="Contact Number",
    )
    role = forms.ChoiceField(
        choices=CustomUser.Role.choices,
        label="Assigned Role",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "contact_number",
        )

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
