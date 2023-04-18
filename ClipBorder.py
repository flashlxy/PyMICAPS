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
    边界裁切类
    """

    def __init__(self, leaf):
        start_pos = 0
        filehead = Projection.leaf_to_string(leaf, "File")
        filetype = Projection.leaf_to_string(leaf, "Type", "shp")
        code = Projection.leaf_to_list(leaf, "Code", [360000])
        drawswitch = str.upper(Projection.leaf_to_string(leaf, "Draw", "off"))
        self.encoding = Projection.leaf_to_string(leaf, "Encoding", "utf-8")
        self.path = self.getPath(
            filehead=filehead,
            code=code,
            filetype=filetype,
            start_pos=start_pos,
            encoding=self.encoding,
        )
        self.draw = str.upper(Projection.leaf_to_string(leaf, "Draw", "off"))
        self.using = Projection.leaf_to_bool(leaf, "Using", True)
        self.linewidth = Projection.leaf_to_float(leaf, "LineWidth", 1)
        self.linecolor = (
            Projection.leaf_to_string(leaf, "LineColor", "k")
            if drawswitch == "ON"
            else "none"
        )

    @staticmethod
    def getPath(filehead, code, filetype, start_pos, encoding=None):
        """
        根据文件类型获取path对象
        :param start_pos: 正文开始的位置，对txt文件有效
        :param filehead: 文件名
        :param code: 闭合区域行政区号-对shp文件有效
        :param filetype: 文件类型
        :return: path对象的一个实例
        """
        if encoding is None:
            encoding = "utf-8"
        if filetype == "shp":
            path = maskout.getPathFromShp(filehead, code, encoding=encoding)
        else:
            path = ClipBorder.readPath(filehead, start_pos)
        return path

    @staticmethod
    def readPath(filename, start_pos=13):
        """
        从类似第9类micaps数据中获取path
        :param start_pos:
        :param filename: 数据文件全名
        :return: path对象的一个实例
        """
        try:
            file_object = open(filename)
            all_the_text = file_object.read()
            file_object.close()
            poses = all_the_text.strip().split()
            lon = [float(p) for p in poses[start_pos::2]]
            lat = [float(p) for p in poses[start_pos + 1 :: 2]]
            path = Path(zip(lon, lat))
            return path
        except Exception as err:
            print("【{0}】{1}-{2}".format(filename, err, datetime.now()))
            return None
