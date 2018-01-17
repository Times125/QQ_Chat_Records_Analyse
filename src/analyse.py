#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author:lichunhui
@Time:  2018/1/13 22:59
@Description: 
"""
import re
import jieba
import jieba.analyse
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from src.config import *
from scipy.misc import imread
from src.mredis import MyRedis
from snownlp import SnowNLP
from src.classify import SVMClassifer

entity = []  # 存放（日期，qq号，内容）
times = []  # 日期-时间
hours = []  # 一天中聊天人数最多的时刻
qqs = []  # 所有参与聊天的qq号
contents = []  # 所有聊天内容


# 从txt文件中读取数据，利用正则匹配想要的数据
def read_data():
    """
    从导出的qq群聊天记录中获取想要的数据，包括时间，成员，内容
    :return: Nothing
    """
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
            hour = re.search(r'(?<=\s)[^\:]+', date).group()  # 一天中聊天的时刻
            times.append(date)  # 记录所有的聊天日期
            hours.append(hour)  # 记录所有聊天时刻点
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
    """
    对聊天记录进行分析，包括统计参与聊天总人数，最近活跃人数，最活跃的群成员，聊天热点话题，用户情感等等
    :return: Nothing
    """
    counter_res = Counter(qqs)  # 统计出发言频率
    most_active_person = dict([(k, v) for k, v in counter_res.most_common(100)])  # 最活跃的50个人
    total_chat_person = len(counter_res)  # 记录中参与聊天总人数
    print(most_active_person)
    print(total_chat_person)
    draw(most_active_person, 'most_active_person.jpg', 'chongqing.jpg')
    # 利用结巴分词对聊天内容进行处理
    with open(os.path.join(material, 'ch_stopwords.txt'), 'r', encoding='utf-8', errors='ignore') as reader:
        lines = reader.readlines()
        stopwords = [sw.strip('\n') for sw in lines]
        stopwords.append(' ')
        stopwords.append('\n')
        # print('停用词=====', stopwords)
    res_list = []
    jieba.load_userdict(os.path.join(material, 'jieba_usr_dict.txt'))  # 自定义词典
    for content in contents:
        seg_list = jieba.cut(content, cut_all=False)
        seg_list = [sl for sl in seg_list if sl not in stopwords]
        if len(seg_list) != 0:
            res_list.extend(seg_list)
    # 统计频次最高的词
    content_counter = Counter(res_list)
    most_hot_topic = dict([(k, v) for k, v in content_counter.most_common(600)])  # 谈论最多的话题点
    print(most_hot_topic)
    draw(most_hot_topic, 'most_hot_word.jpg', 'longmao.jpg')

    # 基于TextRank 算法的关键词抽取
    sentence = ''.join(res_list)
    # print(sentence, '===')
    text_rank = jieba.analyse.textrank(sentence, topK=150, withWeight=False,
                                       allowPOS=('ns', 'n', 'vn', 'v', 'adj'))  # 100个关键词
    print(text_rank)
    draw(text_rank, 'most_hot_topic_tr.jpg', 'china.jpg')

    # 分析一天中群最活跃的时间段
    hours_counter_res = Counter(hours)
    hours_counter = dict([(k + '点', v) for k, v in hours_counter_res.most_common(24)])
    print(hours_counter)
    draw(hours_counter, 'most_active_hour.jpg', 'huoguo.jpg')
    txt = '我今天很伤心啊'
    emotion_analyse(txt)


# 对单个qq用户的情感分析
def emotion_analyse(txt=None):
    """
    desc:对单个qq用户的情感分析，推测此用户的性格以及生活习惯等,利用工具SnowNLP
    :param txt: 传入需要分析的内容text
    :return:
    """
    s = SnowNLP(txt)
    print(s.sentiments)


# 显示统计结果
def draw(counter_res, file_name, mask_name):
    """
    将结果用词云展示
    :param counter_res:dict or list
    :param file_name: the output file name
    :param mask_name: mask picture file name
    :return: Nothing
    """
    mask = imread(os.path.join(material, mask_name))
    wc = WordCloud(font_path=font_path, width=1046, height=1066, background_color="white",
                   relative_scaling=.6, max_words=1000, mask=mask, max_font_size=100)
    if type(counter_res) is dict:
        print(type(counter_res) is dict)
        wc.fit_words(counter_res)  # 字体大小和词频有关
    elif type(counter_res) is list:
        print(type(counter_res) is list)
        wc.generate(' '.join(counter_res))
    wc.to_file(os.path.join(output_path, file_name))  # 将词云导出到文件
    '''
    # plt 画图
    plt.figure()
    plt.imshow(wc)
    plt.axis("off")
    plt.show()
    '''
