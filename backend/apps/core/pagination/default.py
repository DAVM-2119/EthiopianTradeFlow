from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    """
    Standardized DRF pagination class for TradeFlow API collections.
    Supports client configurable page size with a safe ceiling.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
