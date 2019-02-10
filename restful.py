# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 'author':'zouliwei'


"""restful模块"""


from werkzeug.exceptions import MethodNotAllowed

from .response import SUCCESS, FAIL


class RestfulDescriptor():
    def __get__(self, instance, owner):
        return owner()


class RestView(object):
    allow_method_list = ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS')
    restful = RestfulDescriptor()  # 描述符

    def __call__(self, request, **kwargs):
        """分发请求"""

        method = request.method.lower()
        is_not_allow = method.upper() not in self.allow_method_list
        if is_not_allow:
            raise MethodNotAllowed()  # 请求方法在允许的列表之外

        view_func = getattr(self, method, None)
        if view_func is None:  # 请求方法被允许，但未在restful子类中定义处理代码
            raise MethodNotAllowed()
        else:
            return view_func(request, **kwargs)


class RestResponser(object):
    """restful响应器
    装载在app对象上，通过app对象注册成功和失败的响应行为。
    """

    def register_success(self, code, status=None):
        SUCCESS.set_code(code)
        if status is not None:
            SUCCESS.set_status(status)

    def register_fail(self, code_map, status=None):
        FAIL.set_code_map(code_map)
        if status is not None:
            FAIL.set_status(status)
