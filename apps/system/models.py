from unicodedata import name
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.base import Model
import django.utils.timezone as timezone
from django.db.models.query import QuerySet

from utils.model import SoftModel, BaseModel
from simple_history.models import HistoricalRecords

class Permission(SoftModel):
    """
    功能權限:目錄,菜單,介面
    """
    menu_type_choices = (
        ('目錄', '目錄'),
        ('菜單', '菜單'),
        ('介面', '介面')
    )
    name = models.CharField('名稱', max_length=30)
    type = models.CharField('類型', max_length=20,
                            choices=menu_type_choices, default='介面')
    is_frame = models.BooleanField('外部鏈接', default=False)
    sort = models.IntegerField('排序標記', default=1)
    parent = models.ForeignKey('self', null=True, blank=True,
                            on_delete=models.SET_NULL, verbose_name='父')
    method = models.CharField('方法/代號', max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '功能權限表'
        verbose_name_plural = verbose_name
        ordering = ['sort']


class Organization(SoftModel):
    """
    組織架構
    """
    organization_type_choices = (
        ('公司', '公司'),
        ('部門', '部門')
    )
    name = models.CharField('名稱', max_length=60)
    type = models.CharField('類型', max_length=20,
                            choices=organization_type_choices, default='部門')
    parent = models.ForeignKey('self', null=True, blank=True,
                            on_delete=models.SET_NULL, verbose_name='父')

    class Meta:
        verbose_name = '組織架構'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Role(SoftModel):
    """
    角色
    """
    data_type_choices = (
        ('全部', '全部'),
        ('自定義', '自定義'),
        ('同級及以下', '同級及以下'),
        ('本級及以下', '本級及以下'),
        ('本級', '本級'),
        ('僅本人', '僅本人')
    )
    name = models.CharField('角色', max_length=32, unique=True)
    perms = models.ManyToManyField(Permission, blank=True, verbose_name='功能權限')
    datas = models.CharField('數據權限', max_length=50,
                             choices=data_type_choices, default='本級及以下')
    depts = models.ManyToManyField(
        Organization, blank=True, verbose_name='權限範圍', related_name='roles')
    description = models.CharField('描述', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class manufacturers(SoftModel):
    """
    植牙廠牌
    """
    name = models.CharField('名稱', max_length=32, unique=False)
    parentId = models.IntegerField('樹狀', blank=True,null=True)
    long = models.CharField('長度', max_length=50,null=True)

class Position(BaseModel):
    """
    職位/崗位
    """
    name = models.CharField('名稱', max_length=32, unique=True)
    description = models.CharField('描述', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = '職位/崗位'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Laboratories(SoftModel):
    """
    技工所
    """
    name = models.CharField('技工所名稱', max_length=32, unique=False)
    title_name = models.CharField('抬頭', max_length=32, unique=False)
    Unified_compilation = models.CharField('統一編號', max_length=32, unique=False)
    phone_number = models.CharField('電話', null=True, max_length=32, unique=True)
    address = models.CharField('地址', null=True, max_length=100, unique=True)
    payment_method = models.CharField('收款方式', null=True, max_length=32, unique=False)
    roles = models.ManyToManyField(Role, blank=True, verbose_name='角色')
    
    class Meta:
        verbose_name = '技工所'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name   

class Clinic(SoftModel):
    """
    診所
    """
    name = models.CharField('診所名稱', max_length=32, unique=False)
    title_name = models.CharField('抬頭', max_length=32, unique=False)
    Unified_compilation = models.CharField('統一編號', max_length=32, unique=False)
    phone_number = models.CharField('電話', null=True, max_length=32, unique=True)
    address = models.CharField('地址', null=True, max_length=100, unique=True)
    payment_method = models.CharField('收款方式', null=True, max_length=32, unique=False)
    roles = models.ManyToManyField(Role, blank=True, verbose_name='角色')
    
    class Meta:
        verbose_name = '診所'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name    

class Doctor(SoftModel):
    """
    醫師
    """
    name = models.CharField('醫師名稱', max_length=32, unique=False)
    email = models.CharField('電子郵件', null=True, max_length=32, unique=False)
    phone_number = models.CharField('手機號碼', null=True, max_length=32, unique=True)
    type = models.CharField('類型', null=False, max_length=100)
    payment_method = models.CharField('入單方式', null=True, max_length=32, unique=False)
    clinic = models.ManyToManyField(Clinic, blank=True, verbose_name='診所')
    roles = models.ManyToManyField(Role, blank=True, verbose_name='角色')
    
    class Meta:
        verbose_name = '醫師'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name  

class DictType(SoftModel):
    """
    數據字典類型
    """
    name = models.CharField('名稱', max_length=30)
    code = models.CharField('代號', unique=True, max_length=30)
    parent = models.ForeignKey('self', null=True, blank=True,
                            on_delete=models.SET_NULL, verbose_name='父')

    class Meta:
        verbose_name = '字典類型'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Dict(SoftModel):
    """
    數據字典
    """
    name = models.CharField('名稱', max_length=60)
    code = models.CharField('編號', max_length=30, null=True, blank=True)
    description = models.TextField('描述', blank=True, null=True)
    type = models.ForeignKey(
        DictType, on_delete=models.CASCADE, verbose_name='類型')
    sort = models.IntegerField('排序', default=1)
    parent = models.ForeignKey('self', null=True, blank=True,
                            on_delete=models.SET_NULL, verbose_name='父')
    is_used = models.BooleanField('是否有效', default=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = '字典'
        verbose_name_plural = verbose_name
        unique_together = ('name', 'is_used', 'type')

    def __str__(self):
        return self.name

class User(AbstractUser):
    """
    用戶
    """
    name = models.CharField('使用者名稱', max_length=20, null=True, blank=True)
    phone = models.CharField('手機號碼', max_length=11, null=True, blank=True)
    avatar = models.CharField('頭像', default='/media/default/avatar.png', max_length=100, null=True, blank=True)
    address = models.CharField('地址', null=True, max_length=100, blank=True)
    payment_method = models.CharField('收款方式', null=True, max_length=32, blank=True)
    role = models.CharField(null=True, max_length=100, help_text='角色, 醫師, 診所, 技工所')
    roles = models.ManyToManyField(Role, blank=True, verbose_name='角色')
    email = models.CharField('電子郵件', null=True, max_length=32, blank=True)
    type = models.CharField('職務類型', null=True, max_length=100, blank=True)
    title_name = models.CharField('抬頭', null=True, max_length=32, blank=True)
    Unified_compilation = models.CharField('統一編號', null=True, max_length=32, blank=True)
    parentId = models.CharField('上下級', max_length=32, blank=True,default=0)
    created_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='創建者', related_name='created_users')
    top_created_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='上級創建者', related_name='top_created_users')
    

    class Meta:
        verbose_name = '用戶信息'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.username

class CommonAModel(SoftModel):
    """
    業務用基本表A,包含create_by, update_by欄位
    """
    create_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='創建人', related_name= '%(class)s_create_by')
    update_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='最後編輯人', related_name= '%(class)s_update_by')

    class Meta:
        abstract = True

class CommonBModel(SoftModel):
    """
    業務用基本表B,包含create_by, update_by, belong_dept欄位
    """
    create_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='創建人', related_name = '%(class)s_create_by')
    update_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='最後編輯人', related_name = '%(class)s_update_by')
    belong_dept = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='所屬部門', related_name= '%(class)s_belong_dept')

    class Meta:
        abstract = True

class Patient(SoftModel):
    """
    病患資料
    """
    name = models.CharField('病患名稱', max_length=32, unique=False)
    gender = models.CharField('性別', max_length=32, unique=False)
    date_birth = models.CharField('出生年月日', max_length=32, unique=False)
    Medical_record_number = models.CharField('病歷號', null=True, max_length=32, unique=True)
    Drug_allergy = models.CharField('藥物過敏', null=True, max_length=32, unique=False)
    phone = models.CharField('電話', null=True, max_length=32, unique=False)
    remark = models.CharField('備註', null=True, max_length=64, unique=False)
    by_created = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='創建者', related_name='created_patient')
    clinc_by_created = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='上級創建者', related_name='clinc_by_created')
    
    class Meta:
        verbose_name = '病患名稱'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Order(SoftModel):
    """
    訂單資訊
    """
    order_number = models.CharField('訂單號',null=True, max_length=32, unique=False)
    clinic = models.CharField('診所', null=True, max_length=32, unique=False)
    doctor = models.CharField('醫師', max_length=32, unique=False)
    patient = models.CharField('病患名稱', null=True, max_length=32, unique=False)
    #第一介面存取
    address = models.CharField('收件地址', null=True, max_length=32, unique=False)
    phone = models.CharField('電話號碼', null=True, max_length=32, unique=False)
    Implant_Surgical_Board = models.CharField('產品項目_植牙手術版', null=True, max_length=32, unique=False)
    Implant_Surgical_Board_temporary_tooth = models.CharField('產品項目_植牙手術版+臨時牙冠', null=True, max_length=32, unique=False)
    Positioning_plate = models.CharField('產品項目_定位板', null=True, max_length=32, unique=False)
    Payment_method = models.CharField('付款方式', null=True, max_length=32, unique=False)
    #第二介面存取
    Palate_weardate = models.CharField('植牙手術板上顎裝戴日期', null=True, max_length=32, unique=False)
    Palate_surgery_date = models.CharField('植牙手術板上顎手術日期', null=True, max_length=32, unique=False)
    Jaw_weardate = models.CharField('植牙手術板下顎裝戴日期', null=True, max_length=32, unique=False)
    Jaw_surgery_date = models.CharField('植牙手術板下顎手術日期', null=True, max_length=32, unique=False)
    Positioning_plate_palate_date = models.CharField('定位板上顎裝戴日期', null=True, max_length=32, unique=False)
    Positioning_plate_jaw_date = models.CharField('定位板下顎裝戴日期', null=True, max_length=32, unique=False)
    #第三介面存取
    CBCT_order_method = models.CharField('CBCT入單方式', null=True, max_length=32, unique=False)
    Surgical_board_STL_order_method = models.CharField('手術板STL入單方式', null=True, max_length=32, unique=False)
    Dental_implant_type = models.CharField('手術植牙類型', null=True, max_length=32, unique=False)
    Surgical_board_Natural_teeth = models.CharField('手術板自然牙', null=True, max_length=32, unique=False)
    Surgical_board_Metal_scattering = models.CharField('手術板金屬散射', null=True, max_length=32, unique=False)
    Order_Type= models.CharField('訂單類型', null=True, max_length=32, unique=False)
    Equipment_rental = models.CharField('租借器械', null=True, max_length=32, unique=False)
    Surgical_method = models.CharField('手術方式', null=True, max_length=32, unique=False)
    Temporary_tooth = models.CharField('臨牙', null=True, max_length=32, unique=False)
    tooth_position = models.CharField('齒位', null=True, max_length=32, unique=False)
    Surgical_board_remark = models.CharField('手術板備註', null=True, max_length=512, unique=False, blank=True)
    T11_Implant_brand = models.TextField('T11植體廠牌', null=True, max_length=256, unique=False)
    T11_Implant_size = models.TextField('T11植體廠牌尺寸', null=True, max_length=256, unique=False)
    T12_Implant_brand = models.TextField('T12植體廠牌', null=True, max_length=256, unique=False)
    T12_Implant_size = models.TextField('T12植體廠牌尺寸', null=True, max_length=256, unique=False)
    T13_Implant_brand = models.TextField('T13植體廠牌', null=True, max_length=256, unique=False)
    T13_Implant_size = models.TextField('T13植體廠牌尺寸', null=True, max_length=256, unique=False)
    T14_Implant_brand = models.TextField('T14植體廠牌', null=True, max_length=256, unique=False)
    T14_Implant_size = models.TextField('T14植體廠牌尺寸', null=True, max_length=256, unique=False)
    T15_Implant_brand = models.TextField('T15植體廠牌', null=True, max_length=256, unique=False)
    T15_Implant_size = models.TextField('T15植體廠牌尺寸', null=True, max_length=256, unique=False)
    T16_Implant_brand = models.TextField('T16植體廠牌', null=True, max_length=256, unique=False)
    T16_Implant_size = models.TextField('T16植體廠牌尺寸', null=True, max_length=256, unique=False)
    T17_Implant_brand = models.TextField('T17植體廠牌', null=True, max_length=256, unique=False)
    T17_Implant_size = models.TextField('T17植體廠牌尺寸', null=True, max_length=256, unique=False)
    T18_Implant_brand = models.TextField('T18植體廠牌', null=True, max_length=256, unique=False)
    T18_Implant_size = models.TextField('T18植體廠牌尺寸', null=True, max_length=256, unique=False)
    T21_Implant_brand = models.TextField('T21植體廠牌', null=True, max_length=256, unique=False)
    T21_Implant_size = models.TextField('T21植體廠牌尺寸', null=True, max_length=256, unique=False)
    T22_Implant_brand = models.TextField('T22植體廠牌', null=True, max_length=256, unique=False)
    T22_Implant_size = models.TextField('T22植體廠牌尺寸', null=True, max_length=256, unique=False)
    T23_Implant_brand = models.TextField('T23植體廠牌', null=True, max_length=256, unique=False)
    T23_Implant_size = models.TextField('T23植體廠牌尺寸', null=True, max_length=256, unique=False)
    T24_Implant_brand = models.TextField('T24植體廠牌', null=True, max_length=256, unique=False)
    T24_Implant_size = models.TextField('T24植體廠牌尺寸', null=True, max_length=256, unique=False)
    T25_Implant_brand = models.TextField('T25植體廠牌', null=True, max_length=256, unique=False)
    T25_Implant_size = models.TextField('T25植體廠牌尺寸', null=True, max_length=256, unique=False)
    T26_Implant_brand = models.TextField('T26植體廠牌', null=True, max_length=256, unique=False)
    T26_Implant_size = models.TextField('T26植體廠牌尺寸', null=True, max_length=256, unique=False)
    T27_Implant_brand = models.TextField('T27植體廠牌', null=True, max_length=256, unique=False)
    T27_Implant_size = models.TextField('T27植體廠牌尺寸', null=True, max_length=256, unique=False)
    T28_Implant_brand = models.TextField('T28植體廠牌', null=True, max_length=256, unique=False)
    T28_Implant_size = models.TextField('T28植體廠牌尺寸', null=True, max_length=256, unique=False)
    T31_Implant_brand = models.TextField('T31植體廠牌', null=True, max_length=256, unique=False)
    T31_Implant_size = models.TextField('T31植體廠牌尺寸', null=True, max_length=256, unique=False)
    T32_Implant_brand = models.TextField('T32植體廠牌', null=True, max_length=256, unique=False)
    T32_Implant_size = models.TextField('T32植體廠牌尺寸', null=True, max_length=256, unique=False)
    T33_Implant_brand = models.TextField('T33植體廠牌', null=True, max_length=256, unique=False)
    T33_Implant_size = models.TextField('T33植體廠牌尺寸', null=True, max_length=256, unique=False)
    T34_Implant_brand = models.TextField('T34植體廠牌', null=True, max_length=256, unique=False)
    T34_Implant_size = models.TextField('T34植體廠牌尺寸', null=True, max_length=256, unique=False)
    T35_Implant_brand = models.TextField('T35植體廠牌', null=True, max_length=256, unique=False)
    T35_Implant_size = models.TextField('T35植體廠牌尺寸', null=True, max_length=256, unique=False)
    T36_Implant_brand = models.TextField('T36植體廠牌', null=True, max_length=256, unique=False)
    T36_Implant_size = models.TextField('T36植體廠牌尺寸', null=True, max_length=256, unique=False)
    T37_Implant_brand = models.TextField('T37植體廠牌', null=True, max_length=256, unique=False)
    T37_Implant_size = models.TextField('T37植體廠牌尺寸', null=True, max_length=256, unique=False)
    T38_Implant_brand = models.TextField('T38植體廠牌', null=True, max_length=256, unique=False)
    T38_Implant_size = models.TextField('T38植體廠牌尺寸', null=True, max_length=256, unique=False)
    T41_Implant_brand = models.TextField('T41植體廠牌', null=True, max_length=256, unique=False)
    T41_Implant_size = models.TextField('T41植體廠牌尺寸', null=True, max_length=256, unique=False)
    T42_Implant_brand = models.TextField('T42植體廠牌', null=True, max_length=256, unique=False)
    T42_Implant_size = models.TextField('T42植體廠牌尺寸', null=True, max_length=256, unique=False)
    T43_Implant_brand = models.TextField('T43植體廠牌', null=True, max_length=256, unique=False)
    T43_Implant_size = models.TextField('T43植體廠牌尺寸', null=True, max_length=256, unique=False)
    T44_Implant_brand = models.TextField('T44植體廠牌', null=True, max_length=256, unique=False)
    T44_Implant_size = models.TextField('T44植體廠牌尺寸', null=True, max_length=256, unique=False)
    T45_Implant_brand = models.TextField('T45植體廠牌', null=True, max_length=256, unique=False)
    T45_Implant_size = models.TextField('T45植體廠牌尺寸', null=True, max_length=256, unique=False)
    T46_Implant_brand = models.TextField('T46植體廠牌', null=True, max_length=256, unique=False)
    T46_Implant_size = models.TextField('T46植體廠牌尺寸', null=True, max_length=256, unique=False)
    T47_Implant_brand = models.TextField('T47植體廠牌', null=True, max_length=256, unique=False)
    T47_Implant_size = models.TextField('T47植體廠牌尺寸', null=True, max_length=256, unique=False)
    T48_Implant_brand = models.TextField('T48植體廠牌', null=True, max_length=256, unique=False)
    T48_Implant_size = models.TextField('T48植體廠牌尺寸', null=True, max_length=256, unique=False)
    #第四介面存取
    Positioning_plate_STL_order_method = models.CharField('定位板STL入單方式', null=True, max_length=32, unique=False)
    Positioning_plate_Natural_teeth = models.CharField('定位板自然牙', null=True, max_length=32, unique=False)
    Positioning_plate_Metal_scattering = models.CharField('定位板金屬散射', null=True, max_length=32, unique=False)
    Positioning_plate_remark = models.CharField('定位板備註', null=True, max_length=512, unique=False, blank=True)
    #功能性欄位
    patients = models.ForeignKey(Patient,null=True, blank=True, on_delete=models.SET_NULL, verbose_name='病患連接')
    doctors = models.ForeignKey(User,null=True, blank=True,on_delete=models.SET_NULL, verbose_name='醫師連接')

    avatar_3d_palate = models.CharField('3D上顎模型', max_length=500, null=True, blank=True)
    avatar_3d_palate_Denture = models.CharField('3D上顎模型Denture', max_length=500, null=True, blank=True)
    avatar_3d_jaw = models.CharField('3D下顎模型', max_length=500, null=True, blank=True)
    avatar_3d_jaw_Denture = models.CharField('3D下顎模型Denture', max_length=500, null=True, blank=True)
    avatar_image1 = models.CharField('病患照片1', max_length=500, null=True, blank=True)
    avatar_image2 = models.CharField('病患照片2', max_length=500, null=True, blank=True)
    avatar_image3 = models.CharField('病患照片3', max_length=500, null=True, blank=True)
    avatar_image4 = models.CharField('病患照片4', max_length=500, null=True, blank=True)
    avatar_image5 = models.CharField('病患照片5', max_length=500, null=True, blank=True)
    avatar_image6 = models.CharField('病患照片6', max_length=500, null=True, blank=True)
    avatar_image7 = models.CharField('病患照片7', max_length=500, null=True, blank=True)
    avatar_image8 = models.CharField('病患照片8', max_length=500, null=True, blank=True)
    avatar_image9 = models.CharField('病患照片9', max_length=500, null=True, blank=True)
    avatar_project = models.CharField('專案', max_length=500, null=True, blank=True)
    avatar_CT = models.CharField('CT', max_length=500, null=True, blank=True)
    Order_Status = models.IntegerField('訂單進度',  null=True, blank=True)
    draft_status = models.CharField('草稿狀態', max_length=32, null=True, blank=True)
    design = models.CharField('設計師設計檔', max_length=500, null=True, blank=True)    
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='創建者', related_name='created_orders')
    clinc_created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='診所創建者', related_name='clinc_created_by')
    Top_created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='技工所創建者', related_name='Top_created_by')

    class Meta:
        verbose_name = '訂單資訊'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class File(CommonAModel):
    """
    文件存儲表,業務表根據具體情況選擇是否外鍵關聯
    """
    name = models.CharField('名稱', max_length=100, null=True, blank=True)
    size = models.IntegerField('文件大小', default=1, null=True, blank=True)
    file = models.FileField('文件', upload_to='%Y/%m/%d/')
    type_choices = (
        ('文檔', '文檔'),
        ('視頻', '視頻'),
        ('音頻', '音頻'),
        ('圖片', '圖片'),
        ('其它', '其它')
    )
    mime = models.CharField('文件格式', max_length=120, null=True, blank=True)
    type = models.CharField('文件類型', max_length=50, choices=type_choices, default='文檔')
    path = models.CharField('地址', max_length=200, null=True, blank=True)


    class Meta:
        verbose_name = '文件庫'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name