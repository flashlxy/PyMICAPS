# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     FnTime
   Description :
   Author :        Xianyao Liu
   date：          2019/3/16
-------------------------------------------------
   Change Activity:
                   2019/3/16
-------------------------------------------------
"""
import time
from functools import wraps

__author__ = 'Xianyao Liu'


def fn_timer(func):
    @wraps(func)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        t1 = time.time()
        # print("Total time running %s: %s seconds" % (func.__name__, str(t1 - t0)))
        print("Total time running %s: %s seconds" % (func.__name__, str(t1 - t0)))
        return result

    return function_timer
