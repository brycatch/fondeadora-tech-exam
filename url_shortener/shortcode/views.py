from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from shortcode.serializers import CreateURLSerializer, RecoverURLSerializer


class Create(APIView):
    def post(self, request):
        serializer = CreateURLSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url_to_insert, is_new = serializer.get_url_to_insert()
        url = serializer.create(url_to_insert, is_new)

        return Response(
            data={"url": url, "is_new": is_new},
            status=status.HTTP_201_CREATED,
        )


class Recover(APIView):
    def get(self, request, shortcode):
        serializer = RecoverURLSerializer(data={"shortcode": shortcode})
        serializer.is_valid(raise_exception=True)
        url = serializer.get_url()
        serializer.create_tracking(url)
        return Response(data={"url": url.fullname}, status=status.HTTP_200_OK)
