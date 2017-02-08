#!/usr/bin/env python3
#-*- coding:utf8 -*-
#Data:2017-02-03
#Author:jsxnh(qq1679781770@gmail.com)
#version:0.1
import asyncio
from app import init
if __name__ == '__main__':
    loop=asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()