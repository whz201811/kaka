# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 'author':'zouliwei'


"""路由模块"""


from werkzeug.routing import Map, Rule


class Router(object):
    def __init__(self):
        self.view_map = dict()
        self.table = list()
        self.url_set = set()
        self.name_set = set()
        self.map = None
        self.map_adapter = None

    def register(self, entry_list):
        for entry in entry_list:
            url, nexthop, name = entry

            if isinstance(nexthop, Router):  # 归并子路由表
                self.merge(url, nexthop, name)
            elif callable(nexthop):  # 加入路由表
                self.add(url, nexthop, name)
            else:
                raise TypeError('路由条目的endpoint字段必须是子路由器或视图函数')

        self._build_map()

    def route(self, request):
        self.map_adapter = self.map.bind_to_environ(request.environ)
        endpoint, kwargs = self.map_adapter.match()
        view = self.view_map.get(endpoint)
        return view, kwargs

    def merge(self, url, sub_router, name):
        sub_table = sub_router.table

        for sub_entry in sub_table:
            sub_url, sub_nexthop, sub_name = sub_entry
            new_url = url + sub_url
            new_name = name + ':' + sub_name
            self.add(new_url, sub_nexthop, new_name)

    def add(self, url, nexthop, name):
        self._check(url, nexthop, name)
        if url == '':
            url = '/'
        self.table.append(
            (url, nexthop, name)
        )

    def _build_map(self):
        self.map = Map()

        for entry in self.table:
            url, nexthop, name = entry
            self.map.add(
                Rule(url, endpoint=name)
            )
            self.view_map[name] = nexthop

    def _check(self, url, nexthop, name):
        if url.endswith('/'):
            raise ValueError('url不允许有后导/')

        if url in self.url_set:
            raise ValueError(f'url {url} 已经存在')
        else:
            self.url_set.add(url)

        if name in self.name_set:
            raise ValueError(f'name {name} 已经存在')
        else:
            self.name_set.add(name)

    def reverse(self, name, value_dict=None, query_dict=None):
        """反向搜索"""

        values = dict()
        if value_dict is not None:
            values.update(value_dict)
        if query_dict is not None:
            values.update(query_dict)

        url = self.map_adapter.build(
            endpoint=name,
            values=values,
        )
        return url

class RouteEntry(object):
    def __init__(self, url, nexthop, name):
        self.url = url
        self.nexthop = nexthop
        self.name = name

    def __iter__(self):
        return iter([self.url, self.nexthop, self.name])


# 测试用例
if __name__ == '__main__':
    sub_router = Router()
    sub_router.register([
        RouteEntry('/articles', lambda :'a', 'articles'),
    ])
    sub_router2 = Router()
    sub_router2.register([
        RouteEntry('/articles', lambda :'a', 'articles2'),
    ])
    routes = [
        RouteEntry(url='/index', nexthop=lambda :'23', name='index'),
        RouteEntry(url='/blog', nexthop=sub_router, name='blog'),
        RouteEntry(url='/abc', nexthop=sub_router2, name='blog'),
    ]
    router = Router()
    router.register(routes)

    print(router.table)
    print(router.map)
    print(router.view_map)
