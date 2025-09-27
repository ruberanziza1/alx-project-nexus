

# apps/products/filters.py

"""
Product Filters - Simple category filtering
"""

import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """Product filter for category, price range, etc."""
    
    # Filter by category (exact match, case-insensitive)
    category = django_filters.CharFilter(field_name='category', lookup_expr='iexact')
    
    # Price range filters
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Stock filters
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    
    # Featured filter
    is_featured = django_filters.BooleanFilter(field_name='is_featured')
    
    class Meta:
        model = Product
        fields = ['category', 'is_featured']
    
    def filter_in_stock(self, queryset, name, value):
        """Filter products that are in stock"""
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset