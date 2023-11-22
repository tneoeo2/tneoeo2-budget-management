from rest_framework import serializers
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Category, Expenditure

User = get_user_model()

class ExpenditureSerializer(serializers.ModelSerializer):
    total = serializers.IntegerField(source='user.total', label='총지출액', read_only=True)
    class Meta:
        model = Expenditure
        fields = ['category', 'user', 'expense_amount', 'memo',  'is_except', 'total']

        
class ExpenditureDetailSerializer(serializers.ModelSerializer):
    total = serializers.IntegerField(source='user.total',label='총지출액', read_only=True)
    class Meta:
        model = Expenditure
        fields = ['category', 'expense_amount', 'memo', 'is_except', 'total']
        
        
class ExpenditureNotiSerializer(serializers.Serializer):        
    total = serializers.IntegerField(source='user.total',label='총지출액', read_only=True)
    class Meta:
        model = Expenditure
        fields = ['category', 'appropriate_amount','expense_amount', 'memo', 'is_except', 'total']
        