from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ParseError

class MyPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

class PageOrNot:
    def paginate_queryset(self, queryset):
        if (self.paginator is None):
            return None
        elif self.request.query_params.get('pageoff', None) and queryset.count()<500:
            return None
        elif self.request.query_params.get('pageoff', None) and queryset.count()>=500:
            raise ParseError('單次請求數據量大,請求中止')
        return self.paginator.paginate_queryset(queryset, self.request, view=self)
