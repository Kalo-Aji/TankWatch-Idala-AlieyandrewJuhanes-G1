from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser


def add_bootstrap_classes(form):
    for name, field in form.fields.items():
        if isinstance(field.widget, forms.Select):
            css_class = "form-select"
        elif isinstance(field.widget, forms.CheckboxInput):
            css_class = "form-check-input"
        else:
            css_class = "form-control"
        existing_class = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = f"{existing_class} {css_class}".strip()


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="First Name",
        widget=forms.TextInput(attrs={"placeholder": "e.g. John"})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Last Name",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Doe"})
    )
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={"placeholder": "e.g. name@example.com"})
    )
    contact_number = forms.CharField(
        max_length=25,
        required=False,
        label="Contact Number",
        widget=forms.TextInput(attrs={"placeholder": "e.g. +1 555 123 4567"})
    )
    role = forms.ChoiceField(
        choices=[
            (CustomUser.Role.MEMBER, "Client / Member"),
            (CustomUser.Role.OPERATOR, "Tank Operator / Staff"),
            (CustomUser.Role.ADMIN, "System Administrator"),
        ],
        initial=CustomUser.Role.MEMBER,
        label="Account Role",
        help_text="Select your role to access the corresponding dashboard."
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


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, label="First Name")
    last_name = forms.CharField(max_length=150, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    contact_number = forms.CharField(max_length=25, required=False, label="Contact Number")

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
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already in use by another account.")
        return email


class BootstrapAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)
        self.fields["username"].widget.attrs.update({"placeholder": "Enter your username"})
        self.fields["password"].widget.attrs.update({"placeholder": "Enter your password"})


class AdminUserEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, label="First Name")
    last_name = forms.CharField(max_length=150, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    contact_number = forms.CharField(max_length=25, required=False, label="Contact Number")
    role = forms.ChoiceField(
        choices=CustomUser.Role.choices,
        label="Assigned Role",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    is_active = forms.BooleanField(
        required=False,
        label="Account Active",
        help_text="Uncheck to suspend or disable this user account."
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name", "role", "contact_number", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already in use by another account.")
        return email

