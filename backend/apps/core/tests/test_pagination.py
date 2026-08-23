from apps.core.pagination import StandardResultsSetPagination

def test_standard_pagination_attributes():
    paginator = StandardResultsSetPagination()
    assert paginator.page_size == 20
    assert paginator.max_page_size == 100
    assert paginator.page_size_query_param == 'page_size'
