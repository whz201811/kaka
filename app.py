# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 'author':'zlw'


from werkzeug.exceptions import HTTPException, NotFound, MethodNotAllowed
from werkzeug.routing import RequestRedirect
from werkzeug.serving import run_simple

from .errors import ModuleIsAlreadyInstalledError
from .request import BaseRequest
from .render import Render
from .restful import RestResponser
from .routing import Router
from .response import BaseResponse

from .middlewares import MiddleWareManager
from .request import BaseRequest
from werkzeug.routing import NotFound


class KaKa():
    def __init__(self):
        self.middleware_manager = MiddleWareManager()
        self.router = Router()
        self.render = Render()
        self.rest_responser = RestResponser()

    def __call__(self, environ, start_response):
        response = self._deal_with(environ)
        return response(environ, start_response)

    def _deal_with(self, environ):
        """web框架核心驱动"""

        request = self._build_request(environ)

        interrupt = self._hook_before_process(request)
        if interrupt is not None:
            return interrupt

        try:
            view, kwargs = self._route(request)
            response = view(request, **kwargs)
        except HTTPException as exc:
            return exc

        self._hook_after_process(request, response)
        return response

    def _build_request(self, environ):
        request = BaseRequest(environ)
        return request

    def _hook_before_process(self, request):
        interrupt = self.middleware_manager.iter_before(request)
        return interrupt

    def _route(self, request):
        view, kwargs = self.router.route(request)
        return view, kwargs

    def _hook_after_process(self, request, response):
        self.middleware_manager.iter_after(request, response)

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
