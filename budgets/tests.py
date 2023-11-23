from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Budgets, Category
from django.contrib.auth import get_user_model
from .views import BudgetRecView

User = get_user_model()

class BudgetAverageTest(APITestCase):
    #추천 API 카테고리별 예산 평균 테스트
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.category1 = Category.objects.create(name='Category 1')
        self.category2 = Category.objects.create(name='Category 2')
        Budgets.objects.create(user=self.user, category=self.category1, amount=100)
        Budgets.objects.create(user=self.user, category=self.category1, amount=200)
        Budgets.objects.create(user=self.user, category=self.category2, amount=300)
        
    def test_get_average_amount(self):
        # get_average_amount 함수를 테스트합니다.
        view = BudgetRecView()
        average_budgets = view.get_average_amount()
        print('average_budgets : ', average_budgets)
        # 예상 결과와 비교합니다.결과 맞는지 확인
        self.assertEqual(len(average_budgets), 2)
        
        for budget in average_budgets:
            category_name = budget['category']
            avg_amount = budget['avg_amount']
            
            if category_name == 'Category 1':
                self.assertEqual(avg_amount, 150)
            elif category_name == 'Category 2':
                self.assertEqual(avg_amount, 300)


class BudgetRecViewTest(APITestCase):
    #예산 추천API test
    def setUp(self):
        self.user_response = self.client.post(reverse('auths:signup'), {'username': 'testuser', 'password': 'testpassword'})
        self.user2 = User.objects.create(username='testuser2')
        self.category1 = Category.objects.create(name='Category 1')
        self.category2 = Category.objects.create(name='Category 2')
        self.category3 = Category.objects.create(name='Category 3')
        self.category4 = Category.objects.create(name='Category 4')
        self.user = User.objects.get(username='testuser')
        print('self.user : ', self.user)
        Budgets.objects.create(user=self.user, category=self.category1, amount=100)
        Budgets.objects.create(user=self.user2, category=self.category1, amount=200)
        Budgets.objects.create(user=self.user, category=self.category2, amount=300)
        Budgets.objects.create(user=self.user2, category=self.category3, amount=300)
        Budgets.objects.create(user=self.user, category=self.category3, amount=400)
        Budgets.objects.create(user=self.user2, category=self.category4, amount=100)
        Budgets.objects.create(user=self.user, category=self.category4, amount=300)
        
        self.login_response = self.client.post(reverse('auths:jwt-login'), {'username': 'testuser', 'password': 'testpassword'})
        #토큰받아오기
        self.access_token = self.login_response.data['access']
        
    def test_post_request(self):
        response = self.client.post(reverse('budgets:budgets-recommend'), {'user': 1,'category':1, 'amount': 1000}, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        print('post:', response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_patch_request(self):
        response = self.client.patch(reverse('budgets:budgets-recommend'), {'user': 1, 'category': 'Category 1', 'amount': 2000}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        print('patch:', response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
