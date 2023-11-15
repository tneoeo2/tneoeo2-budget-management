from django.test import TransactionTestCase
from budgets.models import Category


class CategoryTestCase(TransactionTestCase):
    def setUp(self):
        # 카테고리 생성
        Category.objects.create(name='식비')
        Category.objects.create(name='패션')
        Category.objects.create(name='교통')
        Category.objects.create(name='건강')
        Category.objects.create(name='저축')
        Category.objects.create(name='문화생활')
        Category.objects.create(name='기타')

    def test_category_name(self):
        # 테스트 케이스 작성
        category = Category.objects.get(name='식비')
        self.assertEqual(category.name, '식비')
        
        print(Category.objects.all())

    # 다른 테스트 메서드들 추가 가능
