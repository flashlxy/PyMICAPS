# -*- coding: utf-8 -*-
#     Micaps第11类数据 继承Micaps基类
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170406

import codecs
import math
import re
import nclcmaps
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from MicapsData import Micaps


class Micaps11Data(Micaps):
    def __init__(self, filename):
        self.filename = filename
        self.U = None
        self.V = None
        self.linewidth = 1
        self.color = 'k'
        self.density = [1, 1]
        self.cmap = None
        self.stream = None
        self.barbs = None
        self.length = 5
        self.scale = 700
        self.colorlist = ['k', 'b', 'r', 'g']
        self.ReadFromFile()

    def ReadFromFile(self):
        """
        读micaps第11类数据文件到内存
        :return: 
        """
        try:
            begin = 17
            file_object = codecs.open(self.filename, mode='r', encoding='GBK')
            all_the_text = file_object.read().strip()
            file_object.close()
            contents = re.split('[\s]+', all_the_text)
            if len(contents) < begin:
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

            self.x = np.arange(self.beginlon, self.endlon + self.deltalon, self.deltalon)
            self.y = np.arange(self.beginlat, self.endlat + self.deltalat, self.deltalat)
            self.X, self.Y = np.meshgrid(self.x, self.y)

            if self.dataflag == 'diamond' and self.style == '11':
                self.U = np.zeros((self.sumlat, self.sumlon))
                self.V = np.zeros((self.sumlat, self.sumlon))
                self.Z = np.zeros((self.sumlat, self.sumlon))

                for i in range(self.sumlon):
                    for j in range(self.sumlat):
                        self.U[j, i] = float(contents[begin + j * self.sumlon + i])

                vbegin = begin + self.sumlat * self.sumlon
                for i in range(self.sumlon):
                    for j in range(self.sumlat):
                        self.V[j, i] = float(contents[vbegin + j * self.sumlon + i])

                for i in range(self.sumlon):
                    for j in range(self.sumlat):
                        self.Z[j, i] = math.sqrt(self.U[j, i]**2 + self.V[j, i]**2)

        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(self.filename, err, datetime.now()))

    def UpdateData(self, products):
        self.UpdateExtents(products)
        micapsfile = products.micapsfiles[0]
        self.min = self.Z.min()
        self.max = self.Z.max()
        self.distance = micapsfile.contour.step
        self.min = math.floor(self.min / self.distance) * self.distance
        self.max = math.ceil(self.max / self.distance) * self.distance
        from Main import equal
        if micapsfile.uv.onspeed and not equal(self.Z.max(), 0):
            self.linewidth = 5*self.Z/self.Z.max()
        else:
            self.linewidth = micapsfile.uv.linewidth
        self.density = micapsfile.uv.density

        if micapsfile.uv.oncolor:
            self.color = self.Z
            self.cmap = nclcmaps.cmaps(micapsfile.legend.micapslegendcolor)
        else:
            self.color = micapsfile.uv.color

        self.barbs = micapsfile.uv.barbs
        self.stream = micapsfile.uv.stream
        self.length = micapsfile.uv.length
        self.scale = micapsfile.uv.scale
        self.colorlist = micapsfile.legend.legendcolor

    def DrawUV(self, m, products):

        if m is plt:
            if self.stream:
                m.streamplot(self.X, self.Y, self.U, self.V,
                             density=self.density,
                             linewidth=self.linewidth,
                             color=self.color,
                             cmap=self.cmap
                             )

            if self.barbs:
                m.barbs(self.X, self.Y, self.U, self.V,
                        length=self.length, barb_increments=dict(half=2, full=4, flag=20),
                        sizes=dict(emptybarb=0))

        else:
            if self.stream:
                # transform vectors to projection grid.
                uproj, vproj, xx, yy = \
                    m.transform_vector(self.U, self.V, self.x, self.y, 31, 31,
                                       returnxy=True, masked=True)

                if isinstance(self.color, np.ndarray):
                    self.color = self.colorlist
                # now plot.
                Q = m.quiver(xx, yy, uproj, vproj, color=self.color, scale=self.scale)
                # make quiver key.
                qk = plt.quiverkey(Q, 0.1, 0.1, 20, '20 m/s', labelpos='W')

            if self.barbs:

                barbs = m.barbs(xx, yy, uproj, vproj, length=self.length,
                                barb_increments=dict(half=2, full=4, flag=20),
                                sizes=dict(emptybarb=0),
                                barbcolor='k', flagcolor='r',
                                linewidth=0.5)
        #  plt.colorbar(strm.lines)
