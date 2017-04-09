# -*- coding: utf-8 -*-
#     产品参数类 关联模块Main，maskout和类Micaps3Data，Micaps4Data，Projection, HeadDesc
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170406
import os
import re
from datetime import datetime
from xml.etree import ElementTree

from matplotlib.path import Path

import maskout
from Map import Map
from MicapsFile import MicapsFile
from Picture import Picture


class Products:
    """
    画图参数的封装类
    用法：

    """

    def __init__(self, xmlfile):
        self.xmlfile = xmlfile
        if not os.path.exists(self.xmlfile):
            return
        try:
            tree = ElementTree.parse(self.xmlfile)
            p = tree.getroot()

            # 地图
            self.map = Map(p)

            # Get the micaps files list

            self.micapsfiles = []

            micapsfiles = p.find("MicapsFiles").getchildren()

            for micapsfile in micapsfiles:
                self.micapsfiles.append(MicapsFile(micapsfile))

            # get picture para class
            self.picture = Picture(p, self.map.clipborders)

        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(self.xmlfile, err, datetime.now()))
            return None

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
            path = Products.readPath(filehead)
        return path

    @staticmethod
    def checkFilename(filepath):
        """
        创建数据文件夹
        :param filepath: 文件路径
        :return: 
        """

        path = os.path.dirname(filepath)
        if not os.path.isdir(path):
            os.makedirs(path)

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

    @staticmethod
    def readPolygon(filename):
        """
        从特定格式的文件中获取path
        :param filename: 特定的数据文件全名
        :return: path对象的一个实例
        """
        try:
            file_object = open(filename)
            all_the_text = file_object.read()
            file_object.close()
            poses = re.split('[,]+|[\s]+', all_the_text)
            lon = [float(p) for p in poses[0::2]]
            lat = [float(p) for p in poses[1::2]]
            path = Path(zip(lon, lat))
            return path
        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(filename, err, datetime.now()))
            return None
