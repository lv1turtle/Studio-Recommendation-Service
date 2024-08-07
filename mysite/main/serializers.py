from rest_framework import serializers
from .models import *


class PropertyDataSerializer(serializers.ModelSerializer):
    is_safe = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = "__all__"

    def get_is_safe(self, obj):
        return getattr(obj, "is_safe", False)


class SampleDataSerializer(serializers.ModelSerializer):
    final_score = serializers.SerializerMethodField()

    class Meta:
        model = SampleData
        fields = "__all__"

    def get_final_score(self, obj):
        # 계산된 최종 점수를 반환
        return obj.final_score


class SampleDataSerializer(serializers.ModelSerializer):
    market_score = serializers.FloatField(read_only=True)
    restaurant_score = serializers.FloatField(read_only=True)
    store_distance_score = serializers.FloatField(read_only=True)
    cafe_distance_score = serializers.FloatField(read_only=True)
    subway_score = serializers.FloatField(read_only=True)
    hospital_score = serializers.FloatField(read_only=True)
    monthly_expense = serializers.FloatField(read_only=True)
    total_facility_score = serializers.FloatField(read_only=True)
    monthly_expense_rank = serializers.IntegerField(read_only=True)
    facility_rank = serializers.IntegerField(read_only=True)
    final_score = serializers.FloatField(read_only=True)

    class Meta:
        model = SampleData
        fields = [
            "id",
            "address",
            "deposit",
            "rent",
            "market_count",
            "restaurant_count",
            "nearest_store_distance",
            "nearest_cafe_distance",
            "subway_count",
            "hospital_count",
            "market_score",
            "restaurant_score",
            "store_distance_score",
            "cafe_distance_score",
            "subway_score",
            "hospital_score",
            "monthly_expense",
            "total_facility_score",
            "monthly_expense_rank",
            "facility_rank",
            "final_score",
        ]
