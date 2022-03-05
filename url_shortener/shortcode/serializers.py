import re, string, random
from datetime import datetime, timedelta

from rest_framework import serializers
from django.http import Http404
from django.shortcuts import get_object_or_404

from shortcode.constants import URL_REGEX, QUERY_PARAMS_REGEX
from shortcode.models import URL, Tracking


class CreateURLSerializer(serializers.Serializer):
    description = serializers.CharField(
        required=True, allow_blank=False, max_length=256
    )
    url = serializers.CharField(required=True, allow_blank=False, max_length=2048)
    shortcode = serializers.CharField(
        required=False, allow_null=False, allow_blank=True, max_length=64
    )
    expiration = serializers.DateField(required=False)

    def validate_url(self, url):
        url_is_invalid = re.search(URL_REGEX, url) is None
        if url_is_invalid:
            raise serializers.ValidationError(
                f"URL: {url} is not a valid URL. Must be started with http or https"
            )
        return url

    def validate_shortcode(self, shortcode):
        try:
            duplicated_url = URL.objects.get(shortcode=shortcode)
            is_expired = duplicated_url.expiration < datetime.today().date()
            if is_expired:
                raise serializers.ValidationError(
                    f"Shortcode: {shortcode} is already used"
                )
            return shortcode
        except URL.DoesNotExist:
            return shortcode

    def validate_expiration(self, expiration):
        today_plus_10_days = (datetime.today() + timedelta(days=10)).date()
        expiration_is_invalid = expiration < today_plus_10_days
        if expiration_is_invalid:
            raise serializers.ValidationError(
                f"Expiration: {expiration} is not a valid date"
            )
        return expiration

    def get_url_to_insert(self):
        description = self.validated_data.get("description")
        name, query_params, fullname = self.__get_name_and_query_params(
            self.validated_data.get("url")
        )
        shortcode, is_new = self.__get_shortcode(fullname)
        expiration = self.__get_expiration()
        url_to_insert = {
            "description": description,
            "shortcode": shortcode,
            "fullname": fullname,
            "name": name,
            "query_params": query_params,
            "expiration": expiration,
        }

        return url_to_insert, is_new

    def create(self, get_url_to_insert, is_new):
        """
        TODO: Make documentation like this
        Create and return a new `URL` instance, given the validated data.
        """
        if is_new:
            url = URL.objects.create(**get_url_to_insert)
            get_url_to_insert["id"] = url.pk
        return get_url_to_insert

    def __get_name_and_query_params(self, fullname):
        url_splitted = fullname.split("?")
        if len(url_splitted) > 1:
            name = url_splitted[0]
            query_params = self.__get_sorted_params(url_splitted[1])
            fullname = f"{name}?{query_params}"
        else:
            name = url_splitted[0]
            query_params = None
            fullname = name
        return name, query_params, fullname

    def __get_sorted_params(self, params):
        result = ""
        params_sorted = []
        params_splitted = params.split("&")

        for p_splitted in params_splitted:
            p_groups = re.findall(QUERY_PARAMS_REGEX, p_splitted)[0]
            params_sorted.append(p_groups)

        params_sorted.sort(key=lambda x: x[0])
        params_length = len(params_sorted)
        counter = 0

        for p_sorted in params_sorted:
            result += f"{p_sorted[0]}={p_sorted[1]}"
            counter += 1
            if counter < params_length:
                result += "&"
        return result

    def __get_shortcode(self, fullname):
        shortcode_generated = self.validated_data.get(
            "shortcode",
            self.__get_random_string(6),
        )
        try:
            duplicated_url = URL.objects.get(fullname=fullname)
            is_new = duplicated_url.expiration < datetime.today().date()
            shortcode = shortcode_generated if is_new else duplicated_url.shortcode
            return shortcode, is_new
        except URL.DoesNotExist:
            is_new = True
            return shortcode_generated, is_new

    def __get_expiration(self):
        today_plus_10_days = (datetime.today() + timedelta(days=10)).date()
        date = self.validated_data.get("expiration", today_plus_10_days)
        return date

    def __get_random_string(self, length):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


class RecoverURLSerializer(serializers.Serializer):
    shortcode = serializers.CharField(
        required=True, allow_blank=False, min_length=6, max_length=256
    )

    def get_url(self):
        shortcode = self.validated_data.get("shortcode")
        url = get_object_or_404(URL, shortcode=shortcode)
        is_expired = url.expiration < datetime.today().date()
        if is_expired:
            raise Http404
        return url

    def create_tracking(self, url):
        tracking = Tracking(url=url)
        tracking.save()
