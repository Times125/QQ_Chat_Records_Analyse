#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author:lichunhui
@Time:  2018/1/13 22:59
@Description: 
"""
import os
import re
import jieba
from src.config import material
from src.mredis import MyRedis


# 从txt文件中读取数据，利用正则匹配想要的数据
def read_data():
    fn = os.path.join(material, 'records.txt')
    with open(fn, 'r', encoding='utf-8', errors='ignore') as reader:
        txt = reader.read()
        re_pat = r'20[\d-]{8}\s[\d:]{7,8}\s+[^\n]+(?:\d{5,11}|@\w+\.[comnetcn]{2,3})\)'  # 正则语句，匹配记录头
        log_title_arr = re.findall(re_pat, txt)  # 记录头数组['2016-06-24 15:42:52  张某(40**21)',…]
        log_content_arr = re.split(re_pat, txt)[1:]  # 记录内容数组['\n', '\n选修的\n\n', '\n就怕这次…]

        print(len(log_title_arr), '---', len(log_content_arr))

        entity = []  # 存放（日期，qq号，内容）
        for i in range(int(len(log_title_arr))):
            date = re.search(r'20[\d-]{8}\s[\d:]{7,8}', log_title_arr[i]).group()  # 匹配记录头中的时间
            qq = re.search(r'(?<=\()[^\)]+', log_title_arr[i]).group()  # 匹配记录头中的QQ号
            content = log_content_arr[i].strip('\n')
            entity.append((date, qq, content))
            print(date)
            print(qq)
            print(content)  # 聊天内容

    rdis = MyRedis.get_redis_instance()  # 获得一个redis实例
    rdis.set('test', 'test')
    print('done!')
