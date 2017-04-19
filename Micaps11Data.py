# -*- coding: utf-8 -*-
#     Micaps第11类数据 继承Micaps基类
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-11
#     Copyright:  ©江西省气象台 2017
#     Version:    2.0.20170411

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
                        self.Z[j, i] = math.sqrt(self.U[j, i] ** 2 + self.V[j, i] ** 2)
            if self.deltalat < 0:
                self.TransposeYaxis()

        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(self.filename, err, datetime.now()))

    def TransposeYaxis(self):
        self.beginlat, self.endlat = self.endlat, self.beginlat
        self.deltalat = math.fabs(self.deltalat)
        self.y = np.arange(self.beginlat, self.endlat + self.deltalat, self.deltalat)
        self.X, self.Y = np.meshgrid(self.x, self.y)
        self.U = self.U[::-1, ::]
        self.V = self.V[::-1, ::]
        self.Z = self.Z[::-1, ::]

    def UpdateData(self, products, micapsfile):
        self.UpdateExtents(products)
        # micapsfile = products.micapsfiles[0]
        self.min = self.Z.min()
        self.max = self.Z.max()
        self.distance = micapsfile.contour.step
        self.min = math.floor(self.min / self.distance) * self.distance
        self.max = math.ceil(self.max / self.distance) * self.distance

        # 如果自定义了legend的最小、最大和步长值 则用自定义的值更新
        self.UpdatePinLegendValue(micapsfile)

        from Main import equal
        if micapsfile.uv.onspeed and not equal(self.Z.max(), 0):
            self.linewidth = 5 * self.Z / self.Z.max()
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

    def GetPatches(self, paths):
        ps = []
        for path in paths:
            from matplotlib import patches
            ps.append(patches.PathPatch(path, linewidth=1, facecolor='none', edgecolor='k'))
        return ps

    def ConvertPacth(self, ax, patch):
        path = patch.get_path()
        lon = []
        lat = []
        for points in path.vertices:
            x, y = points[0], points[1]
            xy_pixels = ax.transData.transform(np.vstack([x, y]).T)
            xpix, ypix = xy_pixels.T
            lon.append(xpix[0])
            lat.append(ypix[0])
        from matplotlib.path import Path
        apath = Path(zip(lon, lat))
        from matplotlib import patches
        apatch = patches.PathPatch(apath,
                                   linewidth=1,
                                   facecolor='none',
                                   edgecolor='k')
        plt.gca().add_patch(apatch)
        return apatch

    def DrawUV(self, fig, m, micapsfile, clipborder, patch):

        if m is plt:
            if self.stream:
                plot = m.streamplot(self.X, self.Y, self.U, self.V,
                                    density=self.density,
                                    linewidth=self.linewidth,
                                    color=self.color,
                                    cmap=self.cmap
                                    )
            if self.barbs:
                barbs = m.barbs(self.X, self.Y, self.U, self.V,
                                length=self.length, barb_increments=dict(half=2, full=4, flag=20),
                                sizes=dict(emptybarb=0))
                pass

        else:
            # transform vectors to projection grid.
            uproj, vproj, xx, yy = \
                m.transform_vector(self.U, self.V, self.x, self.y, 31, 31,
                                   returnxy=True, masked=True)

            if isinstance(self.color, np.ndarray):
                self.color = self.colorlist

            if self.stream:
                # plot = m.streamplot(xx, yy, uproj, vproj  # , latlon=True
                #                     # density=self.density,
                #                     # linewidth=self.linewidth,
                #                     # color=self.color
                #                     # cmap=self.cmap
                #                     )
                # now plot.
                Q = m.quiver(xx, yy, uproj, vproj, color=self.color, scale=self.scale)
                # make quiver key.
                speed = micapsfile.uv.markscalelength
                qk = plt.quiverkey(Q, 0.1, 0.1, speed, '%.0f m/s' % speed, labelpos='W')
            if self.barbs:
                barbs = m.barbs(xx, yy, uproj, vproj, length=self.length,
                                barb_increments=dict(half=2, full=4, flag=20),
                                sizes=dict(emptybarb=0),
                                barbcolor='k', flagcolor='r',
                                linewidth=0.5)

        if m is plt and self.stream:
            if clipborder.path is not None and clipborder.using:
                for ax in fig.axes:
                    from matplotlib.patches import FancyArrowPatch
                    artists = ax.get_children()
                    for artist in artists:
                        if isinstance(artist, FancyArrowPatch):
                            artist.set_clip_path(patch)
                plot.lines.set_clip_path(patch)

        if self.barbs or (m is not plt and self.stream):
            if clipborder.path is not None and clipborder.using:
                for ax in fig.axes:
                    artists = ax.get_children()
                    for artist in artists:
                        from matplotlib.collections import PolyCollection
                        if isinstance(artist, PolyCollection):
                            artist.set_clip_path(patch)
