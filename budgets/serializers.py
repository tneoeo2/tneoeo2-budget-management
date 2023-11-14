from rest_framework import serializers
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Category, Budgets

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        

class BudgetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budgets
        fields = ['category', 'amount', 'user', 'ratio']
        read_only_fields = ['ratio']
        
    def create(self, validated_data):
        print('validated_data[user]: ', validated_data['user'])
        # 유저의 총 예산
        total_budget = get_object_or_404(User, username=validated_data['user']).total
        # 사용자가 입력한 예산
        input_amount = validated_data['amount']
        # 총 예산이 0인 경우 0으로 설정 (분모가 0일 경우 예외 방지)
        ratio = 0.0 if total_budget == 0 else input_amount / total_budget
        # validated_data에 ratio 추가
        validated_data['ratio'] = round(ratio, 2)

        # Budgets 모델 생성
        budget = Budgets.objects.create(**validated_data)

        return budget    
        
        
        
class BudgetsRecSerializer(serializers.ModelSerializer):
    total = serializers.IntegerField(source='user.total',label='총예산')
    class Meta:
        model = Budgets
        fields = ['category', 'amount', 'user', 'total']
        # read_only_fields = ['category', 'amount', 'user', 'total']
        # read_only=True