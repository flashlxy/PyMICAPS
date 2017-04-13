# -*- coding: utf-8 -*-
#
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170406

class HeadDesc:
    """
    标题描述类
    """

    def __init__(self, txt, pos, font):
        self.text = txt
        self.pos = pos
        self.font = font
        # fontdict={'family': 'monospace', 'color': 'blue'}
