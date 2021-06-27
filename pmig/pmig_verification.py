# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/6/27
# @Author  : c
# @File    : pmig_verification.py
#

from pmig import graphs
# AIG = graphs.AIG # alias
PMIG = graphs.PMIG # alias

from prettytable import PrettyTable
import copy

# Types of node
NTYPE_VARIABLE = 0

# Values of node

NVALUE_0 = 0
NVALUE_1 = 1
NVALUE_P01 = 2
NVALUE_P10 = 3
NVALUE_X = -1



class PMIG_Verification:
    def __init__(self, pmig_obj):
        assert isinstance(pmig_obj, PMIG)
        self._pmig_obj = pmig_obj
        self._pmig_nodes_list, self._pis_id, self._latches_id = self.init_pmig_nodes_list()
        # self._pmig_nodes_list：
        #     该列表应当包含self._pmig_obj中所有的nodes信息，每个元素为一个元组： (_MIG_Node对象, 逻辑值， 逻辑值类型)。
        #     逻辑值指的是在目前的仿真中该node具体的逻辑值（定义为NVALUE_xxx，默认应为None，即还未赋值）；逻辑值类型指的是该node在当前仿真中的角色（定义为NTYPE_xxx， 默认应当为NTYPE_VARIABLE，即普通变量）
        #     该列表中元素的顺序必须与在self._pmig_obj._nodes中相应的顺序完全相同！
        #
        # self._pis_id以及self._latches_id：
        #     这两个列表的元素都是整数，每个元素i都表示self._pmig_nodes_list[i]元素所对应的是一个PI/latch类型node。
        #     列表中应当包含所有的PI和latch位置，不能遗漏。
        #     PI/latch在列表中的顺序决定了相应变量在输入向量和输出向量中的位置。
        #     如果要调整顺序，可以使用print_pis_id来显示列表详情，然后使用change_order_pis和change_order_latches，输入新列表。

    def init_pmig_nodes_list(self):
        '''
        Return the list of all nodes, the list of PIs id, and the list of latches id.

        :return:
        '''
        nodes_list = []
        pis_id = []
        latches_id = []

        node_id = 0
        for node_i in self._pmig_obj.attribute_get_nodes_list():
            nodes_list.append( [copy.deepcopy(node_i), None, NTYPE_VARIABLE] ) # [_MIG_Node obj, Value, Type]
            assert (node_id == 0 and node_i.is_const0()) or (node_id > 0 and not node_i.is_const0())
            if node_i.is_pi():
                pis_id.append(node_id)
            if node_i.is_latch():
                latches_id.append(node_id)
            node_id = node_id + 1
        return nodes_list, pis_id, latches_id

    def print_pis_id(self, more_info = False):
        '''
        Print the PIs and Latches in self._pis_id and self._latches_id.

        :param more_info: BOOLEAN
        :return:
        '''
        print("PIs id: ", self._pis_id)
        print("Latches id: ", self._latches_id)
        if more_info:
            table_pis = PrettyTable(['NO.', 'Type', 'Literal', 'Name'])
            id = 0
            for i in self._pis_id:
                literal = i << 2
                node_n, nv_value, nv_type = self._pmig_nodes_list[i]
                assert node_n.is_pi()
                pi_name = None
                assert isinstance(self._pmig_obj, PMIG)
                if self._pmig_obj.has_name(literal):
                    pi_name = self._pmig_obj.get_name_by_id(literal)
                table_pis.add_row( [id, 'PI', literal, pi_name] )
                id = id + 1
            print(table_pis)

            table_latches = PrettyTable(['NO.', 'Type', 'Literal', 'Init', 'Next', 'Name'])
            id = 0
            for i in self._latches_id:
                literal = i << 2
                node_n, nv_value, nv_type = self._pmig_nodes_list[i]
                assert node_n.is_latch()
                latch_name = None
                assert isinstance(self._pmig_obj, PMIG)
                if self._pmig_obj.has_name(literal):
                    latch_name = self._pmig_obj.get_name_by_id(literal)
                latch_init = self._pmig_obj.get_latch_init(literal)
                latch_next = self._pmig_obj.get_latch_next(literal)
                table_pis.add_row( [id, 'Latch', literal, latch_init, latch_next, latch_name] )
                id = id + 1
            print(table_latches)

    def change_order_pis(self, new_pis_list):
        assert len(new_pis_list) == len(self._pis_id)
        for id in self._pis_id:
            assert id in new_pis_list
        for id in new_pis_list:
            assert id in self._pis_id
        self._pis_id = copy.deepcopy(new_pis_list)

    def change_order_latches(self, new_lat_list):
        assert len(new_lat_list) == len(self._latches_id)
        for id in self._latches_id:
            assert id in new_lat_list
        for id in new_lat_list:
            assert id in self._latches_id
        self._latches_id = copy.deepcopy(new_lat_list)



