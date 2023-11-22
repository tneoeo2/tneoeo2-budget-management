import django_filters
from .models import Expenditure


class ExpenditureFilter(django_filters.FilterSet):
    min_expense_amount = django_filters.NumberFilter(field_name='expense_amount', lookup_expr='gte')
    max_expense_amount = django_filters.NumberFilter(field_name='expense_amount', lookup_expr='lte')

    
    class Meta:
        model = Expenditure
        fields = ['min_expense_amount', 'max_expense_amount']
        