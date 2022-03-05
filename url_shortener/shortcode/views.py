from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class Create(APIView):
    def post(self, request):
        return Response(data={"test": "post"}, status=status.HTTP_200_OK)


class Recover(APIView):
    def get(self, request, shortcode):
        return Response(data={"test": shortcode}, status=status.HTTP_200_OK)
