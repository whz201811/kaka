# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 'author':'zlw'


"""模块组装"""


from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from werkzeug.exceptions import HTTPException

from .middlewares import MWManager
from .routing import Router
from .render import Render
from .restful import RestResponser


# 中间件管理器
mw_manager = MWManager()

# 主路由器
router = Router()

# 模板渲染器
render = Render()

# rest响应器
rest_responser = RestResponser()

# 框架内部的模块映射表
_inner_module_map = {
    # module_name: module_instance
    'mw_manager': mw_manager,
    'router': router,
    'render': render,
    'rest_responser': rest_responser,
}
