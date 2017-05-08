# -*- coding: utf-8 -*-
#     Map类
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170409
from __future__ import print_function

import os

from datetime import datetime

import matplotlib
from matplotlib._png import read_png
from matplotlib.font_manager import FontProperties
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.path import Path
from matplotlib.ticker import FormatStrFormatter
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import shapefile
from matplotlib import patches

from Border import Border
from ClipBorder import ClipBorder
from Projection import Projection
import matplotlib.pyplot as plt
import numpy as np


class Map:
    """
    地图类
    """

    def __init__(self, root):

        # 地图投影
        self.projection = Projection(root[0])

        # 边界集合
        bordersleaf = root[0].find('Borders').getchildren()
        self.borders = []
        for borderleaf in bordersleaf:
            self.borders.append(Border(borderleaf))

        # clip区域集合
        clipsleaf = root[0].find('ClipBorders').getchildren()
        self.clipborders = []
        for clipleaf in clipsleaf:
            self.clipborders.append(ClipBorder(clipleaf))

        # 站点文件
        from Stations import Stations
        self.stations = Stations(root[0])

        pass

    @staticmethod
    def DrawContourfAndLegend(contourf, legend, clipborder, patch, cmap, levels, extend, extents, x, y, z, m):
        """
        
        :param contourf: 
        :param legend: 
        :param clipborder: 
        :param patch: 
        :param cmap: 
        :param levels: 
        :param extend: 
        :param extents: 
        :param x: 
        :param y: 
        :param z: 
        :param m: 
        :return: 
        """
        # 是否绘制色斑图 ------ 色版图、图例、裁切是一体的
        xmax = extents.xmax
        xmin = extents.xmin
        ymax = extents.ymax
        ymin = extents.ymin
        if contourf.contourfvisible:
            # 绘制色斑图
            if legend.micapslegendvalue:

                CS = m.contourf(x, y, z, cmap=cmap,
                                levels=levels,
                                extend=extend, orientation='vertical')
            else:

                CS = m.contourf(x, y, z,  # cax=axins,
                                levels=legend.legendvalue, colors=legend.legendcolor,
                                extend=extend, orientation='vertical', hatches=legend.hatches)

            # 用区域边界裁切色斑图
            if clipborder.path is not None and clipborder.using:
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
                if legend.islegendpic:
                    # 插入图片
                    arr_lena = read_png(legend.legendpic)
                    image_box = OffsetImage(arr_lena, zoom=legend.legendopacity)
                    ab = AnnotationBbox(image_box, legend.legendpos, frameon=False)
                    plt.gca().add_artist(ab)
                else:
                    ticks = fmt = None
                    CB = plt.colorbar(CS, cmap='RdBu', anchor=legend.anchor, shrink=legend.shrink,
                                      ticks=ticks,
                                      # fraction=0.15,  # products.fraction,
                                      drawedges=True,  # not products.micapslegendvalue,
                                      filled=False,
                                      spacing='uniform',
                                      use_gridspec=False,
                                      orientation=legend.orientation,
                                      # extendfrac='auto',
                                      format=fmt
                                      )

            else:

                CB = m.colorbar(CS, location=legend.location, size=legend.size,
                                pad=legend.pad
                                )

            if CB is not None:
				fp = Map.GetFontProperties(legend.font)
				fp_title = Map.GetFontProperties(legend.titlefont)
				CB.set_label(legend.title, fontproperties=fp_title, color=legend.titlefont['color'])

				ylab = CB.ax.yaxis.get_label()
				ylab.set_rotation(legend.titlepos['rotation'])
				ylab.set_va(legend.titlepos['va'])
				ylab.set_ha(legend.titlepos['ha'])
				ylab.set_y(legend.titlepos['ypercent'])

				if not legend.micapslegendvalue and legend.legendvaluealias:
					CB.set_ticklabels(legend.legendvaluealias, update_ticks=True)
				CB.ax.tick_params(axis='y', direction='in', length=0)
				for label in CB.ax.xaxis.get_ticklabels() + CB.ax.yaxis.get_ticklabels():
					label.set_color(legend.font['color'])
					label.set_fontproperties(fp)

    @staticmethod
    def DrawContourAndMark(contour, x, y, z, level, clipborder, patch, m):

        # 是否绘制等值线 ------ 等值线和标注是一体的

        if contour.contour['visible']:

            matplotlib.rcParams['contour.negative_linestyle'] = 'dashed'
            if contour.contour['colorline']:
                CS1 = m.contour(x, y, z, levels=level,
                                linewidths=contour.contour['linewidth'])
            else:
                CS1 = m.contour(x, y, z, levels=level,
                                linewidths=contour.contour['linewidth'], colors=contour.contour['linecolor'])

            # 是否绘制等值线标注
            if contour.contourlabel['visible']:
                CS2 = plt.clabel(CS1, inline=1, fmt=contour.contourlabel['fmt'],
                                 inline_spacing=contour.contourlabel['inlinespacing'],
                                 fontsize=contour.contourlabel['fontsize'],
                                 colors=contour.contourlabel['fontcolor'])

            # 用区域边界裁切等值线图
            if clipborder.path is not None and clipborder.using:
                for collection in CS1.collections:
                    # collection.set_clip_on(True)
                    collection.set_clip_path(patch)

                for text in CS2:
                    if not clipborder.path.contains_point(text.get_position()):
                        text.remove()
            # print(CS2)

    @staticmethod
    def DrawClipBorders(clipborders):

        # 绘制裁切区域边界并返回
        path = clipborders[0].path
        linewidth = clipborders[0].linewidth
        linecolor = clipborders[0].linecolor
        if path is not None:
            patch = patches.PathPatch(path,
                                      linewidth=linewidth,
                                      facecolor='none',
                                      edgecolor=linecolor)
            plt.gca().add_patch(patch)
        else:
            patch = None
        return patch

    @staticmethod
    def DrawBorders(m, products):
        """
        画县市边界
        :param m: 画布对象（plt或投影后的plt)
        :param products: 产品参数
        :return: 
        """
        try:
            for area in products.map.borders:
                if not area.draw:
                    continue
                if area.filetype == 'SHP':  # shp文件
                    if m is plt:
                        Map.DrawShapeFile(area)
                    else:
                        m.readshapefile(area.file.replace('.shp', ''),
                                        os.path.basename(area.file),
                                        color=area.linecolor)
                else:  # 文本文件 , 画之前 路径中的点已经被投影了
                    if area.path is None:
                        continue
                    if area.polygon == 'ON':
                        area_patch = patches.PathPatch(area.path, linewidth=area.linewidth, linestyle='solid',
                                                       facecolor='none', edgecolor=area.linecolor)
                        plt.gca().add_patch(area_patch)
                    else:
                        x, y = zip(*area.path.vertices)
                        m.plot(x, y, 'k-', linewidth=area.linewidth, color=area.linecolor)
        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(products.xmlfile, err, datetime.now()))

    @staticmethod
    def DrawShapeFile(area):
        """
        在画布上绘制shp文件
        :param area: 包含shp文件名及线宽和线颜色的一个字典
        :return: 
        """
        try:
            shpfile = area.file
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
                plt.plot(x, y, 'k-', linewidth=area.linewidth, color=area.linecolor)
        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(area['file'], err, datetime.now()))

    @staticmethod
    def DrawWorld(products, m):
        pj = products.map.projection
        if pj.coastlines:
            m.drawcoastlines(linewidth=0.25)
        if pj.countries:
            m.drawcountries(linewidth=0.25)

        if pj.lsmask['visible']:
            m.drawlsmask(land_color=pj.lsmask['land_color'],
                         ocean_color=pj.lsmask['ocean_color'], resolution='l')

    @staticmethod
    def DrawGridLine(products, m):
        pj = products.map.projection
        if m is plt:
            # 坐标轴
            plt.axis(pj.axis)

            # 设置坐标轴刻度值显示格式
            if pj.axis == 'on':
                x_majorFormatter = FormatStrFormatter(pj.axisfmt[0])
                y_majorFormatter = FormatStrFormatter(pj.axisfmt[1])
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

                xaxis.set_visible(pj.lonlabels[3] == 1)
                yaxis.set_visible(pj.latlabels[0] == 1)

            return
        else:
            # draw parallels and meridians.
            if pj.axis == 'on':
                m.drawparallels(np.arange(-80., 81., 10.),
                                labels=pj.latlabels,
                                family='DejaVu Sans',
                                fontsize=10)
                m.drawmeridians(np.arange(-180., 181., 10.),
                                labels=pj.lonlabels,
                                family='DejaVu Sans',
                                fontsize=10)

    @staticmethod
    def GetFontProperties(font):
        fontfile = r"C:\WINDOWS\Fonts\{0}".format(font['family'])
        if not os.path.exists(fontfile):
            fp = FontProperties(family=font['family'], weight=font['weight'], size=font['size'])
        else:
            fp = FontProperties(fname=fontfile, weight=font['weight'], size=font['size'])
        return fp
		
