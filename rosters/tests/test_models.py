from django.test import TestCase
from django.urls import reverse

from ..models import Day


class DayTests(TestCase):
    def setUp(self):
        Day.objects.create(number=5)

    def test_day_content(self):
        day = Day.objects.get(id=1)
        expected_object_number = 5
        self.assertEquals(expected_object_number, 5)

    def test_day_detail_view(self):
        response = self.client.get(reverse("day_detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 5)
        self.assertTemplateUsed(response, "day_detail.html")
