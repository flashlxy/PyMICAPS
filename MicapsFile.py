# -*- coding: utf-8 -*-
#
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170406
from __future__ import print_function
from __future__ import print_function

import os

from matplotlib.font_manager import FontProperties

from Contour import Contour
from File import File
from Legend import Legend
from Title import Title
import matplotlib.pyplot as plt


class MicapsFile:
    def __init__(self, leaf):
        self.file = File(leaf)
        self.legend = Legend(leaf)
        self.contour = Contour(leaf)
        self.title = Title(leaf)

    @staticmethod
    def DrawTitle(m, title, headtxt):
        if m is plt:
            if title.mtitleposition is None:
                for desc in title.descs:
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
                if title.mtitleposition == [0, 0]:
                    plt.title(headtxt, fontdict={'fontsize': 14})
                else:
                    plt.text(title.mtitleposition[0], title.mtitleposition[1], headtxt,
                             size=14,
                             weight='bold',
                             # color='blue',
                             # fontdict=desc.font,
                             # fontproperties=font,
                             rotation=0,
                             ha='left', va='top')
        else:
            plt.title(headtxt)
