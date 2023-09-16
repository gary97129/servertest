

from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule
from rest_framework import serializers

from .models import (Dict, DictType, File, Organization, Permission, Position,
                     Role, User, Patient, Order, Doctor, Clinic, Laboratories,manufacturers)

class IntervalSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntervalSchedule
        fields = '__all__'

class CrontabSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrontabSchedule
        exclude = ['timezone']

class PTaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicTask
        fields = ['name', 'task', 'interval', 'crontab', 'args', 'kwargs']

class PTaskSerializer(serializers.ModelSerializer):
    interval_ = IntervalSerializer(source='interval', read_only=True)
    crontab_ = CrontabSerializer(source='crontab', read_only=True)
    schedule = serializers.SerializerMethodField()
    timetype = serializers.SerializerMethodField()
    class Meta:
        model = PeriodicTask
        fields = '__all__'
    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.select_related('interval','crontab')
        return queryset
    
    def get_schedule(self, obj):
        if obj.interval:
            return obj.interval.__str__()
        if obj.crontab:
            return obj.crontab.__str__()
        return ''
    
    def get_timetype(self, obj):
        if obj.interval:
            return 'interval'
        if obj.crontab:
            return 'crontab'
        return 'interval'

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"

class DictTypeSerializer(serializers.ModelSerializer):
    """
    數據字典類型序列化
    """
    class Meta:
        model = DictType
        fields = '__all__'


class DictSerializer(serializers.ModelSerializer):
    """
    數據字典序列化
    """
    class Meta:
        model = Dict
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    """
    崗位序列化
    """
    class Meta:
        model = Position
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    """
    角色序列化
    """
    class Meta:
        model = Role
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    """
    權限序列化
    """
    class Meta:
        model = Permission
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    """
    組織架構序列化
    """
    type = serializers.ChoiceField(
        choices=Organization.organization_type_choices, default='部門')

    class Meta:
        model = Organization
        fields = '__all__'

class manufacturersSerializer(serializers.ModelSerializer):
    """
    植牙廠牌序列化
    """
    class Meta:
        model = manufacturers
        fields = '__all__'

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name']

class UserListSerializer(serializers.ModelSerializer):
    """
    用戶列表序列化
    """
    roles_name = serializers.StringRelatedField(source='roles', many=True)
    class Meta:
        model = User
        fields = '__all__'

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related('roles')
        return queryset

class PatientSerializer(serializers.ModelSerializer):
    """
    病患資料序列化
    """
    class Meta:
        model = Patient
        fields = ['id', 'name', 'gender', 'Medical_record_number', 'Drug_allergy',
                  'phone', 'date_birth', 'remark','by_created', 'clinc_by_created']

class OrderListSerializer(serializers.ModelSerializer):
    """
    訂單列表序列化
    """
    #patient_name = serializers.StringRelatedField(source='roles', many=True)
    class Meta:
        model = Order
        fields = ['id', 'Order_Status', 'clinic', 'doctor', 'address', 'phone','created_by','patient','clinc_created_by','Top_created_by_id','design',
                  'Implant_Surgical_Board', 'Implant_Surgical_Board_temporary_tooth', 'Positioning_plate', 'Payment_method', 'Palate_weardate', 'Palate_surgery_date', 'Jaw_weardate', 'Jaw_surgery_date',
                  'Positioning_plate_palate_date', 'Positioning_plate_jaw_date', 'CBCT_order_method', 'Surgical_board_STL_order_method', 'Dental_implant_type', 'Surgical_board_Natural_teeth', 'Surgical_board_Metal_scattering', 'Order_Type',
                  'Equipment_rental', 'Surgical_method', 'Temporary_tooth', 'tooth_position', 'Surgical_board_remark', 'Positioning_plate_STL_order_method', 'Positioning_plate_Natural_teeth', 'Positioning_plate_Metal_scattering',
                  'Positioning_plate_remark', 

                'T11_Implant_brand', 'T11_Implant_size', 'T12_Implant_brand', 'T12_Implant_size', 'T13_Implant_brand', 'T13_Implant_size', 'T14_Implant_brand', 'T14_Implant_size',
                'T15_Implant_brand', 'T15_Implant_size', 'T16_Implant_brand', 'T16_Implant_size', 'T17_Implant_brand', 'T17_Implant_size', 'T18_Implant_brand', 'T18_Implant_size',
                'T21_Implant_brand', 'T21_Implant_size', 'T22_Implant_brand', 'T22_Implant_size', 'T23_Implant_brand', 'T23_Implant_size', 'T24_Implant_brand', 'T24_Implant_size',
                'T25_Implant_brand', 'T25_Implant_size', 'T26_Implant_brand', 'T26_Implant_size', 'T27_Implant_brand', 'T27_Implant_size', 'T28_Implant_brand', 'T28_Implant_size',
                'T31_Implant_brand', 'T31_Implant_size', 'T32_Implant_brand', 'T32_Implant_size', 'T33_Implant_brand', 'T33_Implant_size', 'T34_Implant_brand', 'T34_Implant_size',
                'T35_Implant_brand', 'T35_Implant_size', 'T36_Implant_brand', 'T36_Implant_size', 'T37_Implant_brand', 'T37_Implant_size', 'T38_Implant_brand', 'T38_Implant_size',
                'T41_Implant_brand', 'T41_Implant_size', 'T42_Implant_brand', 'T42_Implant_size', 'T43_Implant_brand', 'T43_Implant_size', 'T44_Implant_brand', 'T44_Implant_size',
                'T45_Implant_brand', 'T45_Implant_size', 'T46_Implant_brand', 'T46_Implant_size', 'T47_Implant_brand', 'T47_Implant_size', 'T48_Implant_brand', 'T48_Implant_size',


                  'avatar_3d_palate','avatar_3d_palate_Denture',
                  'avatar_3d_jaw','avatar_3d_jaw_Denture',
                  'avatar_CT','avatar_image1','avatar_image2','avatar_image3','avatar_image4','avatar_image5','avatar_image6','avatar_image7','avatar_image8','avatar_image9','avatar_project' ]



# class OrderSerializer(serializers.ModelSerializer):
#     """
#     訂單資訊序列化
#     """
#     # patient_name = serializers.StringRelatedField(source='patients', many=True)
#     class Meta:
#         model = Order
#         fields = '__all__'

class LaboratoriesSerializer(serializers.ModelSerializer):
    """
    技工所資訊序列化
    """
    class Meta:
        model = Laboratories
        fields = '__all__'

class ClinicSerializer(serializers.ModelSerializer):
    """
    診所資訊序列化
    """
    class Meta:
        model = Clinic
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):
    """
    醫師資訊序列化
    """
    class Meta:
        model = Doctor
        fields = '__all__'

class UserModifySerializer(serializers.ModelSerializer):
    """
    用戶編輯序列化
    """
    phone = serializers.CharField(max_length=11, required=False)

    class Meta:
        model = User
        fields = ['id', 'phone', 'email', 'type', 'title_name', 'Unified_compilation',
                  'username', 'is_active', 'date_joined', 'roles', 'role', 'avatar', 'address','payment_method']

    # def validate_phone(self, phone):
    #     re_phone = '^1[358]\d{9}$|^147\d{8}$|^176\d{8}$'
    #     if not re.match(re_phone, phone):
    #         raise serializers.ValidationError('手機號碼不合法')
    #     return phone


class UserCreateSerializer(serializers.ModelSerializer):
    """
    創建用戶序列化
    """
    username = serializers.CharField(required=True)
    # phone = serializers.CharField(max_length=11, required=False)

    class Meta:
        model = User
        fields = ['id', 'phone', 'email', 'type', 'title_name', 'Unified_compilation',
                  'username', 'is_active', 'date_joined', 'roles', 'avatar', 'address','payment_method', 'role', 'created_by']
        #不可用all，因為密碼是透過後端給予，不是前端匯入

    def validate_username(self, username):
        if User.objects.filter(username=username):
            raise serializers.ValidationError(username + ' 帳號已存在')
        return username

    # def validate_phone(self, phone):
    #     re_phone = '^1[358]\d{9}$|^147\d{8}$|^176\d{8}$'
    #     if not re.match(re_phone, phone):
    #         raise serializers.ValidationError('手機號碼不合法')
    #     if User.objects.filter(phone=phone):
    #         raise serializers.ValidationError('手機號已經被註冊')
    #     return phone
