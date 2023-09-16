from random import choice
from django.db import models
from django.db.models.base import Model
import django.utils.timezone as timezone
from django.db.models.query import QuerySet
from apps.system.models import CommonAModel, CommonBModel, Organization, User, Dict, File
from utils.model import SoftModel, BaseModel
from simple_history.models import HistoricalRecords


class Workflow(CommonAModel):
    """
    工作流
    """
    name = models.CharField('名稱', max_length=50)
    key = models.CharField('工作流標識', unique=True, max_length=20, null=True, blank=True)
    sn_prefix = models.CharField('流水號前綴', max_length=50, default='hb')
    description = models.CharField('描述', max_length=200, null=True, blank=True)
    view_permission_check = models.BooleanField('查看權限校驗', default=True, help_text='開啟後，只允許工單的關聯人(創建人、曾經的處理人)有權限查看工單')
    limit_expression = models.JSONField('限製表達式', default=dict, blank=True, help_text='限制周期({"period":24} 24小時), 限制次數({"count":1}在限制周期內只允許提交1次), 限制級別({"level":1} 針對(1單個用戶 2全局)限制周期限制次數,默認特定用戶);允許特定人員提交({"allow_persons":"zhangsan,lisi"}只允許張三提交工單,{"allow_depts":"1,2"}只允許部門id為1和2的用戶提交工單，{"allow_roles":"1,2"}只允許角色id為1和2的用戶提交工單)')
    display_form_str = models.JSONField('展現表單欄位', default=list, blank=True, help_text='默認"[]"，用於用戶只有對應工單查看權限時顯示哪些欄位,field_key的list的json,如["days","sn"],內置特殊欄位participant_info.participant_name:當前處理人信息(部門名稱、角色名稱)，state.state_name:當前狀態的狀態名,workflow.workflow_name:工作流名稱')
    title_template = models.CharField('標題模板', max_length=50, default='{title}', null=True, blank=True, help_text='工單欄位的值可以作為參數寫到模板中，格式如：你有一個待辦工單:{title}')
    content_template = models.CharField('內容模板', max_length=1000, default='標題:{title}, 創建時間:{create_time}', null=True, blank=True, help_text='工單欄位的值可以作為參數寫到模板中，格式如：標題:{title}, 創建時間:{create_time}')

class State(CommonAModel):
    """
    狀態記錄
    """
    STATE_TYPE_START = 1
    STATE_TYPE_END = 2
    type_choices = (
        (0, '普通'),
        (STATE_TYPE_START, '開始'),
        (STATE_TYPE_END, '結束')
    )
    PARTICIPANT_TYPE_PERSONAL = 1
    PARTICIPANT_TYPE_MULTI = 2
    PARTICIPANT_TYPE_DEPT = 3
    PARTICIPANT_TYPE_ROLE = 4
    PARTICIPANT_TYPE_VARIABLE = 5
    PARTICIPANT_TYPE_ROBOT = 6
    PARTICIPANT_TYPE_FIELD = 7
    PARTICIPANT_TYPE_PARENT_FIELD = 8
    PARTICIPANT_TYPE_FORMCODE = 9
    state_participanttype_choices = (
        (0, '無處理人'),
        (PARTICIPANT_TYPE_PERSONAL, '個人'),
        (PARTICIPANT_TYPE_MULTI, '多人'),
        # (PARTICIPANT_TYPE_DEPT, '部門'),
        (PARTICIPANT_TYPE_ROLE, '角色'),
        # (PARTICIPANT_TYPE_VARIABLE, '變量'),
        (PARTICIPANT_TYPE_ROBOT, '腳本'),
        (PARTICIPANT_TYPE_FIELD, '工單的欄位'),
        # (PARTICIPANT_TYPE_PARENT_FIELD, '父工單的欄位'),
        (PARTICIPANT_TYPE_FORMCODE, '代碼獲取')
    )
    STATE_DISTRIBUTE_TYPE_ACTIVE = 1 # 主動接單
    STATE_DISTRIBUTE_TYPE_DIRECT = 2 # 直接處理(當前為多人的情況，都可以處理，而不需要先接單)
    STATE_DISTRIBUTE_TYPE_RANDOM = 3 # 隨機分配
    STATE_DISTRIBUTE_TYPE_ALL = 4 # 全部處理
    state_distribute_choices=(
        (STATE_DISTRIBUTE_TYPE_ACTIVE, '主動接單'),
        (STATE_DISTRIBUTE_TYPE_DIRECT, '直接處理'),
        (STATE_DISTRIBUTE_TYPE_RANDOM, '隨機分配'),
        (STATE_DISTRIBUTE_TYPE_ALL, '全部處理'),
    )

    STATE_FIELD_READONLY= 1 # 欄位只讀
    STATE_FIELD_REQUIRED = 2 # 欄位必填
    STATE_FIELD_OPTIONAL = 3 # 欄位可選
    STATE_FIELD_HIDDEN = 4 # 欄位隱藏
    state_filter_choices=(
        (0, '無'),
        (1, '和工單同屬一及上級部門'),
        (2, '和創建人同屬一及上級部門'),
        (3, '和上步處理人同屬一及上級部門'),
    )
    name = models.CharField('名稱', max_length=50)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, verbose_name='所屬工作流')
    is_hidden = models.BooleanField('是否隱藏', default=False, help_text='設置為True時,獲取工單步驟api中不顯示此狀態(當前處於此狀態時除外)')
    sort = models.IntegerField('狀態順序', default=0, help_text='用於工單步驟介面時，step上狀態的順序(因為存在網狀情況，所以需要人為設定順序),值越小越靠前')
    type = models.IntegerField('狀態類型', default=0, choices=type_choices, help_text='0.普通類型 1.初始狀態(用於新建工單時,獲取對應的欄位必填及transition信息) 2.結束狀態(此狀態下的工單不得再處理，即沒有對應的transition)')
    enable_retreat = models.BooleanField('允許撤回', default=False, help_text='開啟後允許工單創建人在此狀態直接撤回工單到初始狀態')
    participant_type = models.IntegerField('參與者類型', choices=state_participanttype_choices, default=1, blank=True, help_text='0.無處理人,1.個人,2.多人,3.部門,4.角色,5.變量(支持工單創建人,創建人的leader),6.腳本,7.工單的欄位內容(如表單中的"測試負責人"，需要為用戶名或者逗號隔開的多個用戶名),8.父工單的欄位內容。 初始狀態請選擇類型5，參與人填create_by')
    participant = models.JSONField('參與者', default=list, blank=True, help_text='可以為空(無處理人的情況，如結束狀態)、userid、userid列表\部門id\角色id\變量(create_by,create_by_tl)\腳本記錄的id等，包含子工作流的需要設置處理人為loonrobot')
    state_fields = models.JSONField('表單欄位', default=dict, help_text='json格式字典存儲,包括讀寫屬性1：只讀，2：必填，3：可選, 4:隱藏 示例：{"create_time":1,"title":2, "sn":1}, 內置特殊欄位participant_info.participant_name:當前處理人信息(部門名稱、角色名稱)，state.state_name:當前狀態的狀態名,workflow.workflow_name:工作流名稱')  # json格式存儲,包括讀寫屬性1：只讀，2：必填，3：可選，4：不顯示, 字典的字典
    distribute_type = models.IntegerField('分配方式', default=1, choices=state_distribute_choices, help_text='1.主動接單(如果當前處理人實際為多人的時候，需要先接單才能處理) 2.直接處理(即使當前處理人實際為多人，也可以直接處理) 3.隨機分配(如果實際為多人，則系統會隨機分配給其中一個人) 4.全部處理(要求所有參與人都要處理一遍,才能進入下一步)')
    filter_policy = models.IntegerField('參與人過濾策略', default=0, choices=state_filter_choices)
    participant_cc = models.JSONField('抄送給', default=list, blank=True, help_text='抄送給(userid列表)')

class Transition(CommonAModel):
    """
    工作流流轉，定時器，條件(允許跳過)， 條件流轉與定時器不可同時存在
    """
    TRANSITION_ATTRIBUTE_TYPE_ACCEPT = 1  # 同意
    TRANSITION_ATTRIBUTE_TYPE_REFUSE = 2  # 拒絕
    TRANSITION_ATTRIBUTE_TYPE_OTHER = 3  # 其他
    attribute_type_choices = (
        (1, '同意'),
        (2, '拒絕'),
        (3, '其他')
    )
    TRANSITION_INTERVENE_TYPE_DELIVER = 1  # 轉交操作
    TRANSITION_INTERVENE_TYPE_ADD_NODE = 2  # 加簽操作
    TRANSITION_INTERVENE_TYPE_ADD_NODE_END = 3  # 加簽處理完成
    TRANSITION_INTERVENE_TYPE_ACCEPT = 4  # 接單操作
    TRANSITION_INTERVENE_TYPE_COMMENT = 5  # 評論操作
    TRANSITION_INTERVENE_TYPE_DELETE = 6  # 刪除操作
    TRANSITION_INTERVENE_TYPE_CLOSE = 7  # 強制關閉操作
    TRANSITION_INTERVENE_TYPE_ALTER_STATE = 8  # 強制修改狀態操作
    TRANSITION_INTERVENE_TYPE_HOOK = 9  # hook操作
    TRANSITION_INTERVENE_TYPE_RETREAT = 10  # 撤回
    TRANSITION_INTERVENE_TYPE_CC = 11 # 抄送

    intervene_type_choices = (
        (0, '正常處理'),
        (TRANSITION_INTERVENE_TYPE_DELIVER, '轉交'),
        (TRANSITION_INTERVENE_TYPE_ADD_NODE, '加簽'),
        (TRANSITION_INTERVENE_TYPE_ADD_NODE_END, '加簽處理完成'),
        (TRANSITION_INTERVENE_TYPE_ACCEPT, '接單'),
        (TRANSITION_INTERVENE_TYPE_COMMENT, '評論'),
        (TRANSITION_INTERVENE_TYPE_DELETE, '刪除'),
        (TRANSITION_INTERVENE_TYPE_CLOSE, '強制關閉'),
        (TRANSITION_INTERVENE_TYPE_ALTER_STATE, '強制修改狀態'),
        (TRANSITION_INTERVENE_TYPE_HOOK, 'hook操作'),
        (TRANSITION_INTERVENE_TYPE_RETREAT, '撤回'),
        (TRANSITION_INTERVENE_TYPE_CC, '抄送')
    )

    name = models.CharField('操作', max_length=50)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, verbose_name='所屬工作流')
    timer = models.IntegerField('定時器(單位秒)', default=0, help_text='單位秒。處於源狀態X秒後如果狀態都沒有過變化則自動流轉到目標狀態。設置時間有效')
    source_state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='源狀態', related_name='sstate_transition')
    destination_state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='目的狀態', related_name='dstate_transition')
    condition_expression = models.JSONField('條件表達式', max_length=1000, default=list, help_text='流轉條件表達式，根據表達式中的條件來確定流轉的下個狀態，格式為[{"expression":"{days} > 3 and {days}<10", "target_state":11}] 其中{}用於填充工單的欄位key,運算時會換算成實際的值，當符合條件下個狀態將變為target_state_id中的值,表達式只支持簡單的運算或datetime/time運算.loonflow會以首次匹配成功的條件為準，所以多個條件不要有沖突' )
    attribute_type = models.IntegerField('屬性類型', default=1, choices=attribute_type_choices, help_text='屬性類型，1.同意，2.拒絕，3.其他')
    field_require_check = models.BooleanField('是否校驗必填項', default=True, help_text='默認在用戶點擊操作的時候需要校驗工單表單的必填項,如果設置為否則不檢查。用於如"退回"屬性的操作，不需要填寫表單內容')


class CustomField(CommonAModel):
    """自定義欄位, 設定某個工作流有哪些自定義欄位"""
    field_type_choices = (
        ('string', '字元串'),
        ('int', '整型'),
        ('float', '浮點'),
        ('boolean', '布爾'),
        ('date', '日期'),
        ('datetime', '日期時間'),
        ('radio', '單選'),
        ('checkbox', '多選'),
        ('select', '單選下拉'),
        ('selects', '多選下拉'),
        ('cascader', '單選級聯'),
        ('cascaders', '多選級聯'),
        ('select_dg', '彈框單選'),
        ('select_dgs', '彈框多選'),
        ('textarea', '文本域'),
        ('file', '附件')
    )
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, verbose_name='所屬工作流')
    field_type = models.CharField('類型', max_length=50, choices=field_type_choices, 
    help_text='string, int, float, date, datetime, radio, checkbox, select, selects, cascader, cascaders, select_dg, select_dgs,textarea, file')
    field_key = models.CharField('欄位標識', max_length=50, help_text='欄位類型請盡量特殊，避免與系統中關鍵字沖突')
    field_name = models.CharField('欄位名稱', max_length=50)
    sort = models.IntegerField('排序', default=0, help_text='工單基礎欄位在表單中排序為:流水號0,標題20,狀態id40,狀態名41,創建人80,創建時間100,更新時間120.前端展示工單信息的表單可以根據這個id順序排列')
    default_value = models.CharField('默認值', null=True, blank=True, max_length=100, help_text='前端展示時，可以將此內容作為表單中的該欄位的默認值')
    description = models.CharField('描述', max_length=100, blank=True, null=True, help_text='欄位的描述信息，可用於顯示在欄位的下方對該欄位的詳細描述')
    placeholder = models.CharField('占位符', max_length=100, blank=True, null=True, help_text='用戶工單詳情表單中作為欄位的占位符顯示')
    field_template = models.TextField('文本域模板', null=True, blank=True, help_text='文本域類型欄位前端顯示時可以將此內容作為欄位的placeholder')
    boolean_field_display = models.JSONField('布爾類型顯示名', default=dict, blank=True,
                                             help_text='當為布爾類型時候，可以支持自定義顯示形式。{"1":"是","0":"否"}或{"1":"需要","0":"不需要"}，注意數字也需要引號')
    
    field_choice = models.JSONField('選項值', default=list, blank=True,
                                    help_text='選項值，格式為list, 例["id":1, "name":"張三"]')
    
    label = models.CharField('標簽', max_length=1000, default='', help_text='處理特殊邏輯使用,比如sys_user用於獲取用戶作為選項')
    # hook = models.CharField('hook', max_length=1000, default='', help_text='獲取下拉選項用於動態選項值')
    is_hidden = models.BooleanField('是否隱藏', default=False, help_text='可用於攜帶不需要用戶查看的欄位信息')

class Ticket(CommonBModel):
    """
    工單
    """
    TICKET_ACT_STATE_DRAFT = 0  # 草稿中
    TICKET_ACT_STATE_ONGOING = 1  # 進行中
    TICKET_ACT_STATE_BACK = 2  # 被退回
    TICKET_ACT_STATE_RETREAT = 3  # 被撤回
    TICKET_ACT_STATE_FINISH = 4  # 已完成
    TICKET_ACT_STATE_CLOSED = 5  # 已關閉

    act_state_choices =(
        (TICKET_ACT_STATE_DRAFT, '草稿中'),
        (TICKET_ACT_STATE_ONGOING, '進行中'),
        (TICKET_ACT_STATE_BACK, '被退回'),
        (TICKET_ACT_STATE_RETREAT, '被撤回'),
        (TICKET_ACT_STATE_FINISH, '已完成'),
        (TICKET_ACT_STATE_CLOSED, '已關閉')
    )
    category_choices =(
        ('all', '全部'),
        ('owner', '我創建的'),
        ('duty', '待辦'),
        ('worked', '我處理的'),
        ('cc', '抄送我的')
    )
    title = models.CharField('標題', max_length=500, null=True, blank=True, help_text="工單標題")
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, verbose_name='關聯工作流')
    sn = models.CharField('流水號', max_length=25, help_text="工單的流水號")
    state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='當前狀態', related_name='ticket_state')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name='父工單')
    parent_state = models.ForeignKey(State, null=True, blank=True, on_delete=models.CASCADE, verbose_name='父工單狀態', related_name='ticket_parent_state')
    ticket_data = models.JSONField('工單數據', default=dict, help_text='工單自定義欄位內容')
    in_add_node = models.BooleanField('加簽狀態中', default=False, help_text='是否處於加簽狀態下')
    add_node_man = models.ForeignKey(User, verbose_name='加簽人', on_delete=models.SET_NULL, null=True, blank=True, help_text='加簽操作的人，工單當前處理人處理完成後會回到該處理人，當處於加簽狀態下才有效')
    script_run_last_result = models.BooleanField('腳本最後一次執行結果', default=True)
    participant_type = models.IntegerField('當前處理人類型', default=0, help_text='0.無處理人,1.個人,2.多人', choices=State.state_participanttype_choices)
    participant = models.JSONField('當前處理人', default=list, blank=True, help_text='可以為空(無處理人的情況，如結束狀態)、userid、userid列表')
    act_state = models.IntegerField('進行狀態', default=1, help_text='當前工單的進行狀態', choices=act_state_choices)
    multi_all_person = models.JSONField('全部處理的結果', default=dict, blank=True, help_text='需要當前狀態處理人全部處理時實際的處理結果，json格式')


class TicketFlow(BaseModel):
    """
    工單流轉日誌
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, verbose_name='關聯工單', related_name='ticketflow_ticket')
    transition = models.ForeignKey(Transition, verbose_name='流轉id', help_text='與worklow.Transition關聯， 為空時表示認為乾預的操作', on_delete=models.CASCADE, null=True, blank=True)
    suggestion = models.CharField('處理意見', max_length=10000, default='', blank=True)
    participant_type = models.IntegerField('處理人類型', default=0, help_text='0.無處理人,1.個人,2.多人等', choices=State.state_participanttype_choices)
    participant = models.ForeignKey(User, verbose_name='處理人', on_delete=models.SET_NULL, null=True, blank=True, related_name='ticketflow_participant')
    participant_str = models.CharField('處理人', max_length=200, null=True, blank=True, help_text='非人工處理的處理人相關信息')
    state = models.ForeignKey(State, verbose_name='當前狀態', default=0, blank=True, on_delete=models.CASCADE)
    ticket_data = models.JSONField('工單數據', default=dict, blank=True, help_text='可以用於記錄當前表單數據，json格式')
    intervene_type = models.IntegerField('乾預類型', default=0, help_text='流轉類型', choices=Transition.intervene_type_choices)
    participant_cc = models.JSONField('抄送給', default=list, blank=True, help_text='抄送給(userid列表)')

