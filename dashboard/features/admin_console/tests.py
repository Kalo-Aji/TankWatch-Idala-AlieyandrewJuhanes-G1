from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from dashboard.features.member_dashboard.models import MemberTank


class AdminConsoleFeatureTests(TestCase):
    def setUp(self):
        admin = CustomUser.objects.create_user(
            username="admin",
            password="TankWatch-Test-2026!",
            role=CustomUser.Role.ADMIN,
        )
        self.client.force_login(admin)

    def test_each_admin_console_screen_renders(self):
        urls = [
            reverse("custom_admin:home"),
            reverse("custom_admin:user_list"),
            reverse("custom_admin:user_create"),
            reverse("custom_admin:tanks"),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'data-theme="light"')
                self.assertContains(response, 'id="theme-toggle"')
                self.assertContains(response, "Dark mode")

    def test_lpg_simulation_shows_each_members_account_level(self):
        member = CustomUser.objects.create_user(
            username="client",
            password="TankWatch-Test-2026!",
            role=CustomUser.Role.MEMBER,
            first_name="Client",
        )
        tank = MemberTank.objects.create(
            user=member,
            remaining_kg=Decimal("1.70"),
        )

        response = self.client.get(reverse("custom_admin:tanks"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Live LPG levels for each client and member account.")
        self.assertContains(response, 'data-user-id="{}"'.format(member.pk))
        self.assertContains(response, "12.0%")
        self.assertContains(
            response,
            reverse("custom_admin:user_tank_level", kwargs={"pk": member.pk}),
        )
        self.assertNotContains(response, "Domestic Cooking Gas Cylinder Bank")

    def test_lpg_simulation_marks_40_percent_as_refill_soon(self):
        member = CustomUser.objects.create_user(
            username="client",
            password="TankWatch-Test-2026!",
            role=CustomUser.Role.MEMBER,
        )
        MemberTank.objects.create(
            user=member,
            remaining_kg=Decimal("5.68"),
        )

        response = self.client.get(reverse("custom_admin:tanks"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "40.0%")
        self.assertContains(response, "Refill soon")
        self.assertContains(response, "bg-warning-subtle")
        self.assertContains(response, "text-warning")
        self.assertContains(response, "bg-warning")

    def test_lpg_simulation_status_endpoint_returns_members_only(self):
        member = CustomUser.objects.create_user(
            username="client",
            password="TankWatch-Test-2026!",
            role=CustomUser.Role.MEMBER,
        )
        operator = CustomUser.objects.create_user(
            username="operator",
            password="TankWatch-Test-2026!",
            role=CustomUser.Role.OPERATOR,
        )
        MemberTank.objects.create(user=member, remaining_kg=Decimal("1.70"))
        MemberTank.objects.create(user=operator, remaining_kg=Decimal("7.10"))

        response = self.client.get(reverse("custom_admin:tank_status"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["members"],
            [
                {
                    "user_id": member.pk,
                    "name": "client",
                    "username": "client",
                    "role": "Member",
                    "level_percent": float(Decimal("1.70") / Decimal("14.20") * 100),
                    "remaining_kg": "1.70",
                    "capacity_kg": "14.20",
                }
            ],
        )

    def test_user_directory_has_readable_light_rows(self):
        response = self.client.get(reverse("custom_admin:user_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user-directory-table")
        self.assertContains(response, "color: #1f2937 !important")
        self.assertContains(response, "background-color: #ffffff !important")
        self.assertContains(response, "td:first-child .fw-semibold")
        self.assertContains(response, "td:nth-child(2)")
        self.assertContains(response, "color: #000000 !important")

    def test_user_edit_screen_renders(self):
        user = CustomUser.objects.create_user(
            username="member",
            password="TankWatch-Test-2026!",
        )

        response = self.client.get(
            reverse("custom_admin:user_edit", kwargs={"pk": user.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Account Active")

    def test_admin_can_still_create_admin_accounts(self):
        url = reverse("custom_admin:user_create")
        response = self.client.get(url)

        self.assertContains(response, "System Administrator")

        response = self.client.post(
            url,
            {
                "username": "newadmin",
                "email": "newadmin@example.com",
                "first_name": "New",
                "last_name": "Admin",
                "contact_number": "",
                "role": CustomUser.Role.ADMIN,
                "password1": "TankWatch-Test-2026!",
                "password2": "TankWatch-Test-2026!",
            },
        )

        self.assertRedirects(response, reverse("custom_admin:user_list"))
        self.assertTrue(
            CustomUser.objects.filter(
                username="newadmin",
                role=CustomUser.Role.ADMIN,
            ).exists()
        )

    def test_admin_can_adjust_member_tank_percentage(self):
        member = CustomUser.objects.create_user(
            username="member",
            password="TankWatch-Test-2026!",
            role=CustomUser.Role.MEMBER,
        )
        tank, _ = MemberTank.objects.get_or_create(user=member)
        url = reverse("custom_admin:user_tank_level", kwargs={"pk": member.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Set tank level (%)")

        response = self.client.post(url, {"level_percent": "50"})

        self.assertRedirects(response, reverse("custom_admin:user_list"))
        tank.refresh_from_db()
        self.assertEqual(tank.remaining_kg, Decimal("7.10"))

    def test_refilling_member_tank_is_reflected_in_member_dashboard(self):
        member = CustomUser.objects.create_user(
            username="member",
            password="TankWatch-Test-2026!",
            role=CustomUser.Role.MEMBER,
        )
        tank = MemberTank.objects.create(
            user=member,
            remaining_kg=Decimal("2.02"),
        )
        adjustment_url = reverse(
            "custom_admin:user_tank_level",
            kwargs={"pk": member.pk},
        )

        response = self.client.post(adjustment_url, {"level_percent": "100"})

        self.assertRedirects(response, reverse("custom_admin:user_list"))
        tank.refresh_from_db()
        self.assertEqual(tank.remaining_kg, tank.capacity_kg)

        self.client.force_login(member)
        status_response = self.client.get(reverse("member_tank_status"))
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(
            status_response.json(),
            {
                "level_percent": 100.0,
                "remaining_kg": "14.20",
                "capacity_kg": "14.20",
            },
        )

        dashboard_response = self.client.get(reverse("member_dashboard"))
        self.assertContains(dashboard_response, "100.0% Full")
        self.assertContains(dashboard_response, '<span id="tank-remaining-kg">14.20</span>')

    def test_tank_level_adjustment_rejects_out_of_range_percentages(self):
        member = CustomUser.objects.create_user(
            username="member",
            password="TankWatch-Test-2026!",
            role=CustomUser.Role.MEMBER,
        )
        tank, _ = MemberTank.objects.get_or_create(user=member)
        url = reverse("custom_admin:user_tank_level", kwargs={"pk": member.pk})

        response = self.client.post(url, {"level_percent": "101"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].errors.as_data()["level_percent"][0].code,
            "max_value",
        )
        tank.refresh_from_db()
        self.assertEqual(tank.remaining_kg, Decimal("14.20"))

    def test_tank_level_adjustment_only_applies_to_members(self):
        operator = CustomUser.objects.create_user(
            username="operator",
            password="TankWatch-Test-2026!",
            role=CustomUser.Role.OPERATOR,
        )

        response = self.client.get(
            reverse("custom_admin:user_tank_level", kwargs={"pk": operator.pk})
        )

        self.assertEqual(response.status_code, 404)
