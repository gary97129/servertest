from django.db.models import Q
from django.db.models.query import QuerySet
from rest_framework.generics import GenericAPIView
from apps.system.mixins import CreateUpdateModelBMixin
from apps.system.models import Organization
from utils.queryset import get_child_queryset2


class RbacFilterSet(CreateUpdateModelBMixin, object):
    """
    數據權限控權返回的queryset
    在必須的View下繼承
    需要控數據權限的表需有belong_dept, create_by, update_by欄位(部門, 創建人, 編輯人)
    帶性能優化
    包括必要的創建和編輯操作

    此處對性能有較大影響,根據業務需求進行修改或取捨
    """
    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        if hasattr(self.get_serializer_class(), 'setup_eager_loading'):
            queryset = self.get_serializer_class().setup_eager_loading(queryset)  # 性能優化
        
        if self.request.user.is_superuser:
            return queryset

        if hasattr(queryset.model, 'belong_dept'):
            user = self.request.user
            roles = user.roles
            data_range = roles.values_list('datas', flat=True)
            if '全部' in data_range:
                return queryset
            elif '自定義' in data_range:
                queryset = queryset.filter(belong_dept__roles__in=roles)
                return queryset
            elif '同級及以下' in data_range:
                if user.dept.parent:
                    belong_depts = get_child_queryset2(user.dept.parent)
                    queryset = queryset.filter(belong_dept__in = belong_depts)
                    return queryset
            elif '本級及以下' in data_range:
                belong_depts = get_child_queryset2(user.dept)
                queryset = queryset.filter(belong_dept__in = belong_depts)
                return queryset
            elif '本級' in data_range:
                queryset = queryset.filter(belong_dept = user.dept)
                return queryset
            elif '僅本人' in data_range:
                queryset = queryset.filter(Q(create_by=user)|Q(update_by=user))
                return queryset
        return queryset


def rbac_filter_queryset(user, queryset):
    """
    數據權限控權返回的queryset方法
    需要控數據權限的表需有belong_dept, create_by, update_by欄位(部門, 創建人, 編輯人)
    傳入user實例,queryset
    """
    if user.is_superuser:
        return queryset

    roles = user.roles
    data_range = roles.values_list('datas', flat=True)
    if hasattr(queryset.model, 'belong_dept'):
        if '全部' in data_range:
            return queryset
        elif '自定義' in data_range:
            if roles.depts.exists():
                queryset = queryset.filter(belong_dept__in = roles.depts)
                return queryset
        elif '同級及以下' in data_range:
            if user.dept.parent:
                belong_depts = get_child_queryset2(user.dept.parent)
                queryset = queryset.filter(belong_dept__in = belong_depts)
                return queryset
        elif '本級及以下' in data_range:
            belong_depts = get_child_queryset2(user.dept)
            queryset = queryset.filter(belong_dept__in = belong_depts)
            return queryset
        elif '本級' in data_range:
            queryset = queryset.filter(belong_dept = user.dept)
            return queryset
        elif '僅本人' in data_range:
            queryset = queryset.filter(Q(create_by=user)|Q(update_by=user))
            return queryset    
    return queryset

