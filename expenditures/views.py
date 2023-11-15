import jwt
from django.utils import timezone
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, TruncDate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework import status

from config import settings
from .models import Category, Expenditure, AppropriateExpenditure
from .filters import ExpenditureFilter
from .serializers import ExpenditureSerializer,ExpenditureDetailSerializer, ExpenditureNotiSerializer

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

    def get_user_info(self,request,*args, **kwargs):
        token = request.headers.get("Authorization", "").split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload['user_id']
        if user_id is not None:
            user = get_object_or_404(User, id=user_id)
            return user
        return  None    
    
    def get_total_expense_amount(self): 
        #모든 지출의 합 구하기
        total_expense = Expenditure.objects.aggregate(total=Sum('expense_amount'))['total']
        return total_expense if total_expense is not None else 0
    
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
                queryset.filter(create_at__month=month, category=category, is_except=False)
                .values('category', month=ExtractMonth('create_at'))
                .annotate(total_expense=Sum('expense_amount'))
                .order_by('-total_expense')
            )
        else:
            summary = (
                queryset.filter(create_at__month=month,is_except=False)
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
            queryset.filter(create_at__month=month, is_except=False)
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
        #* 데이터 추가
        user = self.get_user_info(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.total = self.get_total_expense_amount()
        # print("Total expense : ", user.total)
        user.save()
        return super().create(request, *args, **kwargs)

    
class SetExpendituresDetailView(generics.RetrieveUpdateDestroyAPIView):
    '''
    GET       expenditures/<int:pk>/  : 지출 상세 api
    PUT       expenditures/<int:pk>/  : 지출 내역 변경
    PATCH     expenditures/<int:pk>/  : 지출 내역 일부 수정
    DELETE    expenditures/<int:pk>/  : 지출 내역 삭제
    '''
    serializer_class = ExpenditureDetailSerializer
    
    def get_total_expense_amount(self): 
        #모든 지출의 합 구하기
        total_expense = Expenditure.objects.aggregate(total=Sum('expense_amount'))['total']
        return total_expense if total_expense is not None else 0
    
    def get_user_info(self,request,*args, **kwargs):
        token = request.headers.get("Authorization", "").split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload['user_id']
        if user_id is not None:
            user = get_object_or_404(User, id=user_id)
            return user
        return  None    
    
    def get(self, request, *args, **kwargs):
        expenditure_id = self.kwargs['pk']
        expenditure = Expenditure.objects.get(pk=expenditure_id)
        serializer = self.get_serializer(expenditure)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        expenditure_id = self.kwargs['pk']
        expenditure = Expenditure.objects.get(pk=expenditure_id)
        user = self.get_user_info(request)  #token에서 user 정보 받아오기
        
        category = request.data.get('category')
        expense_amount = request.data.get('expense_amount')
        memo = request.data.get('memo')
        is_except = request.data.get('is_except')
        user.total = self.get_total_expense_amount()
        # print("Total expense : ", user.total)
        user.save()
        
        data = {
            'category' : category,
            'expense_amount' : expense_amount,
            'memo' : memo,
            'is_except' :  is_except,
            'total' : user.total
            
        }
        serializer = ExpenditureDetailSerializer(expenditure, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = self.get_user_info(request)  #token에서 user 정보 받아오기
        expenditure_id = self.kwargs['pk']
        expenditure = Expenditure.objects.get(pk=expenditure_id)
        # 부분 업데이트를 위한 데이터 추출
        category = request.data.get('category')
        expense_amount = request.data.get('expense_amount')
        memo = request.data.get('memo')
        
        user.total = self.get_total_expense_amount()
        # print("Total expense : ", user.total)
        user.save()
        
        
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
        user = self.get_user_info(request)  #token에서 user 정보 받아오기
        expenditure_id = self.kwargs['pk']
        expenditure = Expenditure.objects.get(pk=expenditure_id)
        expenditure.delete()
        user.total = self.get_total_expense_amount()
        # print("Total expense : ", user.total)
        user.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpenditureNotiView(generics.ListAPIView):
    '''
    GET api/expenditures/noti : 오늘 지출 안내 api
    '''
    queryset = Expenditure.objects.all()
    serializer_class = ExpenditureNotiSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExpenditureFilter

    def get_user_info(self,request,*args, **kwargs):
        token = request.headers.get("Authorization", "").split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload['user_id']
        if user_id is not None:
            user = get_object_or_404(User, id=user_id)
            return user
        return  None    
    
    def get_category_expense_summary(self, queryset):
        today = timezone.now().date()  # 오늘날짜 가져오기
        try:
            category = self.request.query_params['category']
        except Exception as e:
            category = None

        if category:
            summary = (
                queryset.filter(
                    create_at__date=today,
                    category=category,
                    is_except=False
                )
                .values('category', date=TruncDate('create_at'))
                .annotate(total_expense=Sum('expense_amount'))
                .order_by('-total_expense')
            )
        else:
            summary = (
                queryset.filter(
                    create_at__date=today,
                    is_except=False
                )
                .values('category', date=TruncDate('create_at'))
                .annotate(total_expense=Sum('expense_amount'))
                .order_by('-total_expense')
            )

        return summary
    
    def get_expense_summary(self, queryset):
        today = timezone.now().date() 
        summary = (
            queryset.filter(create_at__date=today, is_except=False)
            .values(date=TruncDate('create_at'))
            .annotate(total_expense=Sum('expense_amount'))
        )

        return summary
    
    def get(self, request, *args, **kwargs):
        user = self.get_user_info(request) # 사용자 정보가져오기
        today_total = self.get_expense_summary(self.queryset)   #오늘 총 지출
        today_category_total = self.get_category_expense_summary(self.queryset)
        
        
        total_expense = list(today_total)[0]['total_expense']
        
        expenditure = Expenditure.objects.get(user_id=user)
        appropriate_amount_id= expenditure.appropriate_amount_id     # 적정예산정보 
        appropriate_expenditure = AppropriateExpenditure.objects.get(id=appropriate_amount_id)
        # print('appropriate_amount_id: ', appropriate_amount_id)
        # print('appropriate_expenditure: ', appropriate_expenditure.appropriate_amount)
        appropriate_amount = appropriate_expenditure.appropriate_amount
        caution = int(total_expense)/int(appropriate_amount)* 100   # n% 형식으로 출력
        
        
        data = {
            '오늘 총지출' : today_total,
            '카테고리 별 금액' : today_category_total,
            '월별 예산 기준 통계' : {
                '적정금액' : appropriate_amount_id,
                '지출금액' : today_total,
                '위험도' : caution
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)
        