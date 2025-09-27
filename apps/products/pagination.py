# apps/products/pagination.py

"""
Pagination Configuration

Custom pagination classes for product APIs.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ProductPagination(PageNumberPagination):
    """
    Custom pagination for product listings
    """
    page_size = 20  # Default number of products per page
    page_size_query_param = 'page_size'
    max_page_size = 100  # Maximum products per page
    page_query_param = 'page'

    def get_paginated_response(self, data):
        """
        Return paginated response with additional metadata
        """
        return Response({
            'success': True,
            'pagination': {
                'count': self.page.paginator.count,
                'page_size': self.page_size,
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            },
            'results': data
        })


class LargeProductPagination(PageNumberPagination):
    """
    Pagination for admin views that might need more items
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    page_query_param = 'page'