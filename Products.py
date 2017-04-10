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
