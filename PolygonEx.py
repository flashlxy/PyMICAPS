# -*- coding: utf-8 -*-
# !/usr/bin/env python
# ##############################################
# Name: PolygonEx.py
# Purpose: 获得凸型轮廓扩大选区的最外围点
# Author: liuxianyao
# Created: 04/11/2015
# ##############################################

import sys

#reload(sys)
#sys.setdefaultencoding('utf-8')
import scipy
import scipy.linalg
import scipy.integrate
import scipy.spatial
import scipy.spatial._procrustes
import scipy.special._ufuncs_cxx
import scipy.optimize._lbfgsb
import scipy.linalg.cython_blas
import scipy.linalg.cython_lapack
from sympy import *
from pylab import *


class PolygonEx:
    def __init__(self, lons, lats, zvalues, d, path):
        """
        :param lons: x方向坐标数组
        :param lats: y方向坐标数组
        :param zvalues: 坐标数组对应的点值
        :param d: 扩大选取的距离
        :param path: 切图所用的path
        :type self: object
        """
        self.lons = lons
        self.lats = lats
        self.zvalues = zvalues
        self.d = d
        self.path = path

    def point_in_path(self, point):
        return self.path.contains_point((point[0], point[1]))

    def get_extend_hull(self):
        ext_points = []
        # 点集转换为numpy数组
        points = np.array([self.lons, self.lats]).T
        if len(points) < 3:
            return ext_points
        # 获取点集的凸多边形轮廓
        hull = scipy.spatial.ConvexHull(points)

        for simplex in hull.simplices:
            # 设置初值 以获得两个解
            if simplex[1] == 0:
                continue
            pairs = [True, False]
            for pair in pairs:
                # print(pair)
                extend_point = self.equations(points[simplex], pair)
                # 在边界内的点排除
                if extend_point and not self.point_in_path(extend_point):
                    ext_points.append([extend_point[0], extend_point[1], self.zvalues[simplex[0]]])
        return ext_points

    def equations(self, point_pairs, is_less):
        """
        以一条线段作为直角三角形的一条边，从这条线段的起点向该线段引一条距离为d的垂线，
        用垂线的另一点和该线段组成一个直角三角形，这个垂线上的另一点即为要扩展的轮廓的一点
        用以下两个方程组成二元二次方程组，求解可获得这点坐标
        ① 直角,向量法.（x-x1)(x2-x1)+(y-y1)(y2-y1)=0
        ② L,两点距离公式.（x-x1)²+(y-y1)²=l²
        解二元二次方程
        :param point_pairs:直角三角形的一条直角边
        :param is_less:初值的x坐标值是否大于直角边起点的x坐标值
        :return:返回一个解（x,y)
        :rtype: object
        """
        try:
            x1 = point_pairs[0][0]
            y1 = point_pairs[0][1]
            x2 = point_pairs[1][0]
            y2 = point_pairs[1][1]
            deta = 0.05
            if is_less:
                init_pairs = [x1 - deta, y1]
            else:
                init_pairs = [x1 + deta, y1]

            x = Symbol('x')
            y = Symbol('y')
            func = [(x2 - x1) * (x - x1) + (y2 - y1) * (y - y1),
                    (x - x1) ** 2 + (y - y1) ** 2 - self.d ** 2]
            return nsolve(func, [x, y], init_pairs)
        except Exception as err:
            return None
