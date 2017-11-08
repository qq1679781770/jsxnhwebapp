#!/usr/bin/env python3
# -*- coding:utf8 -*-
# Data:2017-08-23
# Author:jsxnh(qq1679781770@gmail.com)
# version:0.1

import time, uuid
from orm import Model, StringField, BooleanField, FloatField, TextField,IntegerField


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(Model):
    __table__ = 'users'
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)


class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)


class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)


class Message(Model):
    __table__ = 'messages'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)


class Account(Model):

    __table__ = 'account'

    id = StringField(primary_key=True, ddl='varchar(50)')
    app = StringField(ddl='varchar(50)')
    account = StringField(ddl='varchar(50)')
    password = StringField(ddl='varchar(50)')
    message = TextField()

class Story(Model):

    __table__ = 'story'
    id = IntegerField(primary_key=True)
    question = StringField(ddl='varchar(200)')
    content = TextField()
    islook = IntegerField()


