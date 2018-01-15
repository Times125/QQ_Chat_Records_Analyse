#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author:lichunhui
@Time:  2018/1/15 0:27
@Description: 
"""
import redis


class MyRedis(object):
    def __init__(self):
        pass

    @staticmethod
    def get_redis_instance():
        pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
        rdis = redis.Redis(connection_pool=pool)
        return rdis
