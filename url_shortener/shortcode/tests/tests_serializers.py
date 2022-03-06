from django.test import TestCase
from django.http.response import Http404
from datetime import datetime, timedelta

from rest_framework.exceptions import ValidationError
from shortcode.serializers import CreateURLSerializer, RecoverURLSerializer
from shortcode.models import URL


class CreateURLSerializerTestCase(TestCase):
    def setUp(self):
        self.valid_description = "Description"

        self.valid_url_without_params = "http://test.com"
        self.valid_url_with_params = "http://test.com?abc2=123asd&aaa=11212"
        self.valid_url_params = "aaa=11212&abc2=123asd"
        self.invalid_url = "test.com"

        self.valid_fullname = "http://test.com?aaa=11212&abc2=123asd"

        self.valid_shortcode = "shortcode"
        self.invalid_shortcode = "short"

        self.valid_expiration = (datetime.today() + timedelta(days=20)).date()
        self.invalid_expiration = (datetime.today() - timedelta(days=10)).date()

        self.SHORTCODE_LENGTH = 6

    def test_create_serializer_basic(self):
        data = {
            "description": self.valid_description,
            "url": self.valid_url_without_params,
        }
        serializer = CreateURLSerializer(data=data)
        is_valid = serializer.is_valid(raise_exception=True)
        self.assertTrue(is_valid)

    def test_create_serializer_with_shortcode(self):
        data = {
            "description": self.valid_description,
            "url": self.valid_url_without_params,
            "shortcode": self.valid_shortcode,
        }
        serializer = CreateURLSerializer(data=data)
        is_valid = serializer.is_valid(raise_exception=True)
        self.assertTrue(is_valid)

    def test_create_serializer_with_invalid_url(self):

        data = {
            "description": self.valid_description,
            "url": self.invalid_url,
            "shortcode": self.valid_shortcode,
            "expiration": self.valid_expiration,
        }
        serializer = CreateURLSerializer(data=data)
        self.assertRaises(ValidationError, serializer.is_valid, raise_exception=True)

    def test_create_serializer_with_invalid_expiration(self):

        data = {
            "description": self.valid_description,
            "url": self.valid_url_without_params,
            "shortcode": self.valid_shortcode,
            "expiration": self.invalid_expiration,
        }
        serializer = CreateURLSerializer(data=data)
        self.assertRaises(ValidationError, serializer.is_valid, raise_exception=True)

    def test_create_serializer_with_invalid_shortcode(self):
        data = {
            "description": self.valid_description,
            "url": self.valid_url_without_params,
            "shortcode": self.invalid_shortcode,
            "expiration": self.valid_expiration,
        }
        serializer = CreateURLSerializer(data=data)
        self.assertRaises(ValidationError, serializer.is_valid, raise_exception=True)

    def test_create_serializer_with_duplicated_shortcode(self):
        URL.objects.create(
            description=self.valid_description,
            shortcode=self.valid_shortcode,
            fullname="fullname",
            name="name",
        )

        data = {
            "description": self.valid_description,
            "url": self.valid_url_without_params,
            "shortcode": self.valid_shortcode,
            "expiration": self.valid_expiration,
        }

        serializer = CreateURLSerializer(data=data)
        self.assertRaises(ValidationError, serializer.is_valid, raise_exception=True)

    def test_get_url_to_insert_basic(self):
        data = {
            "description": self.valid_description,
            "url": self.valid_url_without_params,
        }
        serializer = CreateURLSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        url_to_insert, is_new = serializer.get_url_to_insert()

        self.assertTrue(is_new)
        self.assertEqual(url_to_insert["description"], data["description"])
        self.assertEqual(len(url_to_insert["shortcode"]), self.SHORTCODE_LENGTH)
        self.assertEqual(url_to_insert["query_params"], None)
        self.assertEqual(
            (datetime.today() + timedelta(days=10)).date(), url_to_insert["expiration"]
        )

    def test_get_url_to_insert_with_url(self):
        data = {
            "description": self.valid_description,
            "url": self.valid_url_with_params,
        }
        serializer = CreateURLSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        url_to_insert, is_new = serializer.get_url_to_insert()

        self.assertTrue(is_new)
        self.assertEqual(url_to_insert["description"], data["description"])
        self.assertEqual(len(url_to_insert["shortcode"]), self.SHORTCODE_LENGTH)
        self.assertEqual(url_to_insert["query_params"], self.valid_url_params)
        self.assertEqual(
            url_to_insert["fullname"],
            f"{url_to_insert['name']}?{url_to_insert['query_params']}",
        )
        self.assertNotEqual(url_to_insert["fullname"], data["url"])
        self.assertEqual(
            (datetime.today() + timedelta(days=10)).date(), url_to_insert["expiration"]
        )

    def test_get_url_to_insert_with_inserted_url(self):
        url = URL.objects.create(
            description=self.valid_description,
            shortcode=self.valid_shortcode,
            fullname=self.valid_fullname,
            name="name",
        )

        data = {
            "description": self.valid_description,
            "url": self.valid_url_with_params,
        }
        serializer = CreateURLSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        url_to_insert, is_new = serializer.get_url_to_insert()

        self.assertFalse(is_new)
        self.assertEqual(url_to_insert["description"], data["description"])
        self.assertEqual(url_to_insert["shortcode"], url.shortcode)
        self.assertEqual(url_to_insert["query_params"], self.valid_url_params)
        self.assertNotEqual(url_to_insert["fullname"], data["url"])

    def test_create_new(self):
        data = {
            "description": self.valid_description,
            "url": self.valid_url_with_params,
        }
        serializer = CreateURLSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        url_to_insert, is_new = serializer.get_url_to_insert()
        url = serializer.create(url_to_insert, is_new)

        self.assertTrue(is_new)
        self.assertGreater(url["id"], 0)

    def test_create_not_new(self):
        URL.objects.create(
            description=self.valid_description,
            shortcode=self.valid_shortcode,
            fullname=self.valid_fullname,
            name="name",
        )

        data = {
            "description": self.valid_description,
            "url": self.valid_url_with_params,
        }
        serializer = CreateURLSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        url_to_insert, is_new = serializer.get_url_to_insert()
        url = serializer.create(url_to_insert, is_new)

        self.assertFalse(is_new)
        self.assertEqual(url.get("id"), None)


class RecoverURLSerializerTestCase(TestCase):
    def setUp(self):
        self.valid_description = "Description"
        self.valid_shortcode = "shortcode"
        self.invalid_shortcode = "short"
        self.valid_fullname = "http://test.com?aaa=11212&abc2=123asd"

    def test_serializer_valid_shortcode(self):
        data = {"shortcode": self.valid_shortcode}
        serializer = RecoverURLSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid)

    def test_serializer_invalid_shortcode(self):
        data = {"shortcode": self.invalid_shortcode}
        serializer = RecoverURLSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)

    def test_serializer_invalid_length(self):
        data = {"shortcode": "short"}
        serializer = RecoverURLSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)

    def test_get_url_valid(self):
        URL.objects.create(
            description=self.valid_description,
            shortcode=self.valid_shortcode,
            fullname=self.valid_fullname,
            name="name",
        )
        data = {"shortcode": self.valid_shortcode}
        serializer = RecoverURLSerializer(data=data)
        serializer.is_valid()
        url = serializer.get_url()
        self.assertEqual(url.fullname, self.valid_fullname)

    def test_get_url_not_found(self):
        data = {"shortcode": "shortcode"}
        serializer = RecoverURLSerializer(data=data)
        serializer.is_valid()
        self.assertRaises(Http404, serializer.get_url)

    def test_create_tracking(self):
        url = URL.objects.create(
            description=self.valid_description,
            shortcode=self.valid_shortcode,
            fullname=self.valid_fullname,
            name="name",
        )

        data = {"shortcode": "shortcode"}
        serializer = RecoverURLSerializer(data=data)
        serializer.is_valid()
        serializer.create_tracking(url)
