from django.utils import timezone
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework import status

from config import settings
from .models import Category, Expenditure
from .filters import ExpenditureFilter
from .serializers import ExpenditureSerializer,ExpenditureDetailSerializer

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'

User = get_user_model()

# Create your views here.
class SetExpendituresListView(generics.ListCreateAPIView):  #, generics.RetrieveUpdateDestroyAPIView
    '''
     GET expenditures/ : 지출 목록 api
     POST expenditures/: 지출 api
    
    '''
    queryset = Expenditure.objects.all()
    serializer_class = ExpenditureSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExpenditureFilter

    
    def get_category_expense_summary(self, queryset):
        #* 월별 각 카테고리의 비용합계 보기 -> 월 미설정시 현재 달을 기본으로 한다.
        month= timezone.now().month     #기본 이번달로 지정
        try:
            month= self.request.query_params['month']     
        except Exception as e:
            print("month 이번달로 설정")
        try:
            print('self.request.query_params : ', self.request.query_params)
            category = self.request.query_params['category']
        except Exception as e: 
            category = None
        if category:
            summary = (
                queryset.filter(create_at__month=month, category=category)
                .values('category', month=ExtractMonth('create_at'))
                .annotate(total_expense=Sum('expense_amount'))
                .order_by('-total_expense')
            )
        else:
            summary = (
                queryset.filter(create_at__month=month)
                .values('category', month=ExtractMonth('create_at'))
                .annotate(total_expense=Sum('expense_amount'))
                .order_by('-total_expense')
            )
        
        return summary
    
    def get_expense_summary(self, queryset):
        #* 월별 총비용 합계보기
        try:
            month= self.request.query_params['month']     
        except Exception as e:
            month= timezone.now().month     #기본 이번달로 지정
        summary = (
            queryset.filter(create_at__month=month)
            .values(month=ExtractMonth('create_at'))
            .annotate(total_expense=Sum('expense_amount'))
        )
        return summary
    
    
    def get_total_summary(self, data):
        #* 조회된 데이터의 지출비용 총합 구하기
        print('data:', data)
        total_expense_sum = sum(item['total_expense'] for item in data)
        return total_expense_sum
            
        
    
    def get_data_list(self, queryset):
        month= timezone.now().month     #기본 이번달로 지정
        try:
            month= self.request.query_params['month']     
        except Exception as e:
            print("month 이번달로 설정")
        try:
            print('self.request.query_params : ', self.request.query_params)
            category = self.request.query_params['category']
        except Exception as e: 
            category = None
        if category:
            return queryset.filter(create_at__month=month, category=self.request.query_params['category']).values()
        else:
            return queryset.filter(create_at__month=month).values()

    
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        print('queryset: ', queryset)
        category_summary = self.get_category_expense_summary(queryset)
        # total_summary = self.get_expense_summary(queryset)
        total_summary = self.get_total_summary(list(category_summary))
        data_list = self.get_data_list(category_summary)
        data = {
            'data_list': data_list,
            'category_summary' : category_summary,
            'total_expenditures' : total_summary,
        }
        return Response(data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    
class SetExpendituresDetailView(generics.RetrieveUpdateDestroyAPIView):
    '''
    GET       expenditures/<int:pk>/  : 지출 상세 api
    PUT       expenditures/<int:pk>/  : 지출 내역 변경
    PATCH     expenditures/<int:pk>/  : 지출 내역 일부 수정
    DELETE    expenditures/<int:pk>/  : 지출 내역 삭제
    '''
    serializer_class = ExpenditureSerializer
    
    def get(self, request, *args, **kwargs):
        expenditure_id = self.kwargs['pk']
        expenditure = Expenditure.objects.get(pk=expenditure_id)
        serializer = self.get_serializer(expenditure)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        expenditure_id = self.kwargs['pk']
        expenditure = Expenditure.objects.get(pk=expenditure_id)
        
        category = request.data.get('category')
        expense_amount = request.data.get('expense_amount')
        memo = request.data.get('memo')
        
        data = {
            'category' : category,
            'expense_amount' : expense_amount,
            'memo' : memo
        }
        serializer = ExpenditureDetailSerializer(expenditure, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        expenditure_id = self.kwargs['pk']
        expenditure = Expenditure.objects.get(pk=expenditure_id)

        # 부분 업데이트를 위한 데이터 추출
        category = request.data.get('category')
        expense_amount = request.data.get('expense_amount')
        memo = request.data.get('memo')

        data = {}
        if category is not None:
            data['category'] = category
        if expense_amount is not None:
            data['expense_amount'] = expense_amount
        if memo is not None:
            data['memo'] = memo

        serializer = ExpenditureDetailSerializer(expenditure, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        expenditure_id = self.kwargs['pk']
        expenditure = Expenditure.objects.get(pk=expenditure_id)
        expenditure.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
