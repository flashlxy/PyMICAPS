# -*- coding: utf-8 -*-
#     Micaps第17类数据 继承Micaps基类
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-14
#     Copyright:  ©江西省气象台 2017
#     Version:    2.0.20170414
from __future__ import print_function
import codecs
import re
from datetime import datetime

import math

from MicapsData import Micaps, np


class Micaps17Data(Micaps):
    def __init__(self, filename):
        self.filename = filename
        self.stationsum = None
        self.stations = []
        self.ReadFromFile()

    def ReadFromFile(self):
        """
        读micaps第3类数据文件到内存
        :return: 
        """
        try:
            file_object = codecs.open(self.filename, mode='r', encoding='GBK')
            all_the_text = file_object.read().strip()
            file_object.close()
            contents = re.split('[\s]+', all_the_text)
            if len(contents) < 4:
                return
            self.dataflag = contents[0].strip()
            self.style = contents[1].strip()
            self.title = contents[2].strip()
            self.stationsum = int(contents[3].strip())

            if self.dataflag == 'diamond' and self.style == '17':
                begin = 4
                step = 0
                for i in range(self.stationsum):
                    k = step + begin + 7 * i
                    code = contents[k + 0].strip()
                    lat = self.ChangeLL(contents[k + 1].strip())
                    lon = self.ChangeLL(contents[k + 2].strip())
                    height = float(contents[k + 3].strip())
                    iclass = int(contents[k + 4].strip())
                    infosum = int(contents[k + 5].strip())
                    info = []
                    for j in range(infosum):
                        info.append(contents[k + 6 + j].strip())
                    step += infosum - 1
                    # self.stations.append(
                    #     {'code': code, 'lon': lon, 'lat': lat, 'height': height,
                    #      'iclass': iclass, 'infosum': infosum, 'name': info[0]
                    #      }
                    # )
                    self.stations.append(
                        [code, lat, lon, height, iclass, infosum, info[0]]
                    )
        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(self.filename, err, datetime.now()))

    @staticmethod
    def ChangeLL(lonlat):
        if '.' in lonlat:
            return float(lonlat)
        else:
            just = math.floor(float(lonlat)/100)
            return just + (float(lonlat)/100 - just)*100/60.
