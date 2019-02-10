# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 'author':'zouliwei'


"""中间件模块"""


import time
from abc import ABCMeta, abstractmethod

from .errors import EntryPatternError
from .response import BaseResponse


class MWManager(object):
    def __init__(self):
        self._priority_set = set()
        self._middleware_cls_set = set()
        self._mw_list = list()

    def register(self, entry_list):
        """
        中间件注册接口，可以多次注册中间件，将会根据中间件的优先级排列。
        """
        for entry in entry_list:
            self._check_pattern(entry)
            priority, middleware_cls = entry
            self._add(priority, middleware_cls())

    def _check_pattern(self, entry):
        """
        entry的格式是(priority, middleware_cls)
        """
        def check_entry(entry):
            if not isinstance(entry, (tuple, list)):
                raise EntryPatternError('the type of entry must be tuple or list')

            valid_length = len(entry) == 2
            if not valid_length:
                raise EntryPatternError('length of route entry must be 2')
            else:
                priority, middleware_cls = entry
                return priority, middleware_cls

        def check_priority(priority):
            if not isinstance(priority, int):
                raise EntryPatternError('the type of priority must be int.')

            valid_range = 0 <= priority
            if not valid_range:
                raise EntryPatternError('the range of priority must >=0.')

            if priority in self._priority_set:
                raise EntryPatternError(f"the priority: '{priority}' is already set, please change.")
            else:
                self._priority_set.add(priority)

        def check_mw_cls(mw_cls):
            if not issubclass(mw_cls, AbstractMiddleWare):
                raise EntryPatternError('the middleware cls must be subclass of AbstractMiddleWare.')

            if mw_cls in self._middleware_cls_set:
                raise EntryPatternError(f"the middleware: '{mw_cls}' is already register.")
            else:
                self._middleware_cls_set.add(mw_cls)

        priority, middleware_cls = check_entry(entry)
        check_priority(priority)
        check_mw_cls(middleware_cls)

    def _add(self, priority, mw):
        is_empty = len(self._mw_list) == 0
        if is_empty:
            self._mw_list.append((priority, mw))
            return None

        # 如果比第一个中间件的优先级还小
        first_mw_priority = self._mw_list[0][0]
        if priority < first_mw_priority:
            self._mw_list.insert(0, (priority, mw))
            return None

        # 如果比最后一个中间件的优先级还大
        last_mw_priority = self._mw_list[-1][0]
        if priority > last_mw_priority:
            self._mw_list.append((priority, mw))
            return None

        # 如果处于中间位置
        insert_index = None
        for index, _entry in enumerate(self._mw_list):
            _priority = _entry[0]
            if priority < _priority:
                insert_index = index
                break
        self._mw_list.insert(insert_index, (priority, mw))

    def pre_process(self, request):
        """
        仅修改request而不伪造
        绝大部分情况下应该返回None
        如果要截断请求，则返回response对象
        """
        for _entry in self._mw_list:
            mw = _entry[1]
            interrupt_response = mw.pre_process(request)
            if interrupt_response is not None:  # 特殊处理中断的响应对象
                if isinstance(result, BaseResponse):
                    return interrupt_response
                else:
                    raise TypeError(f'the type of response object must be BaseResponse or its subclass. current type: "{type(response)}".')
            else:
                pass
        return None

    def after_process(self, request, response):
        """
        仅修改response而不伪造，必须返回None
        """
        for _entry in reversed(self._mw_list):
            mw = _entry[1]
            mw.after_process(request, response)
        return None


class AbstractMiddleWare(object, metaclass=ABCMeta):
    """抽象中间件类，所有中间件类的定义都要继承此抽象类作为接口约束"""
    
    @abstractmethod
    def pre_process(self, request):
        pass

    @abstractmethod
    def after_process(self, request, response):
        pass
