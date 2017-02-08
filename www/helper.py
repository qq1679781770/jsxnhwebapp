#!/usr/bin/env python3
#-*- coding:utf8 -*-
#Data:2017-02-04
#Author:jsxnh(qq1679781770@gmail.com)
#version:0.1





class Page(object):

    def __init__(self,item_count,page_index=1,page_size=10):
        self.item_count=item_count
        self.page_size=page_size
        self.page_count=item_count//page_size+(1 if item_count%page_size>0 else 0)
        if(item_count==0) or (page_index>self.page_count):
            self.offset=0
            self.limit=0
            self.page_index=1
        else:
            self.page_index=page_index
            self.offset=self.page_size*(page_index-1)
            self.limit=self.page_size
        self.has_next=self.page_index<self.page_count
        self.has_previous=self.page_index>1

    def __str__(self):
        return 'item_count: %s, page_count: %s, page_index: %s, page_size: %s, offset: %s, limit: %s' % (self.item_count, self.page_count, self.page_index, self.page_size, self.offset, self.limit)

def get_page_index(page_str):
    p=1
    try:
        p=int(page_str)
    except ValueError as e:
        pass
    if p<1:
        p=1
    return p               