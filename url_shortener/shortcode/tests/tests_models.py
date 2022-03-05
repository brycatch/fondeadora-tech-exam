from datetime import datetime, timedelta
from django.db import IntegrityError
from django.test import TestCase

from shortcode.models import URL, Tracking


class URLModelTestCase(TestCase):
    def test_add_url_with_expiration(self):
        description = "description-test"
        shortcode = "shortcode"
        fullname = "fullname"
        name = "name"
        query_params = "query_params"
        expiration = "2022-03-03"

        url = URL.objects.create(
            description=description,
            shortcode=shortcode,
            fullname=fullname,
            name=name,
            query_params=query_params,
            expiration=expiration,
        )
        self.assertEqual(url.description, description)
        self.assertEqual(url.shortcode, shortcode)

    def test_add_url_without_optionals(self):
        description = "description-test"
        shortcode = "shortcode"
        fullname = "fullname"
        name = "name"

        url = URL.objects.create(
            description=description, shortcode=shortcode, fullname=fullname, name=name
        )
        today_plus_10_days = (datetime.today() + timedelta(days=10)).date()

        self.assertEqual(url.description, description)
        self.assertEqual(url.expiration, today_plus_10_days)

    def test_add_url_with_duplicated_shortcode(self):
        description = "description-test"
        shortcode = "shortcode_2"
        fullname = "fullname"
        name = "name"

        URL.objects.create(
            description=description, shortcode=shortcode, fullname=fullname, name=name
        )

        self.assertRaises(
            IntegrityError,
            URL.objects.create,
            description=description,
            shortcode=shortcode,
            fullname=fullname,
            name=name,
        )


class TrackingModelTestCase(TestCase):
    def test_add_tracking(self):
        description = "description-test"
        shortcode = "shortcode"
        fullname = "fullname"
        name = "name"
        query_params = "query_params"
        expiration = "2022-03-03"

        url = URL.objects.create(
            description=description,
            shortcode=shortcode,
            fullname=fullname,
            name=name,
            query_params=query_params,
            expiration=expiration,
        )

        tracking = Tracking(url=url)

        self.assertEqual(url.pk, tracking.url.pk)
