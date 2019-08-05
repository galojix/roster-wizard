from django.test import TestCase
from django.urls import reverse

from ..models import Day


class DayTests(TestCase):
    def setUp(self):
        self.day = Day.objects.create(number=5)

    def test_day_content(self):
        self.assertEquals(self.day.number, 5)

    def test_day_detail_view(self):
        response = self.client.get(
            reverse("day_detail", kwargs={"pk": self.day.id})
        )
        print("Location: ", response['location'])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 5)
        self.assertTemplateUsed(response, "day_detail.html")
