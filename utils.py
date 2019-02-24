# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 'author':'zouliwei'


"""公用工具模块"""


from werkzeug.routing import redirect as werkzeug_redirect

from .response import BaseResponse
# from .combinations import router


def redirect(location, code=302):
    return werkzeug_redirect(location, code, BaseResponse)


# def reverse(name, value_dict=None, query_dict=None):
#     return router.reverse(name, value_dict, query_dict)
# TODO: 考虑如何完成reverse函数
