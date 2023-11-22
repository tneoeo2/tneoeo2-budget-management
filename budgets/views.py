import jwt
from datetime import datetime
from django.utils import timezone
from django.db.models import Sum, Count, Avg
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
from .serializers import CategorySerializer, BudgetsSerializer, BudgetsRecSerializer

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
        try:
            return Budgets.objects.get(user=user, category=category, create_at__month=current_month)
        except Budgets.DoesNotExist:
            return None
        
    def post(self, request, *args, **kwargs):
        try:
            token = request.headers.get("Authorization", "").split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            user_id = payload['user_id']
            if user_id is not None:
                user = get_object_or_404(User, id=user_id)
                category_id = request.data.get('category')
                amount = request.data.get('amount')
                current_month = timezone.now().month
                #총 예산 구하기
                # user_infos = Budgets.objects.filter(user_id=user_id)
                # total = user_infos.aggregate(total=Sum('amount'))['total']
                # print("total : " , total)
                # user.total = total
                # user.save() #유저 총액 업데이트
                # print('total 저장완료')
                # 이미 설정한 예산 정보가 있는지 확인
                instance = self.has_budget_for_month(user_id, category_id, current_month)
                if instance is not None:
                    return Response({'error': '해당 카테고리에 이미 설정한 예산 정보가 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = self.serializer_class(data={'user': user_id, 'category': category_id, 'amount': amount})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except jwt.InvalidTokenError:
            return Response({'error' : '권한이 없는 사용자입니다.'}, status.HTTP_401_UNAUTHORIZED) 
        
        
      
    def patch(self, request, *args, **kwargs):
        #예산 정보 수정
        try:
            token = request.headers.get("Authorization", "").split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            user_id = payload['user_id']
            if user_id is not None:
                user = get_object_or_404(User, id=user_id)
                category_id = request.data.get('category')
                amount = request.data.get('amount')
                current_month = timezone.now().month
             # 이미 설정한 예산 정보가 있는지 확인
                instance= self.has_budget_for_month(user_id, category_id, current_month)
                if instance is not None:
                    #총 예산 구하기
                    user_infos = Budgets.objects.filter(user_id=user_id)
                    total = user_infos.aggregate(total=Sum('amount'))['total']
                    user = User.objects.get(id=user_id)
                    user.total = total
                    user.save() #유저 총액 업데이트
                    
                    serializer = self.serializer_class(data={'user': user_id, 'category': category_id, 'amount': amount})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    raise ValueError('기존 데이터가 존재하지않습니다')
                return Response(serializer.data, status=status.HTTP_200_OK)
        except jwt.InvalidTokenError:
            return Response({'error' : '권한이 없는 사용자입니다.'}, status.HTTP_401_UNAUTHORIZED) 
        

class BudgetRecView(generics.ListCreateAPIView, mixins.UpdateModelMixin):
    '''
    POST budgets/rec : 카테고리별 예산 자동설정
    PATCH budgets/rec : 카고리별 총 예산 변경
    '''
    queryset = Budgets.objects.all()
    serializer_class = BudgetsRecSerializer
    # permission_classes = [IsAuthenticated,]
    
    def post(self, request, *args, **kwargs):
        "request : amount"
        try:
            token = request.headers.get("Authorization", "").split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            user_id = payload['user_id']
            
            if user_id is not None:
                total_amount = request.data.get('amount')   #유저가 입력한 총 예산
                serializer = BudgetsRecSerializer(data={'amount': total_amount}, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
        except jwt.InvalidTokenError:
            return Response({'error' : '권한이 없는 사용자입니다.'}, status.HTTP_401_UNAUTHORIZED) 
        
        return Response(serializer.data, status.HTTP_201_CREATED)
    
    def patch(self, request, *args, **kwargs):
        #예산 수동 변경시 사용
        try:
            token = request.headers.get("Authorization", "").split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            user_id = payload['user_id']
            
            if user_id is not None:
                total_amount = request.data.get('amount')   #유저가 입력한 총 예산
                serializer = BudgetsRecSerializer(data={'amount': total_amount}, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
        except jwt.InvalidTokenError:
            return Response({'error' : '권한이 없는 사용자입니다.'}, status.HTTP_401_UNAUTHORIZED) 
        
        
        return Response(serializer.data, status.HTTP_200_OK)