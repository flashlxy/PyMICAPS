# -*- coding: utf-8 -*-
#     MicapsData基类
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170406
from __future__ import print_function
from __future__ import print_function

import sys

import shapefile

reload(sys)
sys.setdefaultencoding('utf-8')

# matplotlib.use('Agg')
from matplotlib.font_manager import FontProperties
from pylab import *
from matplotlib._png import read_png
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.ticker import FormatStrFormatter
from matplotlib.transforms import Bbox
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import os
from datetime import datetime
from matplotlib import patches
from matplotlib.path import Path
import numpy as np
import matplotlib.pyplot as plt
import nclcmaps


class Micaps:
    def __init__(self, filename):
        self.filename = filename
        self.dataflag = None
        self.style = None
        self.title = None
        self.yy = None
        self.mm = None
        self.dd = None
        self.hh = None
        self.forehh = None
        self.level = None
        self.deltalon = None
        self.deltalat = None
        self.beginlon = None
        self.endlon = None
        self.beginlat = None
        self.endlat = None
        self.beginlon = None
        self.endlon = None
        self.sumlon = None
        self.sumlat = None
        self.distance = None
        self.min = None
        self.max = None
        self.def1 = None
        self.def2 = None
        self.X = None
        self.Y = None
        self.Z = None
        self.outPath = os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def UpdatePath(path, projection):
        """
        根据投影对象更新path
        :param path: 路径对象
        :param projection: 投影类型
        :return: 
        """
        if path is None:
            return
        for point in path.vertices:
            point[0], point[1] = projection(point[0], point[1])

    @staticmethod
    def Update(products, projection):
        """
        根据投影类型和更新产品对象中的path对象
        :param products: 产品参数
        :param projection: 投影类型
        :return: 
        """
        Micaps.UpdatePath(products.cutborders[0]['path'], projection)
        for area in products.mapborders:
            Micaps.UpdatePath(area['path'], projection)

    @staticmethod
    def UpdateXY(projection, x, y):
        return projection(x, y)

    @staticmethod
    def DrawBorders(m, products):
        """
        画县市边界
        :param m: 画布对象（plt或投影后的plt)
        :param products: 产品参数
        :return: 
        """
        try:
            for area in products.mapborders:
                if not area['draw']:
                    continue
                if area['filetype'] == 'SHP':  # shp文件
                    if m is plt:
                        Micaps.DrawShapeFile(area)
                    else:
                        m.readshapefile(area['file'].replace('.shp', ''),
                                        os.path.basename(area['file']),
                                        color=area['linecolor'])
                else:  # 文本文件 , 画之前 路径中的点已经被投影了
                    if area['path'] is None:
                        continue
                    if area['polygon'] == 'ON':
                        area_patch = patches.PathPatch(area['path'], linewidth=area['linewidth'], linestyle='solid',
                                                       facecolor='none', edgecolor=area['linecolor'])
                        plt.gca().add_patch(area_patch)
                    else:
                        x, y = zip(*area['path'].vertices)
                        m.plot(x, y, 'k-', linewidth=area['linewidth'], color=area['linecolor'])
        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(products.xmlfile, err, datetime.datetime.now()))

    @staticmethod
    def DrawTitle(m, products, headtxt):
        if m is plt:
            if products.mtitleposition is None:
                for desc in products.descs:
                    fontfile = r"C:\WINDOWS\Fonts\{0}".format(desc.font['family'])
                    if not os.path.exists(fontfile):
                        font = FontProperties(size=desc.font['fontsize'], weight=desc.font['weight'])
                    else:
                        font = FontProperties(fname=fontfile, size=desc.font['fontsize'], weight=desc.font['weight'])
                    plt.text(desc.pos[0], desc.pos[1], desc.text,
                             # size=desc.font['fontsize'], weight=desc.font['weight'],
                             color=desc.font['color'],
                             fontdict=desc.font,
                             fontproperties=font,
                             rotation=0,
                             ha='left', va='top')
            else:
                if products.mtitleposition == [0, 0]:
                    plt.title(headtxt, fontdict={'fontsize': 14})
                else:
                    plt.text(products.mtitleposition[0], products.mtitleposition[1], headtxt,
                             size=14,
                             weight='bold',
                             # color='blue',
                             # fontdict=desc.font,
                             # fontproperties=font,
                             rotation=0,
                             ha='left', va='top')
        else:
            plt.title(headtxt)

    @staticmethod
    def DrawShapeFile(area):
        """
        在画布上绘制shp文件
        :param area: 包含shp文件名及线宽和线颜色的一个字典
        :return: 
        """
        try:
            shpfile = area['file']
            border_shape = shapefile.Reader(shpfile)
            border = border_shape.shapes()
            for b in border:
                border_points = b.points
                path_data = []
                count = 0
                for cell in border_points:
                    if count == 0:
                        trans = (Path.MOVETO, (cell[0], cell[1]))
                        path_data += [trans]
                        cell_end = cell
                    else:
                        trans = (Path.CURVE4, (cell[0], cell[1]))
                        path_data += [trans]
                trans = (Path.CLOSEPOLY, (cell_end[0], cell_end[1]))
                path_data += [trans]

                codes, verts = zip(*path_data)
                path = Path(verts, codes)
                x, y = zip(*path.vertices)
                plt.plot(x, y, 'k-', linewidth=area['linewidth'], color=area['linecolor'])
        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(area['file'], err, datetime.datetime.now()))

    def UpdateExtents(self, products):
        """
        更新产品参数的extents
        :param products: 产品参数对象
        :return: 
        """
        if products.extents is None:
            maxlon = max(self.endlon, self.beginlon)
            minlon = min(self.endlon, self.beginlon)
            maxlat = max(self.endlat, self.beginlat)
            minlat = min(self.endlat, self.beginlat)
            xmax = maxlon + products.margin if maxlon + products.margin <= 180 else 180
            xmin = minlon - products.margin if minlon - products.margin >= -180 else -180
            ymax = maxlat + products.margin if maxlat + products.margin <= 90 else 90
            ymin = minlat - products.margin if minlat - products.margin >= -90 else -90
            products.extents = Bbox.from_extents(xmin, ymin, xmax, ymax)

    def UpdateData(self, products):
        self.UpdateExtents(products)

    def Draw(self, products, debug=True):
        """
        根据产品参数绘制图像
        :param debug: 
        :param products: 
        :return: 产品参数
        """
        # 图例的延展类型
        origin = 'lower'
        if self.title.find(u'降水') >= 0 or self.title.find(u'雨'):
            extend = 'max'
        else:
            extend = 'neither'

        # 更新绘图矩形区域
        # self.UpdateExtents(products)
        self.UpdateData(products)
        xmax = products.extents.xmax
        xmin = products.extents.xmin
        ymax = products.extents.ymax
        ymin = products.extents.ymin

        # 设置绘图画板的宽和高 单位：英寸
        h = products.height
        if products.projection.name == 'sall':  # 等经纬度投影时不用配置本身的宽度，直接根据宽高比得到
            w = h * np.math.fabs((xmax - xmin) / (ymax - ymin)) * products.widthshrink
        else:
            w = products.width

        # 创建画布
        fig = plt.figure(figsize=(w, h), dpi=products.dpi, facecolor="white")  # 必须在前面
        # ax = fig.add_subplot(111)
        # 设置绘图区域
        plt.xlim(xmin, xmax)
        plt.ylim(ymin, ymax)

        # 背景透明
        fig.patch.set_alpha(products.opacity)

        # 坐标系统尽可能靠近绘图区边界
        fig.tight_layout(pad=products.pad)

        # 获得产品投影
        from Projection import Projection
        m = Projection.GetProjection(products)
        if m is not plt:
            # 用投影更新经纬度数据
            self.X, self.Y = Micaps.UpdateXY(m, self.X, self.Y)
            # 用投影更新产品参数中涉及经纬度的数据
            Micaps.Update(products, m)
            if products.projection.coastlines:
                m.drawcoastlines(linewidth=0.25)
            if products.projection.countries:
                m.drawcountries(linewidth=0.25)
            # draw parallels and meridians.
            if products.projection.axis == 'on':
                m.drawparallels(np.arange(-80., 81., 10.),
                                labels=products.projection.latlabels,
                                family='DejaVu Sans',
                                fontsize=10)
                m.drawmeridians(np.arange(-180., 181., 10.),
                                labels=products.projection.lonlabels,
                                family='DejaVu Sans',
                                fontsize=10)

            if products.projection.lsmask['visible']:
                m.drawlsmask(land_color=products.projection.lsmask['land_color'],
                             ocean_color=products.projection.lsmask['ocean_color'], resolution='l')

        else:
            # 坐标轴
            plt.axis(products.projection.axis)

            # 设置坐标轴刻度值显示格式
            if products.projection.axis == 'on':
                x_majorFormatter = FormatStrFormatter('%d°E')
                y_majorFormatter = FormatStrFormatter('%d°N')
                plt.gca().xaxis.set_major_formatter(x_majorFormatter)
                plt.gca().yaxis.set_major_formatter(y_majorFormatter)
                xaxis = plt.gca().xaxis
                for label in xaxis.get_ticklabels():
                    label.set_fontproperties('DejaVu Sans')
                    label.set_fontsize(10)
                yaxis = plt.gca().yaxis
                for label in yaxis.get_ticklabels():
                    label.set_fontproperties('DejaVu Sans')
                    label.set_fontsize(10)

        # 绘制裁切区域边界
        if products.cutborders[0]['path'] is not None:
            patch = patches.PathPatch(products.cutborders[0]['path'],
                                      linewidth=products.cutborders[0]['linewidth'],
                                      facecolor='none',
                                      edgecolor=products.cutborders[0]['linecolor'])
            plt.gca().add_patch(patch)
        else:
            patch = None

        # 绘制地图
        Micaps.DrawBorders(m, products)

        cmap = nclcmaps.cmaps(products.micapslegendcolor)  # cm.jet  temp_diff_18lev
        vmax = math.ceil(self.max)
        vmin = math.floor(self.min)
        levels = arange(vmin - self.distance, vmax + self.distance + 0.1, self.distance)

        if products.micapslegendvalue:
            level = levels
        else:
            level = products.legendvalue

        # 是否绘制等值线 ------ 等值线和标注是一体的
        if products.contour['visible']:

            matplotlib.rcParams['contour.negative_linestyle'] = 'dashed'
            if products.contour['colorline']:
                CS1 = m.contour(self.X, self.Y, self.Z, levels=level,
                                linewidths=products.contour['linewidth'])
            else:
                CS1 = m.contour(self.X, self.Y, self.Z, levels=level,
                                linewidths=products.contour['linewidth'], colors=products.contour['linecolor'])
            # 用区域边界裁切等值线图
            if not products.cutborders[0]['path'] is None and products.cutborders[0]['using']:
                for collection in CS1.collections:
                    collection.set_clip_on(True)
                    collection.set_clip_path(patch)
            # 是否绘制等值线标注
            if products.contourlabel['visible']:
                plt.clabel(CS1, inline=1, fmt=products.contourlabel['fmt'],
                           fontsize=products.contourlabel['fontsize'],
                           colors=products.contourlabel['fontcolor'])

        # 是否绘制色斑图 ------ 色版图、图例、裁切是一体的
        if products.contourfvisible:
            # 绘制色斑图
            if products.micapslegendvalue:

                CS = m.contourf(self.X, self.Y, self.Z, cmap=cmap,
                                levels=levels,
                                extend=extend, orientation='vertical', origin=origin)
            else:

                CS = m.contourf(self.X, self.Y, self.Z,  # cax=axins,
                                levels=products.legendvalue, colors=products.legendcolor,
                                extend=extend, orientation='vertical', origin=origin)

            # 用区域边界裁切色斑图
            if products.cutborders[0]['path'] is not None and products.cutborders[0]['using']:
                for collection in CS.collections:
                    collection.set_clip_on(True)
                    collection.set_clip_path(patch)

            if m is plt:
                # 插入一个新坐标系 以使图例在绘图区内部显示
                ax2 = plt.gca()
                axins = inset_axes(ax2, width="100%", height="100%", loc=1, borderpad=0)
                axins.axis('off')
                axins.margins(0, 0)
                axins.xaxis.set_ticks_position('bottom')
                axins.yaxis.set_ticks_position('left')
                axins.set_xlim(xmin, xmax)
                axins.set_ylim(ymin, ymax)

                # 画图例
                if products.islegendpic:
                    # 插入图片
                    arr_lena = read_png(products.legendpic)
                    image_box = OffsetImage(arr_lena, zoom=products.legendopacity)
                    ab = AnnotationBbox(image_box, products.legendpos, frameon=False)
                    plt.gca().add_artist(ab)
                else:
                    ticks = fmt = None
                    CB = plt.colorbar(CS, cmap='RdBu', anchor=products.anchor, shrink=products.shrink,
                                      ticks=ticks,
                                      # fraction=0.15,  # products.fraction,
                                      drawedges=True,  # not products.micapslegendvalue,
                                      filled=False,
                                      spacing='uniform',
                                      use_gridspec=False,
                                      orientation=products.orientation,
                                      # extendfrac='auto',
                                      format=fmt
                                      )

            else:

                CB = m.colorbar(CS, location=products.projection.location, size=products.projection.size,
                                pad=products.projection.pad)
                
            if CB is not None:
                CB.ax.tick_params(axis='y', length=0)

        # 绘制描述文本
        Micaps.DrawTitle(m, products, self.title)

        # 存图
        fig.savefig(products.picfile, format='png', transparent=False)
        print(products.picfile + u'存图成功!')
        if debug:
            plt.show()
