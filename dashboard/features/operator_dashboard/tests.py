from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class OperatorDashboardFeatureTests(TestCase):
    def test_operator_dashboard_renders_for_operator(self):
        operator = CustomUser.objects.create_user(
            username="operator",
            password="TankWatch-Test-2026!",
            role=CustomUser.Role.OPERATOR,
        )
        self.client.force_login(operator)

        response = self.client.get(reverse("operator_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "LPG-01")
