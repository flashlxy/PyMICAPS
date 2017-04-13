# -*- coding: utf-8 -*-
#     Micaps第4类数据 继承Micaps基类
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-11
#     Copyright:  ©江西省气象台 2017
#     Version:    2.0.20170411

import codecs
import numpy as np
import re

from datetime import datetime
from MicapsData import Micaps


class Micaps4Data(Micaps):
    def __init__(self, filename):
        self.filename = filename
        self.ReadFromFile()

    def ReadFromFile(self):
        """
        读micaps第4类数据文件到内存
        :return: 
        """
        try:
            file_object = codecs.open(self.filename, mode='r', encoding='GBK')
            all_the_text = file_object.read().strip()
            file_object.close()
            contents = re.split('[\s]+', all_the_text)
            if len(contents) < 23:
                return
            self.dataflag = contents[0].strip()
            self.style = contents[1].strip()
            self.title = contents[2].strip()
            self.yy = int(contents[3].strip())
            self.mm = int(contents[4].strip())
            self.dd = int(contents[5].strip())
            self.hh = int(contents[6].strip())
            self.forehh = int(contents[7].strip())
            self.level = contents[8].strip()

            self.deltalon = float(contents[9].strip())
            self.deltalat = float(contents[10].strip())
            self.beginlon = float(contents[11].strip())
            self.endlon = float(contents[12].strip())
            self.beginlat = float(contents[13].strip())
            self.endlat = float(contents[14].strip())

            self.sumlon = int(contents[15].strip())
            self.sumlat = int(contents[16].strip())
            self.distance = float(contents[17].strip())
            self.min = float(contents[18].strip())
            self.max = float(contents[19].strip())
            self.def1 = contents[20].strip()
            self.def2 = contents[21].strip()

            x = np.arange(self.beginlon, self.endlon + self.deltalon, self.deltalon)
            y = np.arange(self.beginlat, self.endlat + self.deltalat, self.deltalat)
            self.X, self.Y = np.meshgrid(x, y)

            if self.dataflag == 'diamond' and self.style == '4':
                begin = 22
                self.Z = np.zeros((self.sumlat, self.sumlon))

                for i in range(self.sumlon):
                    for j in range(self.sumlat):
                        self.Z[j, i] = float(contents[begin + j * self.sumlon + i])

        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(self.filename, err, datetime.now()))

    def UpdateData(self, products, micapsfile):
        self.UpdateExtents(products)
        # 如果自定义了legend的最小、最大和步长值 则用自定义的值更新
        self.UpdatePinLegendValue(micapsfile)

    @staticmethod
    def Write(filename, fdate, edate, flon, elon, flat, elat, xjj, yjj, nx, ny, zi):
        """
        把数据写入 micaps 第四类数据文件
        :param filename: 写入文件
        :param fdate: 起始日期
        :param edate: 结束日期
        :param flon: 起始经度
        :param elon: 结束经度
        :param flat: 起始纬度
        :param elat: 结束纬度
        :param xjj: 经度方向的步长
        :param yjj: 纬度方向的步长
        :param nx: 经度方向上的点数
        :param ny: 纬度方向上的点数
        :param zi: z值数组
        :return: 
        """
        content = 'diamond 4 ' + fdate + '-' + edate + '客观分析网格雨量 '
        content += fdate[0:4] + ' ' + fdate[4:6] + ' ' + fdate[6:8] + ' ' + fdate[8:10] + ' 000 999 '
        content += ' '.join([xjj, yjj, flon, elon, flat, elat, nx, ny, '10.0', '0', str(zi.max()), '0', '0']) + '\n'
        for a in zi.tolist():
            content += ' '.join([Micaps4Data.FToS(b) for b in a]) + '\n'
        fp = open(filename, 'w')
        fp.write(content)
        fp.close()

    @staticmethod
    def FToS(lat):
        """
        实数转字符串
        :param lat: 实数
        :return: 转换后的字符串
        """
        if lat is None:
            s = '0'
        else:
            s = '%.2f' % lat
        return s
