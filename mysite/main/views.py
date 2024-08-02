from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from .models import SampleData, SampleAgentData
from .serializers import SampleDataSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models.functions import RowNumber
from django.db.models import (
    F,
    FloatField,
    ExpressionWrapper,
    Case,
    When,
    Value,
    IntegerField,
    FloatField,
    Window,
    Subquery,
    OuterRef,
    BooleanField,
)


class SampleDataListView(ListAPIView):
    queryset = SampleData.objects.all()
    serializer_class = SampleDataSerializer


# class SampleDataDetailView(APIView):
#     @swagger_auto_schema(
#         operation_description="Get a SampleData object by ID",
#         responses={200: SampleDataSerializer(), 404: "Not Found"},
#         manual_parameters=[openapi.Parameter("id", openapi.IN_PATH, description="매물 ID", type=openapi.TYPE_INTEGER)],
#     )
#     def get(self, request, id, format=None):
#         try:
#             sample_data = SampleData.objects.get(id=id)
#             serializer = SampleDataSerializer(sample_data)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except SampleData.DoesNotExist:
#             return Response({"error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class SampleDataDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Get a SampleData object by ID",
        responses={
            200: SampleDataSerializer(),
            404: "Not Found",
        },
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="매물 ID",
                type=openapi.TYPE_INTEGER,
            )
        ],
    )
    def get(self, request, format=None):
        id = request.GET.get("id")  # 쿼리 파라미터에서 'id'를 가져옴
        if id is None:
            return Response(
                {"error": "ID parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            sample_data = SampleData.objects.get(id=id)
            serializer = SampleDataSerializer(sample_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SampleData.DoesNotExist:
            return Response(
                {"error": "Not Found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError:
            return Response(
                {"error": "ID must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# 추천 알고리즘 적용된 매물들
# request: 필터링 항목들, 리스트 형태로 바꾸기 TYPE_ARRAY 있음
# response: 매물 목록, pagination
class SampleDataFilteringView(APIView):

    @swagger_auto_schema(
        operation_description="Get SampleData objects by filtering",
        responses={200: SampleDataSerializer(many=True), 404: "Not Found"},
        manual_parameters=[
            openapi.Parameter(
                "address",
                openapi.IN_QUERY,
                description="동네 입력",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "min_deposit",
                openapi.IN_QUERY,
                description="최소 보증금 입력",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "max_deposit",
                openapi.IN_QUERY,
                description="최대 보증금 입력",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "include_maintenance_fee",
                openapi.IN_QUERY,
                description="관리비 포함/미포함",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "min_rent",
                openapi.IN_QUERY,
                description="최소 월세 입력",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "max_rent",
                openapi.IN_QUERY,
                description="최대 월세 입력",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "facilities",
                openapi.IN_QUERY,
                description="편의시설 항목",
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING),
            ),
            openapi.Parameter(
                "floor_options",
                openapi.IN_QUERY,
                description="옥탑,반지하 포함 미포함",
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING),
            ),
        ],
    )
    def get(self, request, format=None):
        address = request.GET.get("address")
        min_deposit = request.GET.get("min_deposit")
        max_deposit = request.GET.get("max_deposit")
        include_maintenance_fee = request.GET.get("include_maintenance_fee") == "true"
        min_rent = request.GET.get("min_rent")
        max_rent = request.GET.get("max_rent")
        facilities = request.GET.get("facilities")
        floor_options = request.GET.get("floor_options")

        facility_info = {
            "편의점": "store_count",
            "지하철": "subway_count",
            "카페": "cafe_count",
            "대형마트": "market_count",
            "음식점": "restaurant_count",
            "병원": "hospital_count",
        }

        if not address:
            return Response(
                {"error": "address parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 기본 필터링 조건 적용
            queryset = SampleData.objects.filter(address__icontains=address)

            # 보증금 최소값 필터링 조건 추가
            if min_deposit is not None:
                try:
                    min_deposit_value = int(min_deposit)
                    queryset = queryset.filter(deposit__gte=min_deposit_value)
                except ValueError:
                    return Response(
                        {"error": "min_deposit must be an integer"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # 보증금 최대값 필터링 조건 추가
            if max_deposit is not None:
                try:
                    max_deposit_value = int(max_deposit)
                    queryset = queryset.filter(deposit__lte=max_deposit_value)
                except ValueError:
                    return Response(
                        {"error": "max_deposit must be an integer"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # 월세 최소값 필터링 조건 추가
            if min_rent is not None:
                try:
                    min_rent_value = int(min_rent)
                    if include_maintenance_fee:
                        queryset = queryset.annotate(
                            rent_plus_maintenance=ExpressionWrapper(
                                F("rent") + F("maintenance_fee"),
                                output_field=IntegerField(),
                            )
                        ).filter(rent_plus_maintenance__gte=min_rent_value)
                    else:
                        queryset = queryset.filter(rent__gte=min_rent_value)
                except ValueError:
                    return Response(
                        {"error": "min_rent must be an integer"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # 월세 최대값 필터링 조건 추가
            if max_rent is not None:
                try:
                    max_rent_value = int(max_rent)
                    if include_maintenance_fee:
                        queryset = queryset.annotate(
                            rent_plus_maintenance=ExpressionWrapper(
                                F("rent") + F("maintenance_fee"),
                                output_field=IntegerField(),
                            )
                        ).filter(rent_plus_maintenance__lte=max_rent_value)
                    else:
                        queryset = queryset.filter(rent__lte=max_rent_value)
                except ValueError:
                    return Response(
                        {"error": "max_rent must be an integer"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # 편의시설 필터링 조건 추가
            if facilities is not None:
                facilities = facilities.replace("'", "").split(",")
                for facility in facilities:
                    field_name = facility_info.get(facility)
                    if field_name:
                        queryset = queryset.filter(**{f"{field_name}__gte": 1})

            # 층 옵션 필터링 조건 추가
            if floor_options:
                if floor_options == "옥탑":
                    queryset = queryset.exclude(floor__icontains="반지")
                elif floor_options == "반지하":
                    queryset = queryset.exclude(floor__icontains="옥탑")
            else:
                queryset = queryset.exclude(floor__in=["옥탑", "반지"])

            # 편의시설 점수 계산
            queryset = queryset.annotate(
                market_score=Case(
                    When(market_count__gt=0, then=Value(3)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                restaurant_score=Case(
                    When(restaurant_count__lte=5, then=Value(1)),
                    When(
                        restaurant_count__gt=5, restaurant_count__lte=15, then=Value(2)
                    ),
                    When(restaurant_count__gt=15, then=Value(3)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                store_distance_score=Case(
                    When(nearest_store_distance__lte=100, then=Value(3)),
                    When(
                        nearest_store_distance__gt=100,
                        nearest_store_distance__lte=300,
                        then=Value(2),
                    ),
                    When(
                        nearest_store_distance__gt=300,
                        nearest_store_distance__lte=500,
                        then=Value(1),
                    ),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                cafe_distance_score=Case(
                    When(nearest_cafe_distance__lte=100, then=Value(3)),
                    When(
                        nearest_cafe_distance__gt=100,
                        nearest_cafe_distance__lte=300,
                        then=Value(2),
                    ),
                    When(
                        nearest_cafe_distance__gt=300,
                        nearest_cafe_distance__lte=500,
                        then=Value(1),
                    ),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                subway_score=Case(
                    When(subway_count__gt=0, then=Value(3)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                hospital_score=Case(
                    When(hospital_count__lte=8, then=Value(1)),
                    When(hospital_count__gt=8, hospital_count__lte=20, then=Value(2)),
                    When(hospital_count__gt=20, then=Value(3)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
            )

            # 편의시설 점수 합계 계산
            queryset = queryset.annotate(
                total_facility_score=F("market_score")
                + F("restaurant_score")
                + F("store_distance_score")
                + F("cafe_distance_score")
                + F("subway_score")
                + F("hospital_score")
            )

            # 월 지출비 계산
            queryset = queryset.annotate(
                monthly_expense=ExpressionWrapper(
                    (F("deposit") * 1 / 20 * 1 / 12) + F("rent") + F("maintenance_fee"),
                    output_field=FloatField(),
                )
            )

            # 월 지출비 순위 계산
            queryset = queryset.annotate(
                monthly_expense_rank=Window(
                    expression=RowNumber(),
                    order_by=F("monthly_expense").asc(),
                )
            )

            # 편의시설 점수 순위 계산
            queryset = queryset.annotate(
                facility_rank=Window(
                    expression=RowNumber(),
                    order_by=F("total_facility_score").desc(),
                )
            )

            # 최종 점수 계산
            queryset = queryset.annotate(
                final_score=ExpressionWrapper(
                    3 * F("monthly_expense_rank") + 2 * F("facility_rank"),
                    output_field=FloatField(),
                )
            ).order_by("final_score")

            # 안심 부동산 체크 (agent_code가 2, 3이고 자격증이 있는 경우(not null))
            queryset = queryset.annotate(
                easy_safe=Case(
                    When(
                        Subquery(
                            SampleAgentData.objects.filter(
                                registration_number=OuterRef('registration_number'),
                                agent_name=OuterRef('agent_name'),
                                agent_code__in=[2, 3],
                                certificate_number__isnull=False
                            ).values('id')[:1]    # 만족하는 레코드가 존재하는지 확인하기 위해
                        ).exists(),
                        then=Value(True)
                    ),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )

            if queryset.exists():
                serializer = SampleDataSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Not Found"}, status=status.HTTP_404_NOT_FOUND
                )
        except ValueError:
            return Response(
                {"error": "Invalid parameter"}, status=status.HTTP_400_BAD_REQUEST
            )
