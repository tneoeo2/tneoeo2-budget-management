import jwt
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework import generics, mixins
# from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework import status

from config import settings
from .models import Category, Budgets
from .serializers import CategorySerializer, BudgetsSerializer

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'

User = get_user_model()

class CategoryListView(generics.ListAPIView):
    '''
    GET budgets/category/ 
    '''
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get(self, request, *args, **kwargs):
        # GET 요청에 대한 처리
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(data={"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

   
class SetBudgetView(generics.ListCreateAPIView, mixins.UpdateModelMixin):
    '''
    POST budgets/: 예산설정, 예산의 카테고리 설정
    PATCH budgets/: 설정한 예산 변경
    '''
    queryset = Budgets.objects.all()
    serializer_class = BudgetsSerializer
    permission_classes = [IsAuthenticated,]
    
    def has_budget_for_month(self, user, category, current_month):
        # 해당 월에 동일 카테고리 예산 정보가 있는지 확인
        return Budgets.objects.filter(user=user, category=category, create_at__month=current_month).exists()
    
    def post(self, request, *args, **kwargs):
        # TODO: user는 같은 월에 하나의 catory-amount를 지정할 수 있다.
        
        try:
            token = request.headers.get("Authorization", "").split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            user_id = payload['user_id']
            if user_id is not None:
                category_id = request.data.get('category')
                amount = request.data.get('amount')
                current_month = timezone.now().month
                
                 # 이미 설정한 예산 정보가 있는지 확인
                if self.has_budget_for_month(user_id, category_id, current_month):
                    return Response({'error': '해당 카테고리에 이미 설정한 예산 정보가 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = self.serializer_class(data={'user': user_id, 'category': category_id, 'amount': amount})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except jwt.InvalidTokenError:
            return Response({'error' : '권한이 없는 사용자입니다.'}, status.HTTP_401_UNAUTHORIZED) 
        
        
      
    def patch(self, request, *args, **kwargs):
        
        def get_queryset(self):
            category = self.request.query_params.get('category')
            amount = self.request.query_params.get('amount')
            
        
        
        return self.partial_update(request, *args, **kwargs)