#!/usr/bin/env python3
#-*- coding:utf8 -*-
#Data:2017-02-05
#Author:jsxnh(qq1679781770@gmail.com)
#version:0.1
import re, time, json, logging, hashlib, base64, asyncio
from models import User, Comment, Blog,Message, next_id
from webframe import get,post
from aiohttp import web
from factories import COOKIE_NAME
from helper import get_page_index,Page
from datetime import datetime

def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)
 
@get('/')
def index(*, page='1'):
    date=time.time()
    dt = datetime.fromtimestamp(date)
    page_index = get_page_index(page)
    num = yield from Blog.findNumber('count(id)')
    page = Page(num,page_index)
    if num == 0:
        blogs = []
    else:
        blogs = yield from Blog.findAll(orderBy='created_at desc', limit=(page.offset, page.limit))
    return {
        '__template__': 'blogs.html',
        'page': page,
        'blogs': blogs,
        'dt':dt
    }

@get('/message')
def message():
    messages=yield from Message.findAll(orderBy='created_at desc')
    return{
        '__template__':'message.html',
        'messages':messages
    }

@get('/register')
def register():
    return{
        '__template__':'register.html'
    }

@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
}

@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r

@get('/blog/{id}')
def get_blog(id):
    blog = yield from Blog.find(id)
    '''
    
    '''
    comments = yield from Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    
    for c in comments:
        c.html_content = text2html(c.content)
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments
    }

@get('/manage/blogs/create')
def manage_create_blog():
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs'
    }

@get('/manage/blogs/edit')
def manage_edit_blog(*, id):
    return {
        '__template__': 'manage_blog_edit.html',
        'id': id,
        'action': '/api/blogs/%s' % id
    }

@get('/manage/blogs')
def manage_blogs(*, page='1'):
    page_index = get_page_index(page)
    num = yield from Blog.findNumber('count(id)')
    page = Page(num,page_index)
    return {
        '__template__': 'manage_blogs.html',
        'page': page
    }