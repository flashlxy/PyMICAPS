# -*- coding: utf-8 -*-
#     Micaps第3类数据 继承Micaps基类
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170406

import codecs
import itertools
import math
import operator
import re
import numpy as np
import PolygonEx
from datetime import datetime
from MicapsData import Micaps, griddata


class Micaps3Data(Micaps):
    def __init__(self, filename):
        self.filename = filename
        self.contoursum = None
        self.smoothindex = None
        self.boldvalue = None
        self.pointsincutborder = None
        self.elementsum = 1
        self.stationsum = None
        self.data = []
        # self.ReadFromFile()
        self.defaultvalue = 9999.
        self.ReadFromFile()

    @staticmethod
    def EqualValue(value1, value2):
        return math.fabs(value1 - value2) < 10e-5

    def EqualDefaultValue(self, value):
        return Micaps3Data.EqualValue(self.defaultvalue, value)

    def valid(self, lon, lat, zvalue):
        if self.EqualValue(lon, 0) or self.EqualValue(lon, self.defaultvalue):
            return False
        if self.EqualValue(lat, 0) or self.EqualValue(lat, self.defaultvalue):
            return False
        if self.EqualValue(zvalue, self.defaultvalue):
            return False
        return True

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
            if len(contents) < 14:
                return
            self.dataflag = contents[0].strip()
            self.style = contents[1].strip()
            self.title = contents[2].strip()
            self.yy = int(contents[3].strip())
            self.mm = int(contents[4].strip())
            self.dd = int(contents[5].strip())
            self.hh = int(contents[6].strip())
            self.level = contents[7].strip()

            self.contoursum = int(contents[8].strip())
            self.smoothindex = float(contents[9].strip())
            self.boldvalue = float(contents[10].strip())
            self.pointsincutborder = int(contents[11].strip())

            self.elementsum = int(contents[12].strip())
            self.stationsum = int(contents[13].strip())

            self.x = []
            self.y = []
            self.z = []

            self.stationsum = (len(contents) - 14) / 5
            stations = []
            if self.dataflag == 'diamond' and self.style == '3':
                begin = 14
                for i in range(self.stationsum):
                    code = contents[begin + 5 * i + 0].strip()
                    lon = float(contents[begin + 5 * i + 1].strip())
                    lat = float(contents[begin + 5 * i + 2].strip())
                    height = float(contents[begin + 5 * i + 3].strip())
                    zvalue = float(contents[begin + 5 * i + 4].strip())
                    if self.valid(lon, lat, zvalue):
                        stations.append({'code': code, 'lon': lon, 'lat': lat, 'height': height, 'zvalue': zvalue})

            if len(stations) > 0:
                self.CheckData(stations)

            for ele in stations:
                # code = ele['code']
                lon = ele['lon']
                lat = ele['lat']
                # height = ele['height']
                zvalue = ele['zvalue']
                self.x.append(lon)
                self.y.append(lat)
                self.z.append(zvalue)

            self.beginlon = min(self.x)
            self.endlon = max(self.x)
            self.beginlat = min(self.y)
            self.endlat = max(self.y)
            # self.data.append((code, lon, lat, height, zvalue))

        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(self.filename, err, datetime.now()))

    @staticmethod
    def AddPoints(x, y, z, path):
        # 增加轮廓外围插值点
        ext_polygon = PolygonEx.PolygonEx(x, y, z, 1.0, path)
        control_point = ext_polygon.get_extend_hull()
        for point in control_point:
            x.append(point[0])
            y.append(point[1])
            z.append(point[2])

    def CreateArray(self):
        self.data = np.array(self.data, dtype=[
            ('code', np.int32),
            ('lon', np.float32),
            ('lat', np.float32),
            ('height', np.float32),
            ('zvalue', np.float32)]
                             )

    def UpdateData(self, products):
        self.UpdateExtents(products)

        xmax = products.extents.xmax
        xmin = products.extents.xmin
        ymax = products.extents.ymax
        ymin = products.extents.ymin

        path = products.cutborders[0]['path']

        if path is not None:
            self.AddPoints(self.x, self.y, self.z, path)

        # self.CreateArray()

        self.X = np.linspace(xmin, xmax, products.grid[0])
        self.Y = np.linspace(ymin, ymax, products.grid[1])
        # x = self.data['lon']
        # y = self.data['lat']
        # z = self.data['zvalue']
        self.Z = griddata(self.x, self.y, self.z, self.X, self.Y, 'nn')
        self.X, self.Y = np.meshgrid(self.X, self.Y)

        self.min = min(self.z)
        self.max = max(self.z)
        self.distance = products.step
        self.min = math.floor(self.min / self.distance) * self.distance
        self.max = math.ceil(self.max / self.distance) * self.distance

    @staticmethod
    def CheckData(data):
        # 根据经纬度去重
        getvals = operator.itemgetter('lon', 'lat')
        data.sort(key=getvals)
        result = []
        for k, g in itertools.groupby(data, getvals):
            result.append(g.next())
        data[:] = result
