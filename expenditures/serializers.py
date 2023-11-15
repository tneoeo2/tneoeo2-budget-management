from rest_framework import serializers
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Category, Expenditure

User = get_user_model()

class ExpenditureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expenditure
        fields = ['category', 'user', 'expense_amount', 'memo',  'is_except']

        
class ExpenditureDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expenditure
        fields = ['category', 'expense_amount', 'memo', 'is_except']
        