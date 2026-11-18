from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthenticationFeatureTests(TestCase):
    def test_login_page_renders_and_login_redirects_to_dashboard(self):
        user = get_user_model().objects.create_user(
            username="member",
            password="TankWatch-Test-2026!",
        )

        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("login"),
            {"username": user.username, "password": "TankWatch-Test-2026!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("dashboard_dispatch"))

    def test_logout_redirects_to_login(self):
        user = get_user_model().objects.create_user(
            username="member",
            password="TankWatch-Test-2026!",
        )
        self.client.force_login(user)

        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)
