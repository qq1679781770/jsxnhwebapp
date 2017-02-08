#!/usr/bin/env python3
#-*- coding:utf8 -*-
#Data:2017-02-03
#Author:jsxnh(qq1679781770@gmail.com)
#version:0.1
import logging,os,asyncio,config
from aiohttp import web
from jinja2 import Environment,FileSystemLoader
from webframe import add_routes,add_static
from filters import datetime_filter,marked_filter
from orm import create_pool
from factories import auth_factory,data_factory,response_factory,logger_factory
logging.basicConfig(level=logging.INFO)

def init_jinja2(app,**kw):
    logging.info('init jinja2...')
    options={
        'autoescape':kw.get('autoescape',True),
        'block_start_string': kw.get('block_start_string', '{%'),
        'block_end_string': kw.get('block_end_string', '%}'),
        'variable_start_string': kw.get('variable_start_string', '{{'),
        'variable_end_string': kw.get('variable_end_string', '}}'),
        'auto_reload': kw.get('auto_reload', True)
    }
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters')
    if filters is not None:
        for name, ftr in filters.items():
            env.filters[name] = ftr
    app['__templating__'] = env

@asyncio.coroutine
def init(loop):
    yield from create_pool(loop,**config.db_config)
    app = web.Application(loop=loop, middlewares=[auth_factory,response_factory,logger_factory,data_factory])
    add_routes(app,'handlers')
    add_routes(app,'api')
    add_static(app)
    init_jinja2(app,filters=dict(datetime=datetime_filter, marked=marked_filter))
    srv=yield from loop.create_server(app.make_handler(),'127.0.0.1',9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv
