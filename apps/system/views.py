import logging

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import (FileUploadParser, JSONParser,
                                    MultiPartParser)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError, ParseError
from utils.queryset import get_child_queryset2

from .filters import UserFilter
from .mixins import CreateUpdateModelAMixin, OptimizationMixin
from .models import (Dict, DictType, File, Organization, Permission, Position,
                     Role, User, Patient, Order, Doctor, Clinic, Laboratories,manufacturers)
from .permission import RbacPermission, get_permission_list
from .permission_data import RbacFilterSet
from .serializers import (DictSerializer, DictTypeSerializer, FileSerializer,
                          OrganizationSerializer, PermissionSerializer,
                          PositionSerializer, RoleSerializer, PTaskSerializer,PTaskCreateUpdateSerializer,
                          UserCreateSerializer, UserListSerializer,
                          UserModifySerializer, PatientSerializer, DoctorSerializer, ClinicSerializer, OrderListSerializer, LaboratoriesSerializer,manufacturersSerializer)
#綁定顯示
#from django.shortcuts import render
# from system.models import Role

logger = logging.getLogger('log')
# logger.info('請求成功！ response_code:{}；response_headers:{}；response_body:{}'.format(response_code, response_headers, response_body[:251]))
# logger.error('請求出錯-{}'.format(error))

from server.celery import app as celery_app

# def show_one(request):
#     #讀取一筆資料：cname =張三    
#     try:
#         item = Role.objects.get(name='醫生')
#     except Exception as e:
#         errormsg = '讀取資料出現錯誤：' + e
#     return render(request,'show_one.html',locals())

class TaskList(APIView):
    permission_classes = ()

    def get(self, requests):
        tasks = list(sorted(name for name in celery_app.tasks if not name.startswith('celery.')))
        return Response(tasks)

class LogoutView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):  # 可將token加入黑名單
        return Response(status=status.HTTP_200_OK)

class PTaskViewSet(OptimizationMixin, ModelViewSet):
    perms_map = {'get': '*', 'post': 'ptask_create',
                 'put': 'ptask_update', 'delete': 'ptask_delete'}
    queryset = PeriodicTask.objects.exclude(name__contains='celery.')
    serializer_class = PTaskSerializer
    search_fields = ['name']
    filterset_fields = ['enabled']
    ordering = ['-pk']

    @action(methods=['put'], detail=True, perms_map={'put':'task_update'},
            url_name='task_toggle')
    def toggle(self, request, pk=None):
        """
        修改啟用禁用狀態
        """
        obj = self.get_object()
        obj.enabled = False if obj.enabled else True
        obj.save()
        return Response(status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PTaskSerializer
        return PTaskCreateUpdateSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        timetype = data.get('timetype', None)
        interval_ = data.get('interval_', None)
        crontab_ = data.get('crontab_', None)
        if timetype == 'interval' and interval_:
            data['crontab'] = None
            try:
                interval, _ = IntervalSchedule.objects.get_or_create(**interval_, defaults = interval_)
                data['interval'] = interval.id
            except:
                raise ValidationError('時間策略有誤')
        if timetype == 'crontab' and crontab_:
            data['interval'] = None
            try:
                crontab_['timezone'] = 'Asia/Shanghai'
                crontab, _ = CrontabSchedule.objects.get_or_create(**crontab_, defaults = crontab_)
                data['crontab'] = crontab.id
            except:
                raise ValidationError('時間策略有誤')
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        data = request.data
        timetype = data.get('timetype', None)
        interval_ = data.get('interval_', None)
        crontab_ = data.get('crontab_', None)
        if timetype == 'interval' and interval_:
            data['crontab'] = None
            try:
                if 'id' in interval_:
                    del interval_['id']
                interval, _ = IntervalSchedule.objects.get_or_create(**interval_, defaults = interval_)
                data['interval'] = interval.id
            except:
                raise ValidationError('時間策略有誤')
        if timetype == 'crontab' and crontab_:
            data['interval'] = None
            try:
                crontab_['timezone'] = 'Asia/Shanghai'
                if 'id'in crontab_:
                    del crontab_['id'] 
                crontab, _ = CrontabSchedule.objects.get_or_create(**crontab_, defaults = crontab_)
                data['crontab'] = crontab.id
            except:
                raise ValidationError('時間策略有誤')
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class DictTypeViewSet(ModelViewSet):
    """
    數據字典類型-增刪改查
    """
    perms_map = {'get': '*', 'post': 'dicttype_create',
                 'put': 'dicttype_update', 'delete': 'dicttype_delete'}
    queryset = DictType.objects.all()
    serializer_class = DictTypeSerializer
    pagination_class = None
    search_fields = ['name']
    ordering_fields = ['pk']
    ordering = ['pk']


class DictViewSet(ModelViewSet):
    """
    數據字典-增刪改查
    """
    perms_map = {'get': '*', 'post': 'dict_create',
                 'put': 'dict_update', 'delete': 'dict_delete'}
    # queryset = Dict.objects.get_queryset(all=True) # 獲取全部的,包括軟刪除的
    queryset = Dict.objects.all()
    filterset_fields = ['type', 'is_used', 'type__code']
    serializer_class = DictSerializer
    search_fields = ['name']
    ordering_fields = ['sort']
    ordering = ['sort']

    def paginate_queryset(self, queryset):
        """
        如果查詢參數里沒有page但有type或type__code時則不分頁,否則請求分頁
        也可用utils.pageornot方法
        """
        if self.paginator is None:
            return None
        elif (not self.request.query_params.get('page', None)) and ((self.request.query_params.get('type__code', None)) or (self.request.query_params.get('type', None))):
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

class PositionViewSet(ModelViewSet):
    """
    崗位-增刪改查
    """
    perms_map = {'get': '*', 'post': 'position_create',
                 'put': 'position_update', 'delete': 'position_delete'}
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    pagination_class = None
    search_fields = ['name','description']
    ordering_fields = ['pk']
    ordering = ['pk']


class TestView(APIView):
    perms_map = {'get': 'test_view'}  # 單個API控權
    authentication_classes = []
    permission_classes = []
    def get(self, request, format=None):
        return Response('測試api介面')


class PermissionViewSet(ModelViewSet):
    """
    權限-增刪改查
    """
    perms_map = {'get': '*', 'post': 'perm_create',
                 'put': 'perm_update', 'delete': 'perm_delete'}
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = None
    search_fields = ['name']
    ordering_fields = ['sort']
    ordering = ['pk']


class OrganizationViewSet(ModelViewSet):
    """
    組織機構-增刪改查
    """
    perms_map = {'get': '*', 'post': 'org_create',
                 'put': 'org_update', 'delete': 'org_delete'}
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    pagination_class = None
    search_fields = ['name', 'type']
    ordering_fields = ['pk']
    ordering = ['pk']

class manufacturersViewSet(ModelViewSet):
    """
    植體廠牌-增刪改查
    """
    perms_map = {'get': '*', 'post': 'manufacturers_create',
                 'put': 'manufacturers_update', 'delete': 'manufacturers_delete'}
    queryset = manufacturers.objects.all()
    serializer_class = manufacturersSerializer
    pagination_class = None
    search_fields = ['name']
    ordering_fields = ['pk']
    ordering = ['pk']

class RoleViewSet(ModelViewSet):
    """
    角色-增刪改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    pagination_class = None
    search_fields = ['name']
    ordering_fields = ['pk']
    ordering = ['pk']

class PatientViewSet(ModelViewSet):
    """
    病患資料
    """
    perms_map = {'get': '*', 'post': 'patient_create',
                 'put': 'patient_update', 'delete': 'patient_delete'}
    queryset = Patient.objects.all()
    
    serializer_class = PatientSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['by_created'] = request.user
        serializer.validated_data['clinc_by_created'] = request.user.created_by
        serializer.save(by_created = self.request.user)
       
        return Response(serializer.data)
    
class OrderViewSet(ModelViewSet):
    """
    訂單資料
    """
    perms_map = {'get': '*', 'post': 'order_create',
                 'put': 'order_update', 'delete': 'order_delete'}
    queryset = Order.objects.all()
    
    serializer_class = OrderListSerializer
    pagination_class = None
    search_fields = ['name']
    ordering_fields = ['pk']
    ordering = ['pk']

    def create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        patient_id = request.data.get('patients', None)
        if patient_id is not None:
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer.validated_data['patients'] = patient


        serializer.validated_data['created_by'] = request.user
        serializer.validated_data['doctors'] = request.user
        serializer.validated_data['clinc_created_by'] = request.user.created_by
        user = User.objects.get(id=request.user.top_created_by_id)
        serializer.validated_data['Top_created_by'] = user            

        # Save the order
        order_instance = serializer.save(created_by=self.request.user)
        order_instance.save()


        serializer.save(created_by = self.request.user)
       
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class LaboratoriesViewSet(ModelViewSet):
    """
    技工所資料
    """
    perms_map = {'get': '*', 'post': 'Laboratories_create',
                 'put': 'Laboratories_update', 'delete': 'Laboratories_delete'}
    queryset = Laboratories.objects.all()
    
    serializer_class = LaboratoriesSerializer
    pagination_class = None
    search_fields = ['name']
    ordering_fields = ['pk']
    ordering = ['pk']

class ClinicViewSet(ModelViewSet):
    """
    診所資料
    """
    perms_map = {'get': '*', 'post': 'clinic_create',
                 'put': 'clinic_update', 'delete': 'clinic_delete'}
    queryset = Clinic.objects.all()
    
    serializer_class = ClinicSerializer
    pagination_class = None

class DoctorViewSet(ModelViewSet):
    """
    醫師資料
    """
    perms_map = {'get': '*', 'post': 'doctor_create',
                 'put': 'doctor_update', 'delete': 'doctor_delete'}
    queryset = Doctor.objects.all()
    
    serializer_class = DoctorSerializer
    pagination_class = None
    search_fields = ['name']
    ordering_fields = ['pk']
    ordering = ['pk']

class UserViewSet(ModelViewSet):
    """
    用戶管理-增刪改查
    """
    perms_map = {'get': '*', 'post': 'user_create',
                 'put': 'user_update', 'delete': 'user_delete'}
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    filterset_class = UserFilter
    search_fields = ['username', 'name', 'phone', 'email']
    ordering_fields = ['-pk']

    # def get_queryset(self):
    #     queryset = self.queryset
    #     if hasattr(self.get_serializer_class(), 'setup_eager_loading'):
    #         queryset = self.get_serializer_class().setup_eager_loading(queryset)  # 性能優化
    #     dept = self.request.query_params.get('dept', None)  # 該部門及其子部門所有員工
    #     if dept:
    #         deptqueryset = get_child_queryset2(Organization.objects.get(pk=dept))
    #         queryset = queryset.filter(dept__in=deptqueryset)
    #     return queryset

    def get_serializer_class(self):
        # 根據請求類型動態變更serializer
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'update':
            return UserModifySerializer
        elif self.action == 'list':
            return UserListSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        # 分別取出Tags表中第一條數據與Articles表中第一條數據進行關聯
        #tag = User.objects.get(pk=1)
        #system_user_roles = Role.objects.get(pk=1)
        #system_user_roles.users.add(tag)
        # 創建用戶默認添加密碼

        password = request.data['password'] if 'password' in request.data else None
        if password:
            password = make_password(password)
        else:
            password = make_password('0000')
        
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['created_by'] = request.user
        serializer.validated_data['top_created_by'] = request.user.created_by

        serializer.save(password=password)
       
        return Response(serializer.data)

    @action(methods=['put'], detail=False, permission_classes=[IsAuthenticated], # perms_map={'put':'change_password'}
            url_name='change_password')
    def password(self, request, pk=None):
        """
        修改密碼
        """
        user = request.user
        old_password = request.data['old_password']
        if check_password(old_password, user.password):
            new_password1 = request.data['new_password1']
            new_password2 = request.data['new_password2']
            if new_password1 == new_password2:
                user.set_password(new_password2)
                user.save()
                return Response('密碼修改成功!', status=status.HTTP_200_OK)
            else:
                return Response('新密碼兩次輸入不一致!', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('舊密碼錯誤!', status=status.HTTP_400_BAD_REQUEST)

    # perms_map={'get':'*'}, 自定義action控權
    @action(methods=['get'], detail=False, url_name='my_info', permission_classes=[IsAuthenticated])
    def info(self, request, pk=None):
        """
        初始化用戶信息
        """
        user = request.user
        perms = get_permission_list(user)
        data = {
            'id': user.id,
            'username': user.username,
            'created_by_id':user.created_by_id,

            'name': user.name,
            'roles': user.roles.values_list('name', flat=True),
            'avatar': user.avatar,
            'perms': perms,
        }
        return Response(data)

class FileViewSet(CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    """
    文件上傳用
    """
    perms_map = None
    permission_classes=[IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filterset_fields = ['type']
    search_fields = ['name']
    ordering = ['-create_time']

    def perform_create(self, serializer):
        fileobj = self.request.data.get('file')
        name = fileobj._name
        size = fileobj.size
        mime = fileobj.content_type
        type = '其它'
        if 'image' in mime:
            type = '圖片'
        elif 'video' in mime:
            type = '視頻'
        elif 'audio' in mime:
            type = '音頻'
        elif 'application' or 'text' in mime:
            type = '文檔'
        instance = serializer.save(create_by = self.request.user, name=name, size=size, type=type, mime=mime)
        instance.path = settings.MEDIA_URL + instance.file.name
        instance.save()
