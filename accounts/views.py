from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from .forms import BootstrapAuthenticationForm, CustomUserCreationForm, ProfileUpdateForm
from .models import CustomUser


class BootstrapLoginView(LoginView):
    authentication_form = BootstrapAuthenticationForm
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please check your credentials.")
        return super().form_invalid(form)


class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect("login")

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect("login")


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Your account was created successfully! You can now log in with your credentials."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Please correct the errors below before submitting the form."
        )
        return super().form_invalid(form)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = "profile/account_profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your profile details have been updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update profile. Please verify your input.")
        return super().form_invalid(form)
