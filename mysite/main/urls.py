from django.urls import path
from django.contrib import admin
from main import views


urlpatterns = [
    # path("getAll/", views.PropertyDataListView.as_view(), name="SampleDataListView"),
    path(
        "getDetail/",
        views.PropertyDataDetailView.as_view(),
        name="SampleDataDetailView",
    ),
    path(
        "getFilter/",
        views.PropertyDataFilteringView.as_view(),
        name="SampleDataFilteringView",
    ),
]
