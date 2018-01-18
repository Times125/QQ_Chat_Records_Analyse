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
    hours_counter = dict([(k + '时', v) for k, v in hours_counter_res.most_common(24)])
    print(hours_counter)
    draw(hours_counter, 'most_active_hour.jpg', 'huoguo.jpg')

    # 分析用户情感，推测用户性格
    txt = []
    user_sentiment = {}
    for qq in most_active_person:
        person_index = [i for i, x in enumerate(qqs) if x == qq]  # 最活跃的人的聊天记录的位置
        for i in person_index:
            txt.append(contents[i])
        sentiment_index = emotion_analyse(txt, qq)  # 计算此qq用户的情感指数
        user_sentiment[qq] = sentiment_index
    print(user_sentiment)
    """
    {'1209101643': 0.5427812816478225, '745500530': 0.5507599248949117, '1051617442': 0.5530599685557689, '1045048548': 0.5499328897910526, '2642574488': 0.5446383498406289, '402376637': 0.5407447368409908, '1764011453': 0.5369646476046138, '1251680944': 0.5354333781521334, '1219398106': 0.5364054328018658, '599292912': 0.5364656951947343, '1913409863': 0.53484067081695, '309031584': 0.5344930942030883, '545184326': 0.5341362432855117, '1329636023': 0.53325216105234, '710258421': 0.5330333058797951, '673853621': 0.5326860825299103, '754315527': 0.5321570979667783, '1965083476': 0.5316905993321258, '1141569440': 0.5316969969482886, '2275444386': 0.5306393358854631, 'loyalnovakshayne@qq.com': 0.5310336921617058, '1115133277': 0.5309162264601218, '1715474300': 0.5309849111992685, '122780300': 0.5309933866294124, '10000': 0.5284466697252308, '1227832488': 0.5283585964515772, '1316141782': 0.5285967890143103, '1344754848': 0.5286674077843782, '1241927211': 0.528424292537605, '1278678748': 0.5280859518868842, '1196042086': 0.5280284458864, '784319656': 0.5284060134894644, '452335534': 0.5286984475623131, '2914707056': 0.5287701425196093, '1278109751': 0.5290585856871963, '837125065': 0.5291170420305971, '1064278183': 0.5291016493609904, '798955866': 0.5294630944685925, '1085578433': 0.52930914248514, '422938365': 0.5295712616540428, '1457556035': 0.5296832347357361, '1129344867': 0.5296765800798483, '1822118385': 0.5297533989900461, '2422197668': 0.5297322708242689, '1061275041': 0.5298537037626699, '393989256': 0.5297992500496315, '1105081309': 0.5299694494350515, '747544291': 0.5301582266477316, '357190318': 0.5301595769523562, '121289126': 0.5302845157303446, '1095736889': 0.5303553062869905, '1272082503': 0.5305090612032322, '309941018': 0.5304935382513758, '251604829': 0.5305276413428799, '876705832': 0.5307866870732014, '1351461971': 0.5308601636552932, '363374239': 0.5308308896578008, '328054694': 0.5307810877049866, '504133892': 0.5307463796609506, '641097301': 0.5308282628491252, '506640120': 0.5308740152452233, '812749634': 0.5309081934474766, '961357326': 0.5310443894354496, '568588075': 0.5311020621084173, '904349494': 0.5311619995291751, '1098224615': 0.5311377240414275, '865845406': 0.5311768177693404, '750479251': 0.531187383565594, '1030201081': 0.5311473874833691, '769031687': 0.5309991086644246, '1006392533': 0.5309762045576085, '1009132098': 0.531084708728667, '877697004': 0.5310824284067153, '835194461': 0.5310894638634346, '815263592': 0.5311570717128403, '836483716': 0.5312497820063115, '295083887': 0.531316229230391, '986048812': 0.5312283218489628, '1732376703': 0.53123102278883, '1176781811': 0.531317643774081, '1146751230': 0.5313541708299178, '464870515': 0.5312882048083162, '591985453': 0.5313028049854518, '1503484527': 0.5313465383938655, '846522909': 0.5313583909940992, '244665984': 0.5313870427657331, '761631604': 0.5313994868892827, '1647036905': 0.5313838526108119, '2280737669': 0.5314268451643539, '505420996': 0.5315191037434139, '296585171': 0.5314684837901023, '1985059595': 0.5315002259629534, '3038798137': 0.5315600243751035, '1478620363': 0.5315204256725709, '1194906693': 0.5315078156451286, '849350590': 0.5315612858290759, '1069045056': 0.5315969839355288, '1195912410': 0.5316059291585217, '1172596168': 0.5315992909922406, '774110694': 0.5316443354015329}
    """


# 对单个qq用户的情感分析
def emotion_analyse(txt_lst=None, qq=None):
    """
    desc:对单个qq用户的情感分析，推测此用户的性格以及生活习惯等,利用工具SnowNLP
    :param txt_lst: 传入需要分析的内容text
    :param qq: 传入被分析人的qq
    :return: 用户情感打分
    """
    if txt_lst is None or qq is None:
        return
    sentiment_scores = 0.0
    for txt in txt_lst:
        if len(txt) == 0:
            txt = ' '
        s = SnowNLP(txt)
        sentiment_scores += s.sentiments
        print(sentiment_scores, '<<<=====', qq)
    return sentiment_scores / len(txt_lst)


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
