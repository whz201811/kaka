# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 'author':'zouliwei'


"""错误定义"""


class Error(Exception):
    pass

class HTMLRenderError(Error):
    pass

class ReverseURLFailedError(Error):
    pass

class RestResponserHandlerError(Error):
    pass
