# -*- coding: utf-8 -*-
#
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-11
#     Copyright:  ©江西省气象台 2017
#     Version:    2.0.20170411

import sys
import math
from itertools import takewhile
import time as ttime
from FnTime import fn_timer


def parseInt(s):
    """
    全局函数 字符串转整数
    :param s: 字符串
    :return: 整数
    """
    assert isinstance(s, str)
    return int(''.join(list(takewhile(lambda x: x.isdigit(), s)))) if s[0].isdigit() else None


def equal(value1, value2):
    return math.fabs(value1 - value2) < 10e-5

@fn_timer
def main(debug):
    """
    主程序
    :param debug: 
    :return: 
    """
    if debug:
        xml = r'config.xml'
    else:
        if len(sys.argv) < 2:
            print(u'参数不够，至少需要一个xml文件名参数')
            sys.exit()
        xml = sys.argv[1]


    from Products import Products
    products = Products(xml)
    if products is not None:
        for micapsfile in products.micapsfiles:
            micapsfile.file.micapsdata.Draw(products, micapsfile, debug)
            # break


if __name__ == '__main__':
    ISDEBUG = True
    main(ISDEBUG)
