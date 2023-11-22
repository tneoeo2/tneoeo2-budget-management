from django.db.models import Sum, Count, Avg
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
        # Budgets 모델 생성
        budget = Budgets.objects.create(**validated_data)

        return budget    
        
        
        
class BudgetsRecSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budgets
        fields = ['category', 'amount', 'user', 'ratio']
        read_only_fields = ['category', 'user', 'ratio']
        
    def create(self, validated_data):
        user_id = self.context['request'].user.id
        total_amount = int(validated_data.get('amount'))
        average_budgets = Budgets.objects.values('category').annotate(avg_amount=Avg('amount'))

        budget_list = []
        for budget in average_budgets:
            category = budget['category']
            avg_amount = int(budget['avg_amount'])
            
            # TODO: 비율....? 수정 필요한듯
            ratio = round((0.0 if total_amount == 0 else avg_amount / total_amount), 2)
            # user와 category가 동일한 인스턴스를 가져오거나 생성
            budget, created = Budgets.objects.get_or_create(user_id=user_id, category_id=category,
                                                            defaults={'amount': avg_amount, 'ratio': ratio})
            budget_list.append(budget)
            # 만약 인스턴스가 이미 존재한다면 (created == False), amount와 ratio 값을 업데이트
            if not created:
                budget.amount = avg_amount
                budget.ratio = ratio
                budget.save()
            
        
        return budget_list