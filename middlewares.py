# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 'author':'zouliwei'


"""中间件模块"""


from copy import deepcopy
from abc import ABCMeta,abstractmethod
from .response import BaseResponse


class MiddleWareManager(object):
    def __init__(self):
        self.entry_list = list()  # 记录表，存储中间件记录
        self.middleware_list = list()  # 中间件列表，存储中间件实例化对象
        self.support_stack = list()  # 辅助栈，用于反向遍历

    def register(self, entry_list):
        for entry in entry_list:
            self.entry_list.append(deepcopy(entry))
        self.entry_list.sort(key=lambda entry: entry.priority)
        self._build()

    def _build(self):
        self.middleware_list.clear()

        for entry in self.entry_list:
            self.middleware_list.append(entry.cls())

    def iter_before(self, request):
        """请求处理前的遍历操作"""

        for middleware in self.middleware_list:
            interrupt = middleware.before_process(request)
            self.support_stack.append(middleware)

            if interrupt is not None:  # 发生中断
                assert isinstance(interrupt, BaseResponse), '中断对象必须是响应类型'
                self.iter_after(request, interrupt)
                return interrupt
        return None

    def iter_after(self, request, response):
        """请求处理后或中断后的遍历操作"""

        stack_empty = lambda : len(self.support_stack) == 0
        while not stack_empty():
            middleware = self.support_stack.pop()
            middleware.after_process(request, response)
        return None


# 中间件api
class AbstractMiddleWare(object, metaclass=ABCMeta):
    @abstractmethod
    def before_process(self, request):
        pass

    @abstractmethod
    def after_process(self, request, response):
        pass


class MiddleWareEntry(object):
    def __init__(self, priority, cls, name):
        # TODO: 后续增加path_or_cls，使得用户可以输入中间件类的路径名称或类对象
        self.priority = priority
        self.cls = cls
        self.name = name
