from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include('auths.urls')),
    path("api/budgets/", include('budgets.urls')),
    path("api/expenditures/", include('expenditures.urls')),
]
