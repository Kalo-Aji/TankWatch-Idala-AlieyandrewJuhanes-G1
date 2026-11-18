from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.features.shared.forms import add_bootstrap_classes
from accounts.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="First Name",
        widget=forms.TextInput(attrs={"placeholder": "e.g. John"}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Last Name",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Doe"}),
    )
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={"placeholder": "e.g. name@example.com"}),
    )
    contact_number = forms.CharField(
        max_length=25,
        required=False,
        label="Contact Number",
        widget=forms.TextInput(attrs={"placeholder": "e.g. +1 555 123 4567"}),
    )
    role = forms.ChoiceField(
        choices=[
            (CustomUser.Role.MEMBER, "Client / Member"),
            (CustomUser.Role.OPERATOR, "Tank Operator / Staff"),
        ],
        initial=CustomUser.Role.MEMBER,
        label="Account Role",
        help_text="Select your role to access the corresponding dashboard.",
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "contact_number",
            "role",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email
