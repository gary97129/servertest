from django.core.cache import cache
from rest_framework.permissions import BasePermission
from utils.queryset import get_child_queryset2
from .models import Organization, Permission
from django.db.models import Q

def get_permission_list(user):
    """
    獲取權限列表,可用redis存取
    """
    if user.is_superuser:
        perms_list = ['admin']
    else:
        perms = Permission.objects.none()
        roles = user.roles.all()
        if roles:
            for i in roles:
                perms = perms | i.perms.all()
        perms_list = perms.values_list('method', flat=True)
        perms_list = list(set(perms_list))
    cache.set(user.username + '__perms', perms_list, 60*60)
    return perms_list


class RbacPermission(BasePermission):
    """
    基於角色的權限校驗類
    """

    def has_permission(self, request, view):
        """
        權限校驗邏輯
        :param request:
        :param view:
        :return:
        """
        if not request.user:
            perms = ['visitor'] # 如果沒有經過認證,視為游客
        else:
            perms = cache.get(request.user.username + '__perms')
        if not perms:
            perms = get_permission_list(request.user)
        if perms:
            if 'admin' in perms:
                return True
            elif not hasattr(view, 'perms_map'):
                return True
            else:
                perms_map = view.perms_map
                _method = request._request.method.lower()
                if perms_map:
                    for key in perms_map:
                        if key == _method or key == '*':
                            if perms_map[key] in perms or perms_map[key] == '*':
                                return True
                return False
        else:
            return False
    
    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if not request.user:
            return False
        if hasattr(obj, 'belong_dept'):
            has_obj_perm(request.user, obj)
        return True

def has_obj_perm(user, obj):
    """
    數據權限控權
    返回對象的是否可以操作
    需要控數據權限的表需有belong_dept, create_by, update_by欄位(部門, 創建人, 編輯人)
    傳入user, obj實例
    """
    roles = user.roles
    data_range = roles.values_list('datas', flat=True)
    if '全部' in data_range:
        return True
    elif '自定義' in data_range:
        depts = Organization.objects.filter(roles__in = roles)
        if obj.belong_dept not in depts:
            return False
    elif '同級及以下' in data_range:
        if user.dept.parent:
            belong_depts = get_child_queryset2(user.dept.parent)
            if obj.belong_dept not in belong_depts:
                return False
    elif '本級及以下' in data_range:
        belong_depts = get_child_queryset2(user.dept)
        if obj.belong_dept not in belong_depts:
            return False
    elif '本級' in data_range:
        if obj.belong_dept is not user.dept:
            return False
    return True