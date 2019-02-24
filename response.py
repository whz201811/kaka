# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 'author':'zouliwei'


"""响应模块"""


import json
from werkzeug.wrappers import Response
from .errors import HTMLRenderError, RestResponserHandlerError


class BaseResponse(Response):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = dict()  # 为请求对象增加一个字典以供在多次处理同一请求对象时共享数据


class TextResponse(BaseResponse):
    _mimetype = 'text/plain'

    def __init__(self, text):
        super().__init__(text, mimetype=self._mimetype)


class RenderResponse(BaseResponse):
    _mimetype = 'text/html'
    _render = None
    _has_render = False

    def __init__(self, template_name, **context):
        self._check_set()
        text = self._render_text(template_name, **context)
        super().__init__(text, mimetype=self._mimetype)

    def _check_set(self):
        if not self._has_render:
            raise HTMLRenderError("you have not set a render yet.")

    def _render_text(self, template_name, **context):
        return self._render.render(template_name, **context)

    @classmethod
    def set_render(cls, render):
        if render is None:
            raise ValueError('the render to be set is None.')
        else:
            cls._render = render
            cls._has_render = True


class RestResponse(BaseResponse):
    """
    此类实例化的时候会将code和status作为响应字典的键名，
    若这两个键名也存在于extra_dict中，则会被弹出。
    """
    _mimetype = 'application/json'
    _cannot_override = ('code', 'status')

    def __init__(self, code, status, extra_dict=None):
        json_string = self._build(code, status, extra_dict)
        super().__init__(json_string, mimetype=self._mimetype)

    def _build(self, code, status, extra_dict):
        """
        extra_dict 表示额外的属性信息，合并入响应的字典中，位于一级目录
        """

        field_list = ('code', 'status')
        valud_list = (code, status)
        restful_dict = dict(zip(field_list, valud_list))

        if extra_dict is not None:
            self._check_override(extra_dict)
            restful_dict.update(extra_dict)

        return json.dumps(restful_dict)

    def _check_override(self, extra_dict):
        # 额外信息字典中不允许有code/status属性
        for key in self._cannot_override:
            try:
                extra_dict.pop(key)
            except KeyError:
                pass


class SUCCESS(RestResponse):
    """
    此类实例化过程必须提供一个data属性作为成功的数据字典，若extra_dict中也有重名的data键值对，将会被前者覆盖。
    此类实例化主要是增加data属性值，接着交由父类RestResponse实例化。
    """
    _status = 'SUCCESS!'
    _code = None
    _has_code = False

    def __init__(self, data, extra_dict=None):
        self._check_set()
        if extra_dict is None:
            extra_dict = dict()
        self._add_data(data, extra_dict)
        super().__init__(self._code, self._status, extra_dict=extra_dict)

    def _check_set(self):
        if not self._has_code:
            raise RestResponserHandlerError("you have not set a SUCCESS code yet.")

    def _add_data(self, data, extra_dict):
        extra_dict['data'] = data

    @classmethod
    def set_status(cls, status):
        if not isinstance(status, str):
            raise TypeError(f"the type of status must be str, current is: '{type(status)}'.")
        cls._status = status

    @classmethod
    def set_code(cls, code):
        if not isinstance(code, int):
            raise TypeError(f"the type of code must be int, current is: '{type(code)}'.")
        cls._code = code
        cls._has_code = True


class FAIL(RestResponse):
    """
    此类实例化过程必须提供一个code属性作为操作失败响应码，
    此响应码将会在搜索code_map时使用，得到操作失败的原因why后将会加入到响应字典中。
    若extra_dict中也有重名的why键值对，将会被前者覆盖。
    此类实例化主要是增加why属性值，接着交由父类RestResponse实例化。
    """
    _status = 'FAIL!'
    _code_map = None
    _has_code_map = False

    def __init__(self, code, extra_dict=None):
        """
        extra_dict 是额外的响应信息字典，位于一级目录，不能包含why属性
        """
        self._check_set()
        if extra_dict is None:
            extra_dict = dict()
        self._add_why(code, extra_dict)
        super().__init__(code, self._status, extra_dict=extra_dict)

    def _check_set(self):
        if not self._has_code_map:
            raise RestResponserHandlerError("you have not set a FAIL code_map yet.")

    def _add_why(self, code, extra_dict):
        """
        根据给定的错误码更新额外信息字典，增加why属性
        """

        why = self._code_map.get(code, None)
        if why is None:
            raise RestResponserHandlerError(f"the error code '{code}' is not found in code_map.")
        extra_dict['why'] = why

    @classmethod
    def set_status(cls, status):
        if not isinstance(status, str):
            raise TypeError(f"the type of status must be str, current is: '{type(status)}'.")
        cls._status = status

    @classmethod
    def set_code_map(cls, code_map):
        def check():
            if not isinstance(code_map, dict):
                raise TypeError(f"the type of code_map must be dict, current is: '{type(code_map)}'.")

            # 检查code_map中的值
            for code, why in code_map.items():
                if not isinstance(code, int):
                    raise TypeError(f"the type of code must be int, current is: '{type(code)}'.")

                if not isinstance(why, str):
                    raise TypeError(f"the type of why must be int, current is: '{type(why)}'.")

        check()
        cls._code_map = code_map
        cls._has_code_map = True
