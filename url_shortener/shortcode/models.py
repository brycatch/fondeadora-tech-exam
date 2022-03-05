from django.db import models
import datetime


class URL(models.Model):
    expiration_default_date = datetime.date.today() + datetime.timedelta(days=10)

    class Meta:
        indexes = [
            models.Index(fields=["shortcode"]),
            models.Index(fields=["fullname"]),
        ]

    description = models.CharField(max_length=256, null=False)
    shortcode = models.CharField(max_length=64, null=False)
    fullname = models.CharField(max_length=2048, null=False)
    name = models.CharField(max_length=512, null=False)
    query_params = models.CharField(max_length=1536, null=True)
    expiration = models.DateField(default=expiration_default_date, null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)


class Tracking(models.Model):
    url = models.ForeignKey(URL, on_delete=models.DO_NOTHING)
    requested = models.DateTimeField(auto_now_add=True)
