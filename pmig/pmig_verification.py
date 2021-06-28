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
NTYPE_CONST = 1

NTYPELIST_VAR = (NTYPE_VARIABLE, )
NTYPELIST_FIXED = (NTYPE_CONST, )

# Values of node

NVALUE_0 = 0
NVALUE_1 = 1
NVALUE_P01 = 2
NVALUE_P10 = 3
NVALUE_X = -1

NVALUELIST_ALL = (NVALUE_0, NVALUE_1, NVALUE_P01, NVALUE_P10, NVALUE_X)



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

    def reset_node_value(self):
        '''
        Reset the logic values in self._pmig_node_list

        :return:
        '''
        new_node_list = []
        for node_i, nv_value, nv_type in self._pmig_nodes_list:
            if nv_type in NTYPELIST_VAR:
                new_node_list.append( [copy.deepcopy(node_i), None, nv_type] )
            elif nv_type in NTYPELIST_FIXED:
                new_node_list.append( [copy.deepcopy(node_i), nv_value, nv_type] )
            else:
                assert False
        self._pmig_nodes_list = copy.deepcopy(new_node_list)


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

    def get_node_with_fixed_value(self):
        '''
        Return a list, containing the items that are in self._pmig_nodes_list have fixed logic value.

        :return:
        '''
        fixed_nodes_list = []
        for node_i, nv_value, nv_type in self._pmig_nodes_list:
            if nv_type in NTYPELIST_FIXED:
                fixed_nodes_list.append( (node_i, nv_value, nv_type) )
            else:
                assert nv_type in NTYPELIST_VAR
        return fixed_nodes_list

    def nvalue_negated(self, nvalue):
        assert nvalue in NVALUELIST_ALL
        if nvalue == NVALUE_0:
            return NVALUE_1
        elif nvalue == NVALUE_1:
            return NVALUE_0
        elif nvalue == NVALUE_P01:
            return NVALUE_P10
        elif nvalue == NVALUE_P10:
            return NVALUE_P01
        elif nvalue == NVALUE_X:
            return NVALUE_X
        else:
            assert False

    def nvalue_polymorphic(self, nvalue):
        assert nvalue in NVALUELIST_ALL
        if nvalue == NVALUE_0:
            return NVALUE_P01
        elif nvalue == NVALUE_1:
            return NVALUE_P10
        elif nvalue == NVALUE_P01:
            return NVALUE_0
        elif nvalue == NVALUE_P10:
            return NVALUE_1
        elif nvalue == NVALUE_X:
            return NVALUE_X
        else:
            assert False

    def nvalue_add_attr_if_has_attr(self, nvalue, literal):
        '''
        如果literal具有取反/多态属性，那么就为nvalue赋予相应的属性。

        :param nvalue: INT -
        :param literal: INT - Literal
        :return: INT -
        '''
        assert 0 <= nvalue < len(self._pmig_nodes_list)
        if PMIG.is_negated_literal(literal):
            nvalue_1 = self.nvalue_negated(nvalue=nvalue)
        else:
            nvalue_1 = nvalue
        if PMIG.is_polymorphic_literal(literal):
            nvalue_2 = self.nvalue_polymorphic(nvalue=nvalue_1)
        else:
            nvalue_2 = nvalue_1

        return nvalue_2


    def nvalue_get_value_of_a_node(self, node_id):
        '''
        获取一个node的当前逻辑值。如果它已经被赋予逻辑值，或者它的逻辑值已被计算过，那么就直接返回这个值。如果当前它的值为空，那么就调用nvalue_calculate_value_of_a_node。

        :param node_id: INT
        :return: INT
        '''

        assert 0 <= node_id < len(self._pmig_nodes_list)
        target_node, nv_value, nv_type = self._pmig_nodes_list[node_id]
        if nv_value != None:
            return nv_value
        else:
            return self.nvalue_calculate_value_of_a_node(node_id=node_id)

    def nvalue_calculate_value_of_a_maj(self, ch0, ch1, ch2):
        '''
        输入3个逻辑值ch0, ch1, ch2，输出M(ch0, ch1, ch2)。

        :param ch0:
        :param ch1:
        :param ch2:
        :return:
        '''
        assert ch0 in NVALUELIST_ALL
        assert ch1 in NVALUELIST_ALL
        assert ch2 in NVALUELIST_ALL
        ???

    def nvalue_calculate_value_of_a_node(self, node_id):
        '''
        计算并返回一个node的逻辑值。注意：仅依据get_value_of_a_node获得的扇入值以及该node的类型来确定输出，没有考虑该node的值类型。

        :param node_id: INT -
        :return: INT
        '''

        assert 0 <= node_id < len(self._pmig_nodes_list)
        target_node, nv_value, nv_type = self._pmig_nodes_list[node_id]
        assert nv_value == None

        # MAJ
        if target_node.is_maj():
            ch0_literal = target_node.get_maj_child0()
            ch1_literal = target_node.get_maj_child1()
            ch2_literal = target_node.get_maj_child2()
            ch0_id = ch0_literal >> 2
            ch1_id = ch1_literal >> 2
            ch2_id = ch2_literal >> 2
            ch0_value = self.nvalue_get_value_of_a_node(ch0_id)
            ch1_value = self.nvalue_get_value_of_a_node(ch1_id)
            ch2_value = self.nvalue_get_value_of_a_node(ch2_id)
            ch0_value_with_attr = self.nvalue_add_attr_if_has_attr(nvalue=ch0_value, literal=ch0_literal)
            ch1_value_with_attr = self.nvalue_add_attr_if_has_attr(nvalue=ch1_value, literal=ch1_literal)
            ch2_value_with_attr = self.nvalue_add_attr_if_has_attr(nvalue=ch2_value, literal=ch2_literal)
            maj_value = self.nvalue_calculate_value_of_a_maj(ch0=ch0_value_with_attr, ch1=ch1_value_with_attr, ch2=ch2_value_with_attr)
            return maj_value

        # Latch
        elif target_node.is_latch():
        ???
        # Buffer
        elif target_node.is_buf():

        # PI
        elif target_node.is_pi():

        # CONST0
        elif target_node.is_const0():

        #
        else:
            assert False





    def simu_pos_value(self, pi_vec, latch_vec, allow_node_with_fixed_value = False):
        '''
        Assign

        :param pi_vec:
        :return:
        '''
        assert len(pi_vec) == len(self._pis_id)
        assert len(latch_vec) == len(self._latches_id)
        self.reset_node_value()
        # checks
        fixed_nodes_list = self.get_node_with_fixed_value()
        if len(fixed_nodes_list) != 0:
            if allow_node_with_fixed_value:
                print("[WARNING] pmig_verification.simu_pos_value: _pmig_nodes_list中至少有一个node为固定值，这会导致某些指定的PI向量无效！\n", list(fixed_nodes_list))
            else:
                assert False, "[ERROR] pmig_verification.simu_pos_value: _pmig_nodes_list中至少有一个node为固定值，这会导致某些指定的PI向量无效！\n {}".format(list(fixed_nodes_list))
                ???









