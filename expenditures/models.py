from django.db import models
from django.contrib.auth import get_user_model
from budgets.models import Category



User = get_user_model()

class AppropriateExpenditure(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    appropriate_amount = models.IntegerField(default=0)  #적정금액 예산 기준/날짜 로 계산
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    constraints = [
        models.UniqueConstraint(fields=['user', 'category'], name='unique_user_category_expenditure'),
    ]
    
    def __str__(self):
        return str(self.appropriate_amount)


class Expenditure(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    appropriate_amount = models.ForeignKey(AppropriateExpenditure, on_delete=models.CASCADE, default=0)  #적정금액 예산 기준/날짜 로 계산
    expense_amount = models.IntegerField(default=0)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    memo = models.CharField(max_length=50, null=True)
    is_except = models.BooleanField(default=False)
    
     #유저 - 카테고리-적정금액 당 하나의 적정금액을 갖는다.
    # constraints = [
    #     models.UniqueConstraint(fields=['user', 'category', 'appropriate_amount'], name='unique_user_category_expenditure'),
    # ]
