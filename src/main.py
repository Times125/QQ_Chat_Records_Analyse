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
    # import matplotlib.pyplot as plt
    #
    # x = [1, 2, 3, 4, 5]
    # y1 = [6, 7, 8, 9, 10]
    # plt.plot(x, y1, marker='*', ms=10, color='y')
    # plt.show()
    # import matplotlib.pyplot as plt
    #
    # aaa = {'1209101643': 0.5427812816478225, '745500530': 0.5507599248949117, '1051617442':
    #     0.5530599685557689, '1045048548': 0.5499328897910526, '2642574488': 0.5446383498406289, '402376637':
    #            0.5407447368409908, '1764011453': 0.5369646476046138, '1251680944': 0.5354333781521334, '1219398106':
    #            0.5364054328018658, '599292912': 0.5364656951947343, '1913409863': 0.53484067081695, '309031584':
    #            0.5344930942030883, '545184326': 0.5341362432855117, '1329636023': 0.53325216105234, '710258421':
    #            0.5330333058797951, '673853621': 0.5326860825299103, '754315527': 0.5321570979667783, '1965083476':
    #            0.5316905993321258, '1141569440': 0.5316969969482886, '2275444386': 0.5306393358854631,
    #        'loyalnovakshayne@qq.com': 0.5310336921617058, '1115133277': 0.5309162264601218, '1715474300':
    #            0.5309849111992685, '122780300': 0.5309933866294124, '10000': 0.5284466697252308}
    # x = []
    # y = []
    # for k, v in aaa.items():
    #     print(v)
    #     x.append(k)
    #     y.append(v)
    # # 解决中文乱码问题
    # plt.rcParams['font.sans-serif'] = ['simHei']
    # plt.rcParams['axes.unicode_minus'] = False
    # plt.title('重庆老乡群群友情感指数')
    # plt.ylim(0, 1)  # 设置y轴范围9
    # plt.ylabel('情感指数')  # 设置y轴标签
    # plt.xlabel('用户')  # 设置x轴标签
    # plt.bar(x=x, height=y, color='rgbycmk')
    # plt.xticks(range(25), x, rotation=90, fontsize=6)
    # plt.legend()
    # plt.show()
