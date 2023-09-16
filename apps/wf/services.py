from apps.wf.serializers import CustomFieldSerializer
from apps.wf.serializers import TicketSerializer, TicketSimpleSerializer
from typing import Tuple
from apps.system.models import User
from apps.wf.models import CustomField, State, Ticket, TicketFlow, Transition, Workflow
from rest_framework.exceptions import APIException, PermissionDenied
from django.utils import timezone
from datetime import timedelta
import random
from .scripts import GetParticipants, HandleScripts
from utils.queryset import get_parent_queryset

class WfService(object):
    @staticmethod
    def get_worlflow_states(workflow:Workflow):
        """
        獲取工作流狀態列表
        """
        return State.objects.filter(workflow=workflow, is_deleted=False).order_by('sort')
    
    @staticmethod
    def get_workflow_transitions(workflow:Workflow):
        """
        獲取工作流流轉列表
        """
        return Transition.objects.filter(workflow=workflow, is_deleted=False)
    
    @staticmethod
    def get_workflow_start_state(workflow:Workflow):
        """
        獲取工作流初始狀態
        """
        try:
            wf_state_obj = State.objects.get(workflow=workflow, type=State.STATE_TYPE_START, is_deleted=False)
            return wf_state_obj
        except:
            raise Exception('工作流狀態配置錯誤')

    @staticmethod
    def get_workflow_end_state(workflow:Workflow):
        """
        獲取工作流結束狀態
        """
        try:
            wf_state_obj = State.objects.get(workflow=workflow, type=State.STATE_TYPE_END, is_deleted=False)
            return wf_state_obj
        except:
            raise Exception('工作流狀態配置錯誤')

    @staticmethod
    def get_workflow_custom_fields(workflow:Workflow):
        """
        獲取工單欄位
        """
        return CustomField.objects.filter(is_deleted=False, workflow=workflow).order_by('sort')

    @staticmethod
    def get_workflow_custom_fields_list(workflow:Workflow):
        """
        獲取工單欄位key List
        """
        return list(CustomField.objects.filter(is_deleted=False, workflow=workflow).order_by('sort').values_list('field_key', flat=True))

    @classmethod
    def get_ticket_transitions(cls, ticket:Ticket):
        """
        獲取工單當前狀態下可用的流轉條件
        """
        return cls.get_state_transitions(ticket.state)

    @classmethod    
    def get_state_transitions(cls, state:State):
        """
        獲取狀態可執行的操作
        """
        return Transition.objects.filter(is_deleted=False, source_state=state).all()

    @classmethod
    def get_ticket_steps(cls, ticket:Ticket):
        steps = cls.get_worlflow_states(ticket.workflow)
        nsteps_list = []
        for i in steps:
            if ticket.state == i or (not i.is_hidden):
                nsteps_list.append(i)
        return nsteps_list

    @classmethod
    def get_ticket_transitions(cls, ticket:Ticket):
        """
        獲取工單可執行的操作
        """
        return cls.get_state_transitions(ticket.state)

    @classmethod
    def get_transition_by_args(cls, kwargs:dict):
        """
        查詢並獲取流轉
        """
        kwargs['is_deleted'] = False
        return Transition.objects.filter(**kwargs).all()

    @classmethod
    def get_ticket_sn(cls, workflow:Workflow):
        """
        生成工單流水號
        """
        now = timezone.now()
        today = str(now)[:10]+' 00:00:00'
        next_day = str(now+timedelta(days=1))[:10]+' 00:00:00'
        ticket_day_count_new = Ticket.objects.filter(create_time__gte=today, create_time__lte=next_day, workflow=workflow).count()+1
        return '%s_%04d%02d%02d%04d' % (workflow.sn_prefix, now.year, now.month, now.day, ticket_day_count_new)


        
    @classmethod
    def get_next_state_by_transition_and_ticket_info(cls, ticket:Ticket, transition: Transition, new_ticket_data:dict={})->object:
        """
        獲取下個節點狀態
        """
        source_state = ticket.state
        destination_state = transition.destination_state
        ticket_all_value = cls.get_ticket_all_field_value(ticket)
        ticket_all_value.update(**new_ticket_data)
        for key, value in ticket_all_value.items():
                if isinstance(ticket_all_value[key], str):
                    ticket_all_value[key] = "'" + ticket_all_value[key] + "'"
        if transition.condition_expression:
            for i in transition.condition_expression:
                expression = i['expression'].format(**ticket_all_value)
                import datetime, time  # 用於支持條件表達式中對時間的操作
                if eval(expression, {'__builtins__':None}, {'datetime':datetime, 'time':time}):
                    destination_state = State.objects.get(pk=i['target_state'])
                    return destination_state
        return destination_state
    
    @classmethod
    def get_ticket_state_participant_info(cls, state:State, ticket:Ticket, new_ticket_data:dict={}, handler:User=None):
        """
        獲取工單目標狀態實際的處理人, 處理人類型
        """
        if state.type == State.STATE_TYPE_START:
            """
            回到初始狀態
            """
            return dict(destination_participant_type=State.PARTICIPANT_TYPE_PERSONAL,
                                destination_participant=ticket.create_by.id,
                                multi_all_person={})
        elif state.type == State.STATE_TYPE_END:
            """
            到達結束狀態
            """
            return dict(destination_participant_type=0,
                                destination_participant=0,
                                multi_all_person={})
        multi_all_person_dict = {}
        destination_participant_type, destination_participant = state.participant_type, state.participant
        if destination_participant_type == State.PARTICIPANT_TYPE_FIELD:
            destination_participant = new_ticket_data.get(destination_participant, 0) if destination_participant in new_ticket_data \
                else Ticket.ticket_data.get(destination_participant, 0)

        elif destination_participant_type == State.PARTICIPANT_TYPE_FORMCODE:#代碼獲取
            destination_participant = getattr(GetParticipants, destination_participant)(
                state=state, ticket=ticket, new_ticket_data=new_ticket_data, hander=handler)

        elif destination_participant_type == State.PARTICIPANT_TYPE_DEPT:#部門
            destination_participant = list(User.objects.filter(dept__in=destination_participant).values_list('id', flat=True))

        elif destination_participant_type == State.PARTICIPANT_TYPE_ROLE:#角色
            user_queryset = User.objects.filter(roles__in=destination_participant)
            # 如果選擇了角色, 需要走過濾策略
            if state.filter_policy == 1:
                depts = get_parent_queryset(ticket.belong_dept)
                user_queryset = user_queryset.filter(dept__in=depts)
            elif state.filter_policy == 2:
                depts = get_parent_queryset(ticket.create_by.dept)
                user_queryset = user_queryset.filter(dept__in=depts)
            elif state.filter_policy == 3:
                depts = get_parent_queryset(handler.dept)
                user_queryset = user_queryset.filter(dept__in=depts)
            destination_participant = list(user_queryset.values_list('id', flat=True))
        if type(destination_participant) == list:
            destination_participant_type = State.PARTICIPANT_TYPE_MULTI
            destination_participant = list(set(destination_participant))
            if len(destination_participant) == 1: # 如果只有一個人
                destination_participant_type = State.PARTICIPANT_TYPE_PERSONAL
                destination_participant = destination_participant[0]
        else:
            destination_participant_type = State.PARTICIPANT_TYPE_PERSONAL
        if destination_participant_type == State.PARTICIPANT_TYPE_MULTI:
            if state.distribute_type == State.STATE_DISTRIBUTE_TYPE_RANDOM:
                destination_participant = random.choice(destination_participant)
            elif state.distribute_type == State.STATE_DISTRIBUTE_TYPE_ALL:
                for i in destination_participant:
                    multi_all_person_dict[i]={}

        return dict(destination_participant_type=destination_participant_type,
                          destination_participant=destination_participant,
                          multi_all_person=multi_all_person_dict)
    
    @classmethod
    def ticket_handle_permission_check(cls, ticket:Ticket, user:User)-> dict:
        transitions = cls.get_state_transitions(ticket.state)
        if not transitions:
            return dict(permission=True, msg="工單當前狀態無需操作")
        current_participant_count = 0
        participant_type = ticket.participant_type
        participant = ticket.participant
        state = ticket.state
        if participant_type == State.PARTICIPANT_TYPE_PERSONAL:
            if user.id != participant:
                return dict(permission=False, msg="非當前處理人", need_accept=False)
        elif participant_type in [State.PARTICIPANT_TYPE_MULTI, State.PARTICIPANT_TYPE_DEPT, State.PARTICIPANT_TYPE_ROLE]:
            if user.id not in participant:
                return dict(permission=False, msg="非當前處理人", need_accept=False)
            current_participant_count = len(participant)
        if current_participant_count == 1:
            if [user.id] == participant or user.id == participant:
                pass
            else:
                return dict(permission=False, msg="非當前處理人", need_accept=False)
        elif current_participant_count >1 and state.distribute_type == State.STATE_DISTRIBUTE_TYPE_ACTIVE:
            if user.id not in participant:
                return dict(permission=False, msg="非當前處理人", need_accept=False)
            return dict(permission=False, msg="需要先接單再處理", need_accept=True)
        if ticket.in_add_node:
            return dict(permission=False, msg="工單當前處於加簽中,請加簽完成後操作", need_accept=False)
        return dict(permission=True, msg="", need_accept=False)

    @classmethod
    def check_dict_has_all_same_value(cls, dict_obj: object)->tuple:
        """
        check whether all key are equal in a dict
        :param dict_obj:
        :return:
        """
        value_list = []
        for key, value in dict_obj.items():
            value_list.append(value)
        value_0 = value_list[0]
        for value in value_list:
            if value_0 != value:
                return False
        return True
           
    @classmethod
    def get_ticket_all_field_value(cls, ticket: Ticket)->dict:
        """
        工單所有欄位的值
        get ticket's all field value
        :param ticket:
        :return:
        """
        # 獲取工單基礎表中的欄位中的欄位信息
        field_info_dict = TicketSimpleSerializer(instance=ticket).data
        # 獲取自定義欄位的值
        custom_fields_queryset = cls.get_workflow_custom_fields(ticket.workflow)
        for i in custom_fields_queryset:
            field_info_dict[i.field_key] = ticket.ticket_data.get(i.field_key, None)
        return field_info_dict

    @classmethod
    def handle_ticket(cls, ticket:Ticket, transition: Transition, new_ticket_data:dict={}, handler:User=None, 
        suggestion:str='', created:bool=False, by_timer:bool=False, by_task:bool=False, by_hook:bool=False):

        source_state = ticket.state
        source_ticket_data = ticket.ticket_data

        # 校驗處理權限
        if not handler or not created: # 沒有處理人意味著系統觸發不校驗處理權限
            result = WfService.ticket_handle_permission_check(ticket, handler)
            if result.get('permission') is False:
                raise PermissionDenied(result.get('msg'))

        # 校驗表單必填項目
        if transition.field_require_check or not created:
            for key, value in ticket.state.state_fields.items(): 
                if int(value) == State.STATE_FIELD_REQUIRED:
                    if key not in new_ticket_data or not new_ticket_data[key]:
                        raise APIException('欄位{}必填'.format(key))

        destination_state = cls.get_next_state_by_transition_and_ticket_info(ticket, transition, new_ticket_data)
        multi_all_person = ticket.multi_all_person
        if multi_all_person:
            multi_all_person[handler.id] =dict(transition=transition.id)
            # 判斷所有人處理結果是否一致
            if WfService.check_dict_has_all_same_value(multi_all_person):
                participant_info = WfService.get_ticket_state_participant_info(destination_state, ticket, new_ticket_data)
                destination_participant_type = participant_info.get('destination_participant_type', 0)
                destination_participant = participant_info.get('destination_participant', 0)
                multi_all_person = {}
            else:
                # 處理人沒有沒有全部處理完成或者處理動作不一致
                destination_participant_type = ticket.participant_type
                destination_state = ticket.state  # 保持原狀態
                destination_participant = []
                for key, value in multi_all_person.items():
                    if not value:
                        destination_participant.append(key)
        else:
            # 當前處理人類型非全部處理
            participant_info = WfService.get_ticket_state_participant_info(destination_state, ticket, new_ticket_data)
            destination_participant_type = participant_info.get('destination_participant_type', 0)
            destination_participant = participant_info.get('destination_participant', 0)
            multi_all_person = participant_info.get('multi_all_person', {})

        # 更新工單信息：基礎欄位及自定義欄位， add_relation欄位 需要下個處理人是部門、角色等的情況
        ticket.state = destination_state
        ticket.participant_type = destination_participant_type
        ticket.participant = destination_participant
        ticket.multi_all_person = multi_all_person
        if destination_state.type == State.STATE_TYPE_END:
            ticket.act_state = Ticket.TICKET_ACT_STATE_FINISH
        elif destination_state.type == State.STATE_TYPE_START:
            ticket.act_state = Ticket.TICKET_ACT_STATE_DRAFT
        else:
            ticket.act_state = Ticket.TICKET_ACT_STATE_ONGOING

        if transition.attribute_type == Transition.TRANSITION_ATTRIBUTE_TYPE_REFUSE:
            ticket.act_state = Ticket.TICKET_ACT_STATE_BACK

        # 只更新必填和可選的欄位
        if not created:
            for key, value in source_state.state_fields.items(): 
                    if value in (State.STATE_FIELD_REQUIRED, State.STATE_FIELD_OPTIONAL):
                        if key in new_ticket_data:
                            source_ticket_data[key] = new_ticket_data[key]
            ticket.ticket_data = source_ticket_data
        ticket.save()

        # 更新工單流轉記錄
        if not by_task:
            TicketFlow.objects.create(ticket=ticket, state=source_state, ticket_data=WfService.get_ticket_all_field_value(ticket),
                            suggestion=suggestion, participant_type=State.PARTICIPANT_TYPE_PERSONAL,
                            participant=handler, transition=transition)

        if created:
            if source_state.participant_cc:
                TicketFlow.objects.create(ticket=ticket, state=source_state, 
                            participant_type=0, intervene_type=Transition.TRANSITION_INTERVENE_TYPE_CC,
                            participant=None, participant_cc=source_state.participant_cc)

        # 目標狀態需要抄送
        if destination_state.participant_cc:
            TicketFlow.objects.create(ticket=ticket, state=destination_state, 
                        participant_type=0, intervene_type=Transition.TRANSITION_INTERVENE_TYPE_CC,
                        participant=None, participant_cc=destination_state.participant_cc)
        
        # 如果目標狀態是腳本則執行
        if destination_state.participant_type == State.PARTICIPANT_TYPE_ROBOT:
            getattr(HandleScripts, destination_state.participant)(ticket)
        
        return ticket

