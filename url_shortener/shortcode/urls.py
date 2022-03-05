from django.urls import path
from shortcode import views

urlpatterns = [
    path("create", views.Create.as_view(), name="create"),
    path("<slug:shortcode>", views.Recover.as_view(), name="shortcode"),
]
