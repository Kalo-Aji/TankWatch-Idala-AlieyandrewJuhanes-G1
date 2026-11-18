from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class AdminDashboardFeatureTests(TestCase):
    def test_admin_dashboard_renders_for_administrator(self):
        admin = CustomUser.objects.create_user(
            username="admin",
            password="TankWatch-Test-2026!",
            role=CustomUser.Role.ADMIN,
        )
        self.client.force_login(admin)

        response = self.client.get(reverse("admin_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["role_title"], "System Administrator")

    def test_admin_dashboard_does_not_render_personnel_directory(self):
        admin = CustomUser.objects.create_user(
            username="admin",
            password="TankWatch-Test-2026!",
            role=CustomUser.Role.ADMIN,
        )
        self.client.force_login(admin)

        response = self.client.get(reverse("admin_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Station Personnel & Client Directory")
