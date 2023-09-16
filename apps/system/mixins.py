from django.db.models.query import QuerySet

class CreateUpdateModelAMixin:
    """
    業務用基本表A用
    """
    def perform_create(self, serializer):
        serializer.save(create_by = self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(update_by = self.request.user)

class CreateUpdateModelBMixin:
    """
    業務用基本表B用
    """
    def perform_create(self, serializer):
        serializer.save(create_by = self.request.user, belong_dept=self.request.user.dept)
    
    def perform_update(self, serializer):
        serializer.save(update_by = self.request.user)

class CreateUpdateCustomMixin:
    """
    整合
    """
    def perform_create(self, serializer):
        if hasattr(self.queryset.model, 'belong_dept'):
            serializer.save(create_by = self.request.user, belong_dept=self.request.user.dept)
        else:
            serializer.save(create_by = self.request.user)
    def perform_update(self, serializer):
        serializer.save(update_by = self.request.user)

class OptimizationMixin:
    """
    性能優化,需要在序列化器里定義setup_eager_loading,可在必要的View下繼承
    """
    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        if hasattr(self.get_serializer_class(), 'setup_eager_loading'):
            queryset = self.get_serializer_class().setup_eager_loading(queryset)  # 性能優化
        return queryset

    