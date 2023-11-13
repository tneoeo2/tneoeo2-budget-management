from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .models import Category, Budgets

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        

class BudgetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budgets
        fields = ['category', 'amount', 'user']