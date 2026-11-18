from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from dashboard.features.member_dashboard.models import (
    ConsumptionRecord,
    MemberTank,
)


class MemberConsumptionTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="member",
            password="test-password",
            role=CustomUser.Role.MEMBER,
        )
        self.client.force_login(self.user)
        self.url = reverse("member_dashboard")

    def test_dashboard_starts_with_full_14_2_kg_tank(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        tank = MemberTank.objects.get(user=self.user)
        self.assertEqual(tank.capacity_kg, Decimal("14.20"))
        self.assertEqual(tank.remaining_kg, Decimal("14.20"))
        self.assertContains(response, "100.0% Full")

    def test_consumption_reduces_balance_and_updates_percentage(self):
        response = self.client.post(self.url, {"amount_kg": "2"})

        self.assertRedirects(response, self.url)
        tank = MemberTank.objects.get(user=self.user)
        self.assertEqual(tank.remaining_kg, Decimal("12.20"))
        self.assertEqual(
            ConsumptionRecord.objects.filter(user=self.user).count(),
            1,
        )

        response = self.client.get(self.url)
        self.assertContains(response, '<span id="tank-remaining-kg">12.20</span>')
        self.assertContains(response, '<span id="tank-capacity-kg">14.20</span>')
        self.assertContains(response, "85.9% Full")
        self.assertContains(response, "2.00 kg LPG Consumed Today")

    def test_consumption_history_displays_all_owned_records_and_actions(self):
        records = [
            ConsumptionRecord.objects.create(user=self.user, amount_kg=Decimal(amount))
            for amount in ("1.00", "2.00", "3.00", "4.00", "5.00", "6.00")
        ]

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Consumption History")
        self.assertContains(
            response,
            reverse("consumption_edit", kwargs={"pk": records[-1].pk}),
        )
        self.assertContains(
            response,
            reverse("consumption_delete", kwargs={"pk": records[-1].pk}),
        )
        self.assertContains(response, "1.00 kg")

    def test_member_can_edit_consumption_and_balance_is_adjusted(self):
        tank, _ = MemberTank.objects.get_or_create(user=self.user)
        tank.remaining_kg = Decimal("12.20")
        tank.save(update_fields=["remaining_kg"])
        record = ConsumptionRecord.objects.create(
            user=self.user,
            amount_kg=Decimal("2.00"),
        )
        url = reverse("consumption_edit", kwargs={"pk": record.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Consumption Record")

        response = self.client.post(url, {"amount_kg": "3.00"})

        self.assertRedirects(response, self.url)
        tank.refresh_from_db()
        record.refresh_from_db()
        self.assertEqual(tank.remaining_kg, Decimal("11.20"))
        self.assertEqual(record.amount_kg, Decimal("3.00"))

    def test_member_can_delete_consumption_and_balance_is_restored(self):
        tank, _ = MemberTank.objects.get_or_create(user=self.user)
        tank.remaining_kg = Decimal("12.20")
        tank.save(update_fields=["remaining_kg"])
        record = ConsumptionRecord.objects.create(
            user=self.user,
            amount_kg=Decimal("2.00"),
        )

        response = self.client.post(
            reverse("consumption_delete", kwargs={"pk": record.pk})
        )

        self.assertRedirects(response, self.url)
        self.assertFalse(ConsumptionRecord.objects.filter(pk=record.pk).exists())
        tank.refresh_from_db()
        self.assertEqual(tank.remaining_kg, Decimal("14.20"))

    def test_editing_consumption_rejects_amount_over_available_balance(self):
        tank, _ = MemberTank.objects.get_or_create(user=self.user)
        tank.remaining_kg = Decimal("12.20")
        tank.save(update_fields=["remaining_kg"])
        record = ConsumptionRecord.objects.create(
            user=self.user,
            amount_kg=Decimal("2.00"),
        )
        url = reverse("consumption_edit", kwargs={"pk": record.pk})

        response = self.client.post(url, {"amount_kg": "14.21"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].errors.as_data()["amount_kg"][0].code,
            "max_value",
        )
        tank.refresh_from_db()
        record.refresh_from_db()
        self.assertEqual(tank.remaining_kg, Decimal("12.20"))
        self.assertEqual(record.amount_kg, Decimal("2.00"))

    def test_members_cannot_edit_or_delete_another_users_records(self):
        other_user = CustomUser.objects.create_user(
            username="other",
            password="TankWatch-Test-2026!",
            role=CustomUser.Role.MEMBER,
        )
        record = ConsumptionRecord.objects.create(
            user=other_user,
            amount_kg=Decimal("2.00"),
        )

        edit_response = self.client.get(
            reverse("consumption_edit", kwargs={"pk": record.pk})
        )
        delete_response = self.client.post(
            reverse("consumption_delete", kwargs={"pk": record.pk})
        )

        self.assertEqual(edit_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
        self.assertTrue(ConsumptionRecord.objects.filter(pk=record.pk).exists())

    def test_only_member_roles_can_manage_consumption_records(self):
        operator = CustomUser.objects.create_user(
            username="operator",
            password="TankWatch-Test-2026!",
            role=CustomUser.Role.OPERATOR,
        )
        record = ConsumptionRecord.objects.create(
            user=operator,
            amount_kg=Decimal("2.00"),
        )
        self.client.force_login(operator)

        edit_response = self.client.get(
            reverse("consumption_edit", kwargs={"pk": record.pk})
        )
        delete_response = self.client.post(
            reverse("consumption_delete", kwargs={"pk": record.pk})
        )

        self.assertEqual(edit_response.status_code, 302)
        self.assertEqual(
            edit_response["Location"],
            reverse("dashboard_dispatch"),
        )
        self.assertEqual(delete_response.status_code, 302)
        self.assertEqual(
            delete_response["Location"],
            reverse("dashboard_dispatch"),
        )
        self.assertTrue(ConsumptionRecord.objects.filter(pk=record.pk).exists())

    def test_cannot_consume_more_than_remaining_amount(self):
        response = self.client.post(self.url, {"amount_kg": "14.21"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["consumption_form"].errors.as_data()["amount_kg"][0].code,
            "max_value",
        )
        self.assertEqual(
            MemberTank.objects.get(user=self.user).remaining_kg,
            Decimal("14.20"),
        )
        self.assertFalse(ConsumptionRecord.objects.filter(user=self.user).exists())

    def test_consumption_is_scoped_to_logged_in_user(self):
        self.client.post(self.url, {"amount_kg": "2"})
        other_user = CustomUser.objects.create_user(
            username="other",
            password="test-password",
            role=CustomUser.Role.MEMBER,
        )
        self.client.force_login(other_user)

        response = self.client.get(self.url)

        self.assertContains(response, '<span id="tank-remaining-kg">14.20</span>')
        self.assertContains(response, '<span id="tank-capacity-kg">14.20</span>')
        self.assertContains(response, "0.00 kg LPG Consumed Today")

    def test_live_status_endpoint_returns_only_the_signed_in_users_tank(self):
        tank, _ = MemberTank.objects.get_or_create(user=self.user)
        tank.remaining_kg = Decimal("1.70")
        tank.save(update_fields=["remaining_kg"])
        other_user = CustomUser.objects.create_user(
            username="other",
            password="test-password",
            role=CustomUser.Role.MEMBER,
        )
        MemberTank.objects.create(
            user=other_user,
            remaining_kg=Decimal("7.10"),
        )

        response = self.client.get(reverse("member_tank_status"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "level_percent": float(Decimal("1.70") / Decimal("14.20") * 100),
                "remaining_kg": "1.70",
                "capacity_kg": "14.20",
            },
        )
        self.assertEqual(response["Cache-Control"], "max-age=0, no-cache, no-store, must-revalidate, private")

    def test_dashboard_contains_live_simulation_polling(self):
        response = self.client.get(self.url)

        self.assertContains(response, 'data-theme="light"')
        self.assertContains(response, 'id="theme-toggle"')
        self.assertContains(response, "Dark mode")
        self.assertContains(response, "LPG SIMULATION")
        self.assertContains(response, "setInterval(refreshSimulation, 5000)")
        self.assertContains(response, reverse("member_tank_status"))
        self.assertNotContains(response, "Simulation Status")
        self.assertNotContains(response, "Live simulation")
        self.assertNotContains(response, "simulation-live-status")
        self.assertNotContains(response, "LPG Tank")
        self.assertContains(response, "Today's Gas Usage")
        self.assertContains(response, "Petron")

    def test_tank_level_turns_red_at_15_percent_or_less(self):
        tank, _ = MemberTank.objects.get_or_create(user=self.user)
        tank.remaining_kg = Decimal("2.13")
        tank.save(update_fields=["remaining_kg"])

        response = self.client.get(self.url)

        self.assertContains(response, "15.0% Full")
        self.assertContains(response, "text-danger")
        self.assertContains(response, "bg-danger")

    def test_tank_level_is_yellow_between_15_and_40_percent(self):
        tank, _ = MemberTank.objects.get_or_create(user=self.user)
        tank.remaining_kg = Decimal("2.20")
        tank.save(update_fields=["remaining_kg"])

        response = self.client.get(self.url)

        self.assertContains(response, "15.5% Full")
        self.assertContains(response, "text-warning")
        self.assertContains(response, "bg-warning")

    def test_tank_level_is_yellow_at_40_percent(self):
        tank, _ = MemberTank.objects.get_or_create(user=self.user)
        tank.remaining_kg = Decimal("5.68")
        tank.save(update_fields=["remaining_kg"])

        response = self.client.get(self.url)

        self.assertContains(response, "40.0% Full")
        self.assertContains(response, "text-warning")
        self.assertContains(response, "bg-warning")

    def test_tank_level_is_green_above_40_percent(self):
        tank, _ = MemberTank.objects.get_or_create(user=self.user)
        tank.remaining_kg = Decimal("5.69")
        tank.save(update_fields=["remaining_kg"])

        response = self.client.get(self.url)

        self.assertContains(response, "40.1% Full")
        self.assertContains(response, "text-success")
        self.assertContains(response, "bg-success")
