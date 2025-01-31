from rest_framework import serializers
from .models import User
from data_manager.serializers import DataSerializer

class UserSerializer(serializers.ModelSerializer):
    data = DataSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = ['anki_uid', 'name', 'data']
        extra_kwargs = {'anki_uid': {'validators': []}}