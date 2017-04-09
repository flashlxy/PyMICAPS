# -*- coding: utf-8 -*-
#
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170406
from __future__ import print_function
from __future__ import print_function

from HeadDesc import HeadDesc
from Main import parseInt
from Projection import Projection


class Title:
    def __init__(self, root):
        p = root.find("Title")

        # 是否按Micaps数据的标题写产品描述
        self.mtitleposition = Projection.leaf_to_list(p, "MTitlePosition", None)

        # 产品图片文字描述（可能多个）
        descs = p.find("Descs").getchildren()
        self.descs = []
        for desc in descs:
            txt = Projection.leaf_to_string(desc, 'Text', u'测试数据')
            pos = Projection.leaf_to_list(desc, "Position", [113.2, 30.5])
            fonts = desc.find("Font").text.strip().split(',')
            font = {'family': 'monospace', 'weight': 'bold', 'fontsize': 12, 'color': 'k'}
            if len(fonts) == 4:
                font['fontsize'] = parseInt(fonts[0].strip())
                font['family'] = fonts[1]
                font['weight'] = fonts[2]
                font['color'] = fonts[3]
            self.descs.append(HeadDesc(txt, pos, font))
