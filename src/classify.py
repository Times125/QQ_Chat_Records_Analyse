#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author:lichunhui
@Time:  2018/1/17 20:19
@Description: 
"""
# ! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author:lichunhui
@Time:  2018/1/17 20:19
@Description: 
"""
import jieba
import os
import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.externals import joblib
from gensim.models.word2vec import Word2Vec
from sklearn.model_selection import train_test_split


class SVMClassifer:
    @classmethod
    def load_file(cls):
        # neg = pd.read_excel('data/neg.xls', header=None, index=None)
        # pos = pd.read_excel('data/pos.xls', header=None, index=None)
        #
        # cw = lambda x: list(jieba.cut(x))
        # pos['words'] = pos[0].apply(cw)
        # neg['words'] = neg[0].apply(cw)
        #
        # # use 1 for positive sentiment, 0 for negative
        # y = np.concatenate((np.ones(len(pos)), np.zeros(len(neg))))
        # x_train, x_test, y_train, y_test = train_test_split(
        #     np.concatenate((pos['words'], neg['words'])), y, test_size=0.2)
        # np.save('svm_data/y_train.npy', y_train)
        # np.save('svm_data/y_test.npy', y_test)

        import os

        with open(os.path.dirname(__file__) + '/../dataset/pos.txt', 'r') as f:
            conts = f.readlines()
            pos_res = list()
            for cont in conts:
                pos_res.append(list(jieba.cut(cont)))

        with open(os.path.dirname(__file__) + '/../dataset/neg.txt', 'r') as f:
            conts = f.readlines()
            neg_res = list()
            for cont in conts:
                neg_res.append(list(jieba.cut(cont)))

        y = np.concatenate((np.ones(len(pos_res)), np.zeros(len(neg_res))))
        x_train, x_test, y_train, y_test = train_test_split(
            np.concatenate((pos_res, neg_res)), y, test_size=0.2)
        np.save('svm_data/y_train.npy', y_train)
        np.save('svm_data/y_test.npy', y_test)

        return x_train, x_test

    @classmethod
    # 对每个句子的所有词向量取均值
    def build_wordvector(cls, text, size, imdb_w2v):
        vec = np.zeros(size).reshape((1, size))
        count = 0.
        for word in text:
            try:
                vec += imdb_w2v[word].reshape((1, size))
                count += 1.
            except KeyError:
                continue
        if count != 0:
            vec /= count
        return vec

    # 计算词向量
    @classmethod
    def save_train_vecs(cls, x_train, x_test):
        n_dim = 300
        # Initialize model and build vocab
        imdb_w2v = Word2Vec(size=n_dim, min_count=10)
        imdb_w2v.build_vocab(x_train)

        # Train the model over train_reviews (this may take several minutes)
        imdb_w2v.train(x_train, total_examples=imdb_w2v.corpus_count, epochs=imdb_w2v.iter)
        train_vecs = np.concatenate([cls.build_wordvector(z, n_dim, imdb_w2v) for z in x_train])
        # train_vecs = scale(train_vecs)

        np.save('svm_data/train_vecs.npy', train_vecs)

        # Train word2vec on test tweets
        imdb_w2v.train(x_test, total_examples=imdb_w2v.corpus_count, epochs=imdb_w2v.iter)
        imdb_w2v.save('svm_data/w2v_model/w2v_model.pkl')
        # Build test tweet vectors then scale
        test_vecs = np.concatenate([cls.build_wordvector(z, n_dim, imdb_w2v) for z in x_test])
        # test_vecs = scale(test_vecs)
        np.save('svm_data/test_vecs.npy', test_vecs)

    @classmethod
    def get_data(cls):
        train_vecs = np.load('svm_data/train_vecs.npy')
        y_train = np.load('svm_data/y_train.npy')
        test_vecs = np.load('svm_data/test_vecs.npy')
        y_test = np.load('svm_data/y_test.npy')
        return train_vecs, y_train, test_vecs, y_test

    # 训练svm模型
    @classmethod
    def train(cls):
        x_train, x_test = cls.load_file()
        cls.save_train_vecs(x_train, x_test)
        train_vecs, y_train, test_vecs, y_test = cls.get_data()
        clf = SVC(kernel='rbf', verbose=True)
        clf.fit(train_vecs, y_train)
        joblib.dump(clf, )
        print(clf.score(test_vecs, y_test))

    # 得到待预测单个句子的词向量
    @classmethod
    def get_predict_vecs(cls, words):
        n_dim = 300
        imdb_w2v = Word2Vec.load('svm_data/w2v_model/w2v_model.pkl')
        # imdb_w2v.train(words)
        train_vecs = cls.build_wordvector(words, n_dim, imdb_w2v)
        # print train_vecs.shape
        return train_vecs

    # 对单个句子进行情感判断
    @classmethod
    def predict(cls, string):
        words = jieba.lcut(string)
        words_vecs = cls.get_predict_vecs(words)
        clf = joblib.load('svm_data/svm_model/model.pkl')
        result = clf.predict(words_vecs)
        return result[0]
