# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 'author':'zouliwei'


"""渲染模块"""


from jinja2 import Environment, FileSystemLoader

from .response import RenderResponse


class Render(object):
    """基于jinja2的模板渲染器"""

    def __init__(self):
        self.jinja = None

    def register(self, template_path):
        self.jinja = Environment(
            loader=FileSystemLoader(template_path),
            autoescape=True,
        )
        RenderResponse.set_render(self)  # 设置RenderResponse响应对象的属性

    def render(self, template_name, **context):
        t = self.jinja.get_template(template_name)  # call jinja.get_tempalte()
        return t.render(context)
