from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.response import Response
import rest_framework.status as status
import logging
logger = logging.getLogger('log')

class BaseResponse(object):
    """
    封裝的返回信息類
    """

    def __init__(self):
        self.code = 200
        self.data = None
        self.msg = None

    @property
    def dict(self):
        return self.__dict__


class FitJSONRenderer(JSONRenderer):
    """
    自行封裝的渲染器
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        如果使用這個render，
        普通的response將會被包裝成：
            {"code":200,"data":"X","msg":"X"}
        這樣的結果
        使用方法：
            - 全局
                REST_FRAMEWORK = {
                'DEFAULT_RENDERER_CLASSES': ('utils.response.FitJSONRenderer', ),
                }
            - 局部
                class UserCountView(APIView):
                    renderer_classes = [FitJSONRenderer]

        :param data:
        :param accepted_media_type:
        :param renderer_context:
        :return: {"code":200,"data":"X","msg":"X"}
        """
        response_body = BaseResponse()
        response = renderer_context.get("response")
        response_body.code = response.status_code
        if response_body.code >= 400:  # 響應異常
            response_body.data = data  # data里是詳細異常信息
            prefix = ""
            if isinstance(data, dict):
                prefix = list(data.keys())[0]
                data = data[prefix]
            if isinstance(data, list):
                data = data[0]
            response_body.msg = prefix + ":" + str(data) # 取一部分放入msg,方便前端alert
        else:
            response_body.data = data
        renderer_context.get("response").status_code = 200  # 統一成200響應,用code區分
        return super(FitJSONRenderer, self).render(response_body.dict, accepted_media_type, renderer_context)
