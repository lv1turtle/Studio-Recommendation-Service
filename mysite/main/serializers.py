from rest_framework import serializers
from .models import SampleData


class SampleDataSerializer(serializers.ModelSerializer):
    is_safe = serializers.SerializerMethodField()

    class Meta:
        model = SampleData
        fields = "__all__"

    def get_is_safe(self, obj):
        return getattr(obj, "is_safe", False)
