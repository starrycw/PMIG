# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/9/25
# @Author  : c
# @File    : graphs_ops.py


####### import
from pmig import graphs
PMIG = graphs.PMIG # alias

from prettytable import PrettyTable
import copy

class PMIG_operator:
    def __init__(self):
        self._pmig_obj = None # 作为操作对象的PMIG，它不应当被修改
        self._ptype = None # PMIG的多态类型

    def initialization(self, mig_obj):
        assert isinstance(mig_obj, PMIG)
        self._pmig_obj = copy.deepcopy(mig_obj)
        self._ptype = self._pmig_obj.attr_ptype_get()




class PMIG_optimization:
    def __init__(self):
        self._pmig_init = None # 初始的PMIG，它不应当被修改
        self._ptype = None # PMIG的多态类型
        self._pmig_current = None # 当前的PMIG
        self._pmig_last = None  # 前一个PMIG
        self._pmig_savepoint_dict = {} # 字典，用于存档PMIG，key为存档名称,value为PMIG类型对象

    def initialization(self, mig_obj):
        assert isinstance(mig_obj, PMIG)
        self._pmig_init = copy.deepcopy(mig_obj)
        self._ptype = self._pmig_init.attr_ptype_get()
        self._pmig_current = copy.deepcopy(mig_obj)
        self._pmig_last = None
        self._pmig_savepoint_dict = {}


    def update_current_pmig(self, new_pmig):
        assert isinstance(new_pmig, PMIG)
        self._pmig_last = copy.deepcopy(self._pmig_current)
        self._pmig_current = copy.deepcopy(new_pmig)


    def savepoint_restore_to_the_last_pmig(self):
        print("Current PMIG is restored to the last version!")
        self._pmig_current = copy.deepcopy(self._pmig_last)
        self._pmig_last = None


    def savepoint_save_current_pmig(self, name):
        assert isinstance(name, str)
        if name in self._pmig_savepoint_dict:
            print("Save current PMIG obj to savepoint. Key [" + name + "] created!")
        else:
            print("Save current PMIG obj to savepoint. The obj in key [" + name + "] is replaced!")
        self._pmig_savepoint_dict[name] = copy.deepcopy(self._pmig_current)

    def savepoint_get_pmig(self, name):
        assert name in self._pmig_savepoint_dict
        return copy.deepcopy(self._pmig_savepoint_dict[name])

    def savepoint_restore_pmig(self, name):
        assert name in self._pmig_savepoint_dict
        print("Current PMIG is restored to the version named as [" + name + "] !")
        # self._pmig_last = copy.deepcopy(self._pmig_current)
        # self._pmig_current = copy.deepcopy(self._pmig_savepoint_dict[name])
        self.update_current_pmig(new_pmig=self._pmig_savepoint_dict[name])

    def savepoint_delete_pmig(self, name):
        # assert name in self._pmig_savepoint_dict
        print("Remove key [" + name + '] in the savepoint!')
        self._pmig_savepoint_dict.pop(key=name)

    def savepoint_delete_all(self):
        print("Savepoint initialized!")
        self._pmig_savepoint_dict = {}


    def opti_clean_pos_by_type(self, po_type_tuple = (PMIG.PO_OBSOLETE, )):
        '''
        清除某些类型的POs， 并清除多余的nodes。

        :param pos: TUPLE - POs类型元组，默认包含PMIG.PO_OBSOLETE.
        :return:
        '''
        assert isinstance(self._pmig_current, PMIG)
        new_pmig = self._pmig_current.pmig_clean_pos_by_type(po_type_tuple=po_type_tuple)
        self.update_current_pmig(new_pmig=new_pmig)

    def opti_clean_irrelevant_nodes(self, pos = None):
        '''
        指定POs列表（指定id），清除与这些POs无关的node。

        :param pos: None (Default) or LIST - POs列表，默认包含当前全部POs.
        :return:
        '''
        assert isinstance(self._pmig_current, PMIG)
        new_pmig = self._pmig_current.pmig_clean_irrelevant_nodes(pos=pos)
        self.update_current_pmig(new_pmig=new_pmig)





