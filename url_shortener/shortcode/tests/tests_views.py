import json
from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from shortcode.models import URL


class ShortenerViewTestCase(TestCase):
    def setUp(self):
        self.description = "description"
        self.shortcode = "shortcode"
        self.url = "https://test.com?abc2=123asd&aaa=11212"
        self.content_type = "application/json"

    def test_valid_POST(self):
        resp = self.client.post(
            reverse("create"),
            json.dumps(
                {
                    "description": self.description,
                    "url": self.url,
                }
            ),
            content_type=self.content_type,
        )
        self.assertEqual(resp.status_code, 201)

    def test_valid_POST_with_shortcode(self):
        resp = self.client.post(
            reverse("create"),
            json.dumps(
                {
                    "description": self.description,
                    "url": self.url,
                    "shortcode": "shortcode",
                }
            ),
            content_type=self.content_type,
        )
        self.assertEqual(resp.status_code, 201)

    def test_valid_POST_with_expiration(self):
        expiration = (datetime.today() + timedelta(days=20)).date().strftime("%m/%d/%Y")

        resp = self.client.post(
            reverse("create"),
            json.dumps(
                {
                    "description": self.description,
                    "url": self.url,
                    "shortcode": "shortcode",
                    "expiration": expiration,
                }
            ),
            content_type=self.content_type,
        )
        self.assertEqual(resp.status_code, 201)

    def test_invalid_POST_shortcode(self):
        resp = self.client.post(
            reverse("create"),
            json.dumps(
                {
                    "description": self.description,
                    "url": self.url,
                    "shortcode": "short",
                }
            ),
            content_type=self.content_type,
        )
        self.assertEqual(resp.status_code, 400)

    def test_invalid_POST_url(self):
        resp = self.client.post(
            reverse("create"),
            json.dumps(
                {
                    "description": self.description,
                    "url": "test.com?abc2=123asd&aaa=11212",
                }
            ),
            content_type=self.content_type,
        )
        self.assertEqual(resp.status_code, 400)

    def test_invalid_POST_json(self):
        resp = self.client.post(
            reverse("create"),
            json.dumps({}),
            content_type=self.content_type,
        )
        self.assertEqual(resp.status_code, 400)

    def test_recover_GET_valid(self):
        URL.objects.create(
            description=self.description,
            shortcode=self.shortcode,
            fullname=self.url,
            name="name",
        )

        resp = self.client.get(f"/{self.shortcode}")
        self.assertEqual(resp.status_code, 200)

    def test_recover_GET_invalid(self):
        resp = self.client.get(f"/{self.shortcode}")
        self.assertEqual(resp.status_code, 404)
