# -*- coding: utf-8 -*-
########################################################################################################################
# ### This module enables you to maskout the unneccessary data outside the
#                     interest region on a matplotlib-plotted output instance
# ################### in an effecient way,You can use this script for free   ###########################################
# ######################################################################################################################
# ####USAGE:INPUT include 'originfig':the matplotlib instance##
#                         'ax': the Axes instance
#                         'shapefile': the shape file used for generating a basemap A
#                         'region':the name of a region of on the basemap A,outside the region the data is to be maskout
#           OUTPUT    is  'clip' :the the masked-out or clipped matplotlib instance.
import shapefile
from matplotlib.path import Path
from matplotlib.patches import PathPatch


def getPathFromShp(shpfile, region):
    try:
        sf = shapefile.Reader(shpfile)
        vertices = []  # 这块是已经修改的地方
        codes = []  # 这块是已经修改的地方

        for shape_rec in sf.shapeRecords():
            # if shape_rec.record[3] == region:  # 这里需要找到和region匹配的唯一标识符，record[]中必有一项是对应的。
            if shape_rec.record[4] in region or region == [100000]:  # 这块是已经修改的地方
                pts = shape_rec.shape.points
                prt = list(shape_rec.shape.parts) + [len(pts)]
                for i in range(len(prt) - 1):
                    for j in range(prt[i], prt[i + 1]):
                        vertices.append((pts[j][0], pts[j][1]))
                    codes += [Path.MOVETO]
                    codes += [Path.LINETO] * (prt[i + 1] - prt[i] - 2)
                    codes += [Path.CLOSEPOLY]
                path = Path(vertices, codes)
        return path
    except Exception as err:
        print(err)
        return None


def shp2clip(originfig, ax, shpfile, region):
    sf = shapefile.Reader(shpfile)
    vertices = []  # 这块是已经修改的地方
    codes = []  # 这块是已经修改的地方
    for shape_rec in sf.shapeRecords():
        # if shape_rec.record[3] == region:  # 这里需要找到和region匹配的唯一标识符，record[]中必有一项是对应的。
        if shape_rec.record[4] in region:  # 这块是已经修改的地方
            pts = shape_rec.shape.points
            prt = list(shape_rec.shape.parts) + [len(pts)]
            for i in range(len(prt) - 1):
                for j in range(prt[i], prt[i + 1]):
                    vertices.append((pts[j][0], pts[j][1]))
                codes += [Path.MOVETO]
                codes += [Path.LINETO] * (prt[i + 1] - prt[i] - 2)
                codes += [Path.CLOSEPOLY]
            path = Path(vertices, codes)
            # extents = path.get_extents()
            patch = PathPatch(path, transform=ax.transData, facecolor='none', edgecolor='black')
    for contour in originfig.collections:
        contour.set_clip_path(patch)
    return path, patch
