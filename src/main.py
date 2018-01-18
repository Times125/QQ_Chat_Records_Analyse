#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author:lichunhui
@Time:  2018/1/14 18:12
@Description: 
"""

from src.analyse import *


def main():
    read_data()
    analyse()
    # lst = ['感觉搞无机的太少了', '她是个善良的女孩，温柔可爱', '今天天气不错，让我心情舒畅', '我真的很伤心啊', '我真的很无聊啊','他们肯定太无聊了']
    # print(lst.index('我真的很伤心啊'))
    # print([i for i, x in enumerate(lst) if x == '我真的很伤心啊'])
    # for i in lst:
    #     s = SnowNLP(i)
    #     print(s.sentiments)


if __name__ == '__main__':
    main()
