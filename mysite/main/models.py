from django.db import models


# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")


class SampleData(models.Model):
    room_id = models.CharField(max_length=100)
    platform = models.CharField(max_length=50)
    service_type = models.CharField(max_length=50)
    title = models.TextField(max_length=500)
    floor = models.CharField(max_length=50)
    area = models.FloatField()
    deposit = models.IntegerField()
    rent = models.IntegerField()
    maintenance_fee = models.IntegerField()
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    property_link = models.CharField(max_length=500)
    registration_number = models.CharField(max_length=100)
    agency_name = models.CharField(max_length=100)
    agent_name = models.CharField(max_length=100)
    subway_count = models.IntegerField()
    nearest_subway_distance = models.IntegerField()
    store_count = models.IntegerField()
    nearest_store_distance = models.IntegerField()
    cafe_count = models.IntegerField()
    nearest_cafe_distance = models.IntegerField()
    market_count = models.IntegerField()
    nearest_market_distance = models.IntegerField()
    restaurant_count = models.IntegerField()
    nearest_restaurant_distance = models.IntegerField()
    hospital_count = models.IntegerField()
    nearest_hospital_distance = models.IntegerField()
    image_link = models.CharField(max_length=500)

    def __str__(self):
        return f"방 제목: {self.title} 주소: {self.address}"


class agency_details(models.Model):
    registration_number = models.CharField(primary_key=True, max_length=100)
    agent_name = models.CharField(max_length=100)
    agent_code = models.IntegerField()
    position_code = models.IntegerField()
    certificate_number = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "agency_details"

    def __str__(self):
        return f"부동산 등록번호: {self.registration_number} 중개사 이름: {self.agent_name}"


class Property(models.Model):
    room_id = models.CharField(primary_key=True, max_length=100)
    platform = models.CharField(max_length=50)
    service_type = models.CharField(max_length=50)
    title = models.TextField(max_length=500)
    floor = models.CharField(max_length=50)
    area = models.FloatField()
    deposit = models.IntegerField()
    rent = models.IntegerField()
    maintenance_fee = models.IntegerField()
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    property_link = models.CharField(max_length=500)
    registration_number = models.CharField(max_length=100)
    agency_name = models.CharField(max_length=100)
    agent_name = models.CharField(max_length=100)
    subway_count = models.IntegerField()
    nearest_subway_distance = models.IntegerField()
    store_count = models.IntegerField()
    nearest_store_distance = models.IntegerField()
    cafe_count = models.IntegerField()
    nearest_cafe_distance = models.IntegerField()
    market_count = models.IntegerField()
    nearest_market_distance = models.IntegerField()
    restaurant_count = models.IntegerField()
    nearest_restaurant_distance = models.IntegerField()
    hospital_count = models.IntegerField()
    nearest_hospital_distance = models.IntegerField()
    image_link = models.CharField(max_length=500)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = "property"

    def __str__(self):
        return f"방 제목: {self.title} 주소: {self.address}, 포털:{self.platform}"
