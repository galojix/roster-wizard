from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Day


class ModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='temporary',
            password='temporary',
            available=True,
            shifts_per_roster=10,
        )
        self.day = Day.objects.create(number=5)

    def test_user_content(self):
        self.assertEqual(self.user.shifts_per_roster, 10)

    def test_day_content(self):
        self.assertEqual(self.day.number, 5)

    def test_day_detail_view(self):
        self.client.login(username='temporary', password='temporary')
        response = self.client.get(
            reverse("day_detail", kwargs={"pk": self.day.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 5)
        self.assertTemplateUsed(response, "day_detail.html")
