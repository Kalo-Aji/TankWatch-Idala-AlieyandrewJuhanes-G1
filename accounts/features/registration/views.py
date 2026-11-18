from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from accounts.features.registration.forms import CustomUserCreationForm


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Your account was created successfully! You can now log in with your credentials.",
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Please correct the errors below before submitting the form.",
        )
        return super().form_invalid(form)
