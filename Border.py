# -*- coding: utf-8 -*-
#
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170409
from __future__ import print_function
import re
from datetime import datetime
from matplotlib.path import Path
from ClipBorder import ClipBorder
from Projection import Projection


class Border:
    """
    标题描述类
    """

    def __init__(self, leaf):
        self.file = Projection.leaf_to_string(leaf, "File")
        self.filetype = str.upper(Projection.leaf_to_string(leaf, "Type", "shp"))
        self.draw = Projection.leaf_to_bool(leaf, "Draw", False)
        self.encoding = Projection.leaf_to_string(leaf, "Encoding", "utf-8")
        self.path = (
            ClipBorder.readPath(self.file, 0) if self.filetype != "SHP" else None
        )
        self.polygon = str.upper(Projection.leaf_to_string(leaf, "Polygon", "on"))
        # self.draw = Projection.leaf_to_bool(leaf, "Draw", False)
        self.linewidth = Projection.leaf_to_float(leaf, "LineWidth", 1)
        self.linecolor = Projection.leaf_to_string(leaf, "LineColor", "k")

    @staticmethod
    def readPolygon(filename):
        """
        从特定格式的文件中获取path
        :param filename: 特定的数据文件全名
        :return: path对象的一个实例
        """
        try:
            file_object = open(filename)
            all_the_text = file_object.read().strip()
            file_object.close()
            poses = re.split(r"[,]+|[\s]+", all_the_text)
            lon = [float(p) for p in poses[0::2]]
            lat = [float(p) for p in poses[1::2]]
            path = Path(zip(lon, lat))
            return path
        except Exception as err:
            print("【{0}】{1}-{2}".format(filename, err, datetime.now()))
            return None
