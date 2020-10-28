from rest_framework import serializers
from bonds.models import Bond


class BondSerializer(serializers.ModelSerializer):

    maturity = serializers.DateField(input_formats=["%Y-%m-%d"])
    currency = serializers.CharField(min_length=3, max_length=3)

    class Meta:
        model = Bond
        exclude = ["user"]
