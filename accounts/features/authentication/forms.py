from django.contrib.auth.forms import AuthenticationForm

from accounts.features.shared.forms import add_bootstrap_classes


class BootstrapAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)
        self.fields["username"].widget.attrs.update(
            {"placeholder": "Enter your username"}
        )
        self.fields["password"].widget.attrs.update(
            {"placeholder": "Enter your password"}
        )
