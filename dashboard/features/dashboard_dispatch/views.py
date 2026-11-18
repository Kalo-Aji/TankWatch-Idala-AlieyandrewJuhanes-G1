from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View


class DashboardDispatchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_administrator():
            return redirect("admin_dashboard")
        if user.is_operator():
            return redirect("operator_dashboard")
        return redirect("member_dashboard")
