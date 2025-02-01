from rest_framework import serializers
from .models import Data

class DataSerializer(serializers.ModelSerializer):
    period = serializers.ChoiceField(
        choices=['day', 'week', 'month', 'alltime'],
        required=True
    )
    sort_by = serializers.ChoiceField(
        choices=['reviews', 'streak', 'retention'],
        required=True
    )

    class Meta:
        model = Data
        fields = ('period', 'sort_by')