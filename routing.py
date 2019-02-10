# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 'author':'zouliwei'


"""路由模块"""


from werkzeug.routing import Map, Rule, BuildError
from werkzeug.exceptions import HTTPException

from .errors import (
    RouteRegisterError,
    EntryPatternError,
    TableBuildError,
    ReverseURLFailedError,
)


class Router():
    """
    路由器类
    定义了路由表注册、路由搜索、反向查询等接口，且可以实现多级路由分发。
    """

    def __init__(self):
        self.table = list()
        self._url_set = set()
        self._name_set = set()
        self._url_map = None
        self._view_map = None
        self._map_adapter = None

    def route(self, environ):
        """路由查找"""

        map_adapter = self._url_map.bind_to_environ(environ)  # call werkzeug.routing.Map().bind_to_environ
        self._map_adapter = map_adapter
        endpoint, kwargs = map_adapter.match()  # call mapadapter.match

        if callable(endpoint):  # endpoint is view
            return view, kwargs
        else:  # endpoint is name
            view = self._view_map.get(endpoint)
            assert view is not None and callable(view), 'stop route because the view searched is not correct'
            return view, kwargs

    def reverse(self, name, value_dict=None, query_dict=None):
        """反向搜索"""

        values = dict()
        if value_dict is not None:
            values.update(value_dict)
        if query_dict is not None:
            values.update(query_dict)

        try:
            url = self._map_adapter.build(
                endpoint=name,
                values=values,
            )

        except BuildError as why:
            raise ReverseURLFailedError(why)

        return url

    def register(self, entry_list):
        """路由表注册接口
        此接口将会处理用户提供的路由表entry_list。
        此接口要求路由表中的url**不能有前导斜杠**(为了防止多级路由拼接时错误)，
        但最终在调用底层werkzeug的map前会为路由表整体加上一个前导斜杠(底层map要求前导斜杠)。
        """

        try:
            for entry in entry_list:
                self._check_pattern(entry)  # entry pattern error
                url, view, *name = entry

                if self._is_router(view):  # 意味着是一个子路由器
                    self._merge_table(url, view, *name)  # table build error
                else:
                    self._build_table(url, view, *name)  # table build error

        except (EntryPatternError, TableBuildError):
            raise RouteRegisterError()

        self._build_map()

    def _check_pattern(self, entry):
        """
        entry的格式是(url, view or sub_route, <name>)
        """

        def check_entry(entry):
            if not isinstance(entry, (tuple, list)):
                raise EntryPatternError('the type of entry must be tuple or list.')

            valid_length = 2<= len(entry) <= 3
            if not valid_length:
                raise EntryPatternError('length of route entry must be 2 or 3.')
            else:
                url, view, *name = entry
                return url, view, name

        def check_url(url):
            if not isinstance(url, str):
                raise EntryPatternError('the type of url must be str.')

            # if url.startswith('/'):
            #     raise EntryPatternError("url do not start with a leading slash: '/'.")

            if not url.endswith('/'):
                raise EntryPatternError("url must end with a tailing slash: '/'.")

        def check_view(view):
            if not callable(view):
                if isinstance(view, Router):
                    pass
                else:
                    raise EntryPatternError('the view must be callable.')

        def check_name(name):
            has_name = len(name) == 1
            if has_name:
                name = name[0]
                if not isinstance(name, str):
                    raise EntryPatternError('the type of name must be str.')

        url, view, name = check_entry(entry)
        check_url(url)
        check_view(view)
        check_name(name)

    def _is_router(self, view):
        return isinstance(view, Router)

    def _merge_table(self, url, sub_router, *name):
        """合并子路由器的路由表"""

        sub_table = sub_router.table

        for sub_entry in sub_table:
            sub_url, sub_view, *sub_name = sub_entry
            merge_url = ''.join([url, sub_url])
            self._check_exist_url(merge_url)

            # merge name and merge table
            if len(sub_name) == 1:
                if len(name) == 1:
                    merge_name = ':'.join([name[0], sub_name[0]])  # example: 'blog:articles'
                else:
                    merge_name = sub_name[0]
                self._check_exist_name(merge_name)
                self.table.append((merge_url, sub_view, merge_name))
            else:
                self.table.append((merge_url, sub_view))

    def _build_table(self, url, view, *name):
        self._check_exist_url(url)

        if len(name) == 1:
            name = name[0]
            self._check_exist_name(name)
            self.table.append((url, view, name))
        else:
            self.table.append((url, view))

    def _check_exist_url(self, url):
        if url in self._url_set:
            raise TableBuildError(f"the url '{url}' is already exist, please check your route table.")
        self._url_set.add(url)

    def _check_exist_name(self, name):
        if name in self._name_set:
            raise TableBuildError(f"the entry name '{name}' is already exist, please change another.")
        self._name_set.add(name)

    def _build_map(self):
        """构造底层werkzeug的map对象"""

        # build rule list
        rule_list = list()
        view_map = dict()

        for entry in self.table:
            url, view, *name = entry
            url = self._add_leading_slash(url)
            has_name = len(name) == 1

            if has_name:
                name = name[0]
                rule = Rule(url, endpoint=name)
                view_map[name] = view
            else:
                rule = Rule(url, endpoint=view)
            rule_list.append(rule)

        # build map
        self._url_map = Map(rule_list)
        self._view_map = view_map

    def _add_leading_slash(self, url):
        """添加前导斜杠，仅用于_build_map方法中。"""
        return '/' + url
