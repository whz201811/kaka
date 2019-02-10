# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 'author':'zlw'


from werkzeug.exceptions import HTTPException, NotFound, MethodNotAllowed
from werkzeug.routing import RequestRedirect
from werkzeug.serving import run_simple

from .combinations import _inner_module_map
from .errors import ModuleIsAlreadyInstalledError
from .request import BaseRequest
from .response import BaseResponse


class KaKa():
    """
    app应用负责接收底层服务器传入的每一次的http请求并生成正确的响应然后返回给底层服务器。
    app通过引入各种模块以扩展自身的能力，最基本的模块是：路由系统、中间件系统。

    1. 所有的请求和响应对象均以BaseRequest和BaseReponse为基类。
    2. 请求和响应对象在中间件中不得伪造，但可修改。
    """

    def __init__(self):
        self._install_modules(_inner_module_map)  # 安装内部模块

    def __call__(self, environ, start_response):
        return self._wsgi_api(environ, start_response)

    def _wsgi_api(self, environ, start_response):  # http api接口
        response = self._deal_with(environ)
        return response(environ, start_response)

    def _deal_with(self, environ):  # 核心处理接口
        request = BaseRequest(environ)
        response = None

        def hook_pre_process():
            """不允许伪造request，只允许修改request或者返回response
            所以必须返回None或者response对象
            """
            interrupt_response = self.mw_manager.pre_process(request)
            return interrupt_response

        def route():
            view, kwargs = self.router.route(environ)
            return view, kwargs

        def process(view, kwargs):
            response = view(request, **kwargs)
            return response

        def check_type(response):
             """检查响应对象的类型，必须是BaseResponse及其子类"""
             is_valid_type = isinstance(response, BaseResponse)
             if not is_valid_type:
                raise TypeError(f'the type of response object must be BaseResponse or its subclass. current type: "{type(response)}".')

        def hook_after_process():
            """不允许伪造response，只允许修改response,所以必须返回None"""
            self.mw_manager.after_process(request, response)

        def start():
            interrupt_response = hook_pre_process()
            if interrupt_response is not None:  # 特殊处理中断对象(拦截请求并直接要求返回的对象)
                check_type(interrupt_response)
                return interrupt_response
            else:  # 否则什么也不做,继续处理
                pass

            view, kwargs = route()  # NotFoundError, RequestRedictError

            nonlocal response
            response = process(view, kwargs)  # MethodNotAllowdError(with restful)
            check_type(response)

            hook_after_process()

        try:
            start()
        except (NotFound, RequestRedirect, MethodNotAllowed)  as exc:  # 这些错误对象可以作为response对象返回
            return exc

        return response

    def _install_modules(self, module_map):
        """安装内部模块的接口，暂不对用户开放"""

        def not_installed(name):
            return getattr(self, name, None) is None

        def install(name, module):
            setattr(self, name, module)

        for name, module in module_map.items():
            if not_installed(name) is True:
                install(name, module)
            else:
                raise ModuleIsAlreadyInstalledError(f"the module '{name}' is already installed.")

    def run_server(self, host='localhost', port=8888, debug=False):
        """服务器启动接口，默认本地环回口，端口号8888"""
        use_reloader = debug
        use_debugger = debug
        
        run_simple(
            hostname=host,
            port=port,
            application=self,
            use_reloader=use_reloader,
            use_debugger=use_debugger,
        )
