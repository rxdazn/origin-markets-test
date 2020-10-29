from rest_framework import serializers
from bonds.models import Bond


class BondSerializer(serializers.ModelSerializer):

    # users are not required to pass legal_name when creating a Bond
    legal_name = serializers.ReadOnlyField()
    maturity = serializers.DateField(input_formats=["%Y-%m-%d"])
    currency = serializers.CharField(min_length=3, max_length=3)

    class Meta:
        model = Bond
        exclude = ["user"]
