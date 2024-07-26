from django.urls import path
from django.contrib import admin
from main import views


urlpatterns = [
    path("getAll/", views.SampleDataListView.as_view(), name="SampleDataListView"),
    path("getDetail/", views.SampleDataDetailView.as_view(), name="SampleDataDetailView"),
    path("getFilter/", views.SampleDataFilteringView.as_view(), name="SampleDataFilteringView"),
]
