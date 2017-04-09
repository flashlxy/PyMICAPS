# -*- coding: utf-8 -*-
#
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170409
from __future__ import print_function

from datetime import datetime

from matplotlib.path import Path

import maskout
from Projection import Projection


class ClipBorder:
    """
    标题描述类
    """

    def __init__(self, leaf):

        filehead = Projection.leaf_to_string(leaf, "File")
        filetype = Projection.leaf_to_string(leaf, "Type", 'shp')
        code = Projection.leaf_to_list(leaf, "Code", [360000])
        drawswitch = str.upper(Projection.leaf_to_string(leaf, "Draw", 'off'))
        self.path = self.getPath(filehead=filehead, code=code, filetype=filetype)
        self.draw = str.upper(Projection.leaf_to_string(leaf, "Draw", 'off'))
        self.using = Projection.leaf_to_bool(leaf, "Using", True)
        self.linewidth = Projection.leaf_to_float(leaf, "LineWidth", 1)
        self.linecolor = Projection.leaf_to_string(leaf, "LineColor", 'k') if drawswitch == 'ON' else 'none'

    @staticmethod
    def getPath(filehead, code, filetype):
        """
        根据文件类型获取path对象
        :param filehead: 文件名
        :param code: 闭合区域行政区号-对shp文件有效
        :param filetype: 文件类型
        :return: path对象的一个实例
        """
        if filetype == 'shp':
            path = maskout.getPathFromShp(filehead, code)
        else:
            path = ClipBorder.readPath(filehead)
        return path

    @staticmethod
    def readPath(filename):
        """
        从类似第9类micaps数据中获取path
        :param filename: 数据文件全名
        :return: path对象的一个实例
        """
        try:
            file_object = open(filename)
            all_the_text = file_object.read()
            file_object.close()
            poses = all_the_text.split()
            lon = [float(p) for p in poses[13::2]]
            lat = [float(p) for p in poses[14::2]]
            path = Path(zip(lon, lat))
            return path
        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(filename, err, datetime.now()))
            return None
