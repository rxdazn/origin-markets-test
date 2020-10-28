from django.conf import settings
from django.db import models

from bonds.services import get_legal_name


class Bond(models.Model):
    isin = models.CharField(max_length=20)
    size = models.IntegerField()
    currency = models.CharField(max_length=3)
    maturity = models.DateField()
    lei = models.CharField(max_length=40)
    legal_name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.legal_name = get_legal_name(self.lei)
        return super().save(*args, **kwargs)
