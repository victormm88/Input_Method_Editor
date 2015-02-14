# -*- coding: utf-8 -*-

'entity_Word'

__author__ = 'Wang Junqi'

class word(object):
    def __init__(self,name):
        self.name=name;
        self.freq=0;
        self.bigram={};
        # self.pin=pin;
