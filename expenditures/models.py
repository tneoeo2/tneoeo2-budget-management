from django.db import models
from django.contrib.auth import get_user_model
from budgets.models import Category



User = get_user_model()


class Expenditure(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    appropriate_amount = models.IntegerField(default=0)  #적정금액 예산 기준/날짜 로 계산
    expense_amount = models.IntegerField(default=0)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    memo = models.CharField(max_length=50, null=True)
    is_except = models.BooleanField(default=False)
