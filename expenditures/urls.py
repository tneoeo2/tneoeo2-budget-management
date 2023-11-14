from django.urls import path
from .views import SetExpendituresListView,SetExpendituresDetailView
app_name = "expenditures"

urlpatterns = [
   path('',  SetExpendituresListView.as_view(), name='expenditures-crud'),
   path('<int:pk>/',  SetExpendituresDetailView.as_view(), name='expenditures-crud'),
]