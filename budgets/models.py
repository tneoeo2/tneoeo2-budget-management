from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name

class Budgets(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    ratio = models.DecimalField(default=0.0, decimal_places=2, max_digits=5)  #금액비율
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
        