from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class ProfileFeatureTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="member",
            password="TankWatch-Test-2026!",
        )
        self.client.force_login(self.user)

    def test_profile_page_renders_and_updates_current_user(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("profile"),
            {
                "first_name": "Updated",
                "last_name": "Member",
                "email": "updated@example.com",
                "contact_number": "123456789",
            },
        )

        self.assertRedirects(response, reverse("profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.email, "updated@example.com")
