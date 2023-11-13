from django.urls import path
from .views import CategoryListView, SetBudgetView

app_name = "budgets"

urlpatterns = [
   path('category/',  CategoryListView.as_view(), name='category_list'),
   path('',  SetBudgetView.as_view(), name='budgets'),
]