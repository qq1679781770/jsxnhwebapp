#!/usr/bin/env python3
#-*- coding:utf8 -*-
#Data:2017-02-03
#Author:jsxnh(qq1679781770@gmail.com)
#version:0.1
import asyncio,functools,inspect,logging,os
from aiohttp import web
from error import APIError

def request(path,*,method):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kw):
            return func(*args,**kw)
        wrapper.__method__=method
        wrapper.__route__=path
        return wrapper
    return decorator

get=functools.partial(request,method='GET')
post=functools.partial(request,method='POST')
put=functools.partial(request,method='PUT')
delete=functools.partial(request,method='DELETE')

class RequestHandler(object):
    def __init__(self,func):
        self._func=asyncio.coroutine(func)
    @asyncio.coroutine
    def __call__(self,request):
        required_args=inspect.signature(self._func).parameters
        logging.info('required args: %s' % required_args)
        kw = {arg: value for arg, value in request.__data__.items() if arg in required_args}
        kw.update(request.match_info)
        if 'request' in required_args:
            kw['request'] = request
        for key, arg in required_args.items():
            if key == 'request' and arg.kind in (arg.VAR_POSITIONAL, arg.VAR_KEYWORD):
                return web.HTTPBadRequest(text='request parameter cannot be the var argument.')
            if arg.kind not in (arg.VAR_POSITIONAL, arg.VAR_KEYWORD):
                if arg.default == arg.empty and arg.name not in kw:
                    return web.HTTPBadRequest(text='Missing argument: %s' % arg.name)
        logging.info('call with args: %s' % kw)
        try:
            r = yield from self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)

def add_static(app):
    path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'static')
    app.router.add_static('/static/',path)
    logging.info('add static %s=>%s'%('/static/',path))

def add_route(app,fn):
    method=getattr(fn,'__method__',None)
    path=getattr(fn,'__route__',None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(fn))

def add_routes(app,module_name):
    n=module_name.rfind('.')
    if n==(-1):
        mod=__import__(module_name, globals(), locals())
    else: 
        name=module_name[n+1:]
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        fn=getattr(mod,attr)
        if callable(fn):
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            if method and path:
                add_route(app,fn)
