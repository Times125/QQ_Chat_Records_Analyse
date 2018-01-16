#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author:lichunhui
@Time:  2018/1/13 22:59
@Description: 
"""
import re
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from src.config import *
from scipy.misc import imread
from src.mredis import MyRedis

entity = []  # 存放（日期，qq号，内容）
times = []
qqs = []
contents = []


# 从txt文件中读取数据，利用正则匹配想要的数据
def read_data():
    fn = os.path.join(material, 'records.txt')
    with open(fn, 'r', encoding='utf-8', errors='ignore') as reader:
        txt = reader.read()
        re_pat = r'20[\d-]{8}\s[\d:]{7,8}\s+[^\n]+(?:\d{5,11}|@\w+\.[comnetcn]{2,3})\)'  # 正则语句，匹配记录头
        log_title_arr = re.findall(re_pat, txt)  # 记录头数组['2016-06-24 15:42:52  张某(40**21)',…]
        log_content_arr = re.split(re_pat, txt)[1:]  # 记录内容数组['\n', '\n选修的\n\n', '\n就怕这次…]

        print(len(log_title_arr), '---', len(log_content_arr))
        for i in range(int(len(log_title_arr))):
            date = re.search(r'20[\d-]{8}\s[\d:]{7,8}', log_title_arr[i]).group()  # 匹配记录头中的时间
            qq = re.search(r'(?<=\()[^\)]+', log_title_arr[i]).group()  # 匹配记录头中的QQ号
            content = log_content_arr[i].strip('\n')  # 聊天内容
            times.append(date)  # 记录所有的聊天日期
            qqs.append(qq)  # 所有qq
            contents.append(content)  # 所有聊天内容
            entity.append((date, qq, content))
        print(len(times), '---', len(contents))
    '''
    rdis = MyRedis.get_redis_instance()  # 获得一个redis实例
    rdis.set('entity', entity)
    rdis.set('times', times)
    rdis.set('qqs', qqs)
    rdis.set('contents', contents)
    '''


# 进行聊天记录分析
def analyse():
    counter_res = Counter(qqs)  # 统计出发言频率
    most_active_person = dict([(k, v) for k, v in counter_res.most_common(100)])  # 最活跃的50个人
    total_chat_person = len(counter_res)  # 记录中参与聊天总人数
    print(most_active_person)
    print(total_chat_person)
    draw(most_active_person, 'most_active_person.jpg', 'longmao.jpg')
    # 利用结巴分词对聊天内容进行处理
    with open(os.path.join(material, 'ch_stopwords.txt'), 'r', encoding='utf-8', errors='ignore') as reader:
        lines = reader.readlines()
        stopwords = [sw.strip('\n') for sw in lines]
        print('停用词=====', stopwords)
    res_list = []
    jieba.load_userdict(os.path.join(material, 'jieba_usr_dict.txt'))  # 自定义词典
    for content in contents:
        seg_list = jieba.cut(content, cut_all=False)
        seg_list = [sl for sl in seg_list if sl not in stopwords]
        print(seg_list)
        if len(seg_list) != 0:
            res_list.extend(seg_list)
    # 获取关键词
    content_counter = Counter(res_list)
    most_hot_topic = dict([(k, v) for k, v in content_counter.most_common(600)])  # 谈论最多的话题点
    most_hot_topic.pop(' ')  # 删除空白项
    print(most_hot_topic)
    draw(most_hot_topic, 'most_hot_topic.jpg', 'longmao.jpg')


# 显示统计结果
def draw(counter_dict, file_name, mask_name):
    mask = imread(os.path.join(material, mask_name))
    wc = WordCloud(font_path=font_path, width=1046, height=1066, background_color="white",
                   relative_scaling=.6, max_words=1000, mask=mask, max_font_size=100)
    wc.fit_words(counter_dict)  # 字体大小和词频有关
    wc.to_file(os.path.join(output_path, file_name))  # 将词云导出到文件
    '''
    # plt 画图
    plt.figure()
    plt.imshow(wc)
    plt.axis("off")
    plt.show()
    '''