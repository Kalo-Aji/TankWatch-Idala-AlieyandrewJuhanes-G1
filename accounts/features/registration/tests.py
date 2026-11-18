from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class RegistrationFeatureTests(TestCase):
    def test_signup_page_renders_and_creates_account(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "System Administrator")

        response = self.client.post(
            reverse("signup"),
            {
                "username": "newmember",
                "email": "newmember@example.com",
                "first_name": "New",
                "last_name": "Member",
                "contact_number": "",
                "role": CustomUser.Role.MEMBER,
                "password1": "TankWatch-Test-2026!",
                "password2": "TankWatch-Test-2026!",
            },
        )

        self.assertRedirects(response, reverse("login"))
        self.assertTrue(CustomUser.objects.filter(username="newmember").exists())

    def test_public_signup_rejects_admin_role_submitted_directly(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "attemptedadmin",
                "email": "attemptedadmin@example.com",
                "first_name": "Attempted",
                "last_name": "Admin",
                "contact_number": "",
                "role": CustomUser.Role.ADMIN,
                "password1": "TankWatch-Test-2026!",
                "password2": "TankWatch-Test-2026!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].errors.as_data()["role"][0].code,
            "invalid_choice",
        )
        self.assertFalse(
            CustomUser.objects.filter(username="attemptedadmin").exists()
        )
