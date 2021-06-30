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
NBIT_0 = 0
NBIT_1 = 1
NBIT_X = -1

NBITLIST_ALL = (NBIT_0, NBIT_1, NBIT_X)

NVALUE_0 = (NBIT_0, NBIT_0)
NVALUE_1 = (NBIT_1, NBIT_1)
NVALUE_P01 = (NBIT_0, NBIT_1)
NVALUE_P10 = (NBIT_1, NBIT_0)
NVALUE_X = (NBIT_X, NBIT_X)
NVALUE_PX0 = (NBIT_X, NBIT_0)
NVALUE_PX1 = (NBIT_X, NBIT_1)
NVALUE_P0X = (NBIT_0, NBIT_X)
NVALUE_P1X = (NBIT_1, NBIT_X)

NVALUELIST_ALL = (NVALUE_0, NVALUE_1, NVALUE_P01, NVALUE_P10, NVALUE_X, NVALUE_PX0, NVALUE_PX1, NVALUE_P0X, NVALUE_P1X)



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

    # Logic value of nodes
    def nvalue_negate_bit(self, b):
        '''
        对1bit的逻辑值取反

        :param b:
        :return:
        '''
        assert b in NBITLIST_ALL
        if b == NBIT_1:
            return NBIT_0
        elif b == NBIT_0:
            return NBIT_1
        elif b == NBIT_X:
            return NBIT_X
        else:
            assert False

    def nvalue_negate(self, nvalue):
        '''
        对一个nvalue值（包含2 bits 逻辑值）取反。

        :param nvalue:
        :return:
        '''
        assert nvalue in NVALUELIST_ALL
        # if nvalue == NVALUE_0:
        #     return NVALUE_1
        # elif nvalue == NVALUE_1:
        #     return NVALUE_0
        # elif nvalue == NVALUE_P01:
        #     return NVALUE_P10
        # elif nvalue == NVALUE_P10:
        #     return NVALUE_P01
        # elif nvalue == NVALUE_X:
        #     return NVALUE_X
        # elif nvalue == NVALUE_PX0:
        #     return NVALUE_PX1
        # elif nvalue == NVALUE_PX1:
        #     return NVALUE_PX0
        # elif nvalue == NVALUE_P0X:
        #     return NVALUE_P1X
        # elif nvalue == NVALUE_P1X:
        #     return NVALUE_P0X
        # else:
        #     assert False
        v0 = self.nvalue_negate_bit( nvalue[0] )
        v1 = self.nvalue_negate_bit( nvalue[1] )
        nvalue_result = (v0, v1)
        return nvalue_result

    # def nvalue_polymorphic(self, nvalue):
    #     assert nvalue in NVALUELIST_ALL
    #     if nvalue == NVALUE_0:
    #         return NVALUE_P01
    #     elif nvalue == NVALUE_1:
    #         return NVALUE_P10
    #     elif nvalue in (NVALUE_P01, NVALUE_P0X):
    #         return NVALUE_0
    #     elif nvalue == (NVALUE_P10, NVALUE_P1X):
    #         return NVALUE_1
    #     elif nvalue in (NVALUE_X, NVALUE_PX0, NVALUE_PX1):
    #         return NVALUE_X
    #
    #     else:
    #         assert False

    def nvalue_and_bit(self, nbit1, nbit2):
        '''
        对两个1 bit逻辑值进行逻辑与

        :param nbit1:
        :param nbit2:
        :return:
        '''
        assert nbit1 in NBITLIST_ALL
        assert nbit2 in NBITLIST_ALL

        if ( nbit1 == NBIT_0 ) or ( nbit2 == NBIT_0 ):
            return NBIT_0
        elif nbit1 == NBIT_1:
            return nbit2
        elif nbit2 == NBIT_1:
            return nbit1
        elif ( nbit1 == NBIT_X ) and ( nbit2 == NBIT_X ):
            return NBIT_X
        else:
            assert False

    def nvalue_and(self, nvalue1, nvalue2):
        '''
        对两个nvalue值（包含2 bits逻辑值）进行逻辑与。

        :param nvalue1:
        :param nvalue2:
        :return:
        '''
        assert nvalue1 in NVALUELIST_ALL
        assert nvalue2 in NVALUELIST_ALL
        v0 = self.nvalue_and_bit(nbit1=nvalue1[0], nbit2=nvalue2[0])
        v1 = self.nvalue_and_bit(nbit1=nvalue1[1], nbit2=nvalue2[1])
        nvalue_result = (v0, v1)
        return nvalue_result

    def nvalue_or_bit(self, nbit1, nbit2):
        '''
        对两个1 bit逻辑值进行逻辑或。

        :param nbit1:
        :param nbit2:
        :return:
        '''
        assert nbit1 in NBITLIST_ALL
        assert nbit2 in NBITLIST_ALL
        if ( nbit1 == NBIT_1 ) or ( nbit2 == NBIT_1 ):
            return NBIT_1
        elif nbit1 == NBIT_0:
            return nbit2
        elif nbit2 == NBIT_0:
            return nbit1
        elif ( nbit1 == NBIT_X ) and ( nbit2 == NBIT_X ):
            return NBIT_X
        else:
            assert False

    def nvalue_or(self, nvalue1, nvalue2):
        '''
        对两个nvalue值（包含2 bits逻辑值）进行逻辑或。

        :param nvalue1:
        :param nvalue2:
        :return:
        '''
        assert nvalue1 in NVALUELIST_ALL
        assert nvalue2 in NVALUELIST_ALL
        v0 = self.nvalue_or_bit(nbit1=nvalue1[0], nbit2=nvalue2[0])
        v1 = self.nvalue_or_bit(nbit1=nvalue1[1], nbit2=nvalue2[1])
        nvalue_result = (v0, v1)
        return nvalue_result




    def nvalue_maj_bit(self, bit_ch0, bit_ch1, bit_ch2):
        '''
        输入3个1bit逻辑值，返回三个逻辑值的MAJ结果。

        :param bit_ch0:
        :param bit_ch1:
        :param bit_ch2:
        :return:
        '''
        assert bit_ch0 in NBITLIST_ALL
        assert bit_ch1 in NBITLIST_ALL
        assert bit_ch2 in NBITLIST_ALL

        s01 = self.nvalue_and_bit(nbit1=bit_ch0, nbit2=bit_ch1)
        s02 = self.nvalue_and_bit(nbit1=bit_ch0, nbit2=bit_ch2)
        s12 = self.nvalue_and_bit(nbit1=bit_ch1, nbit2=bit_ch2)
        s01_02 = self.nvalue_or_bit(nbit1=s01, nbit2=s02)
        s01_02_12 = self.nvalue_or_bit(nbit1=s01_02, nbit2=s12)
        return s01_02_12

    def nvalue_calculate_value_of_a_maj(self, ch0, ch1, ch2):
        '''
        输入3个nvalue逻辑值（包含两个1bit逻辑值）ch0, ch1, ch2，输出M(ch0, ch1, ch2)。

        :param ch0:
        :param ch1:
        :param ch2:
        :return:
        '''
        assert ch0 in NVALUELIST_ALL
        assert ch1 in NVALUELIST_ALL
        assert ch2 in NVALUELIST_ALL

        v0 = self.nvalue_maj_bit(bit_ch0=ch0[0], bit_ch1=ch1[0], bit_ch2=ch2[0])
        v1 = self.nvalue_maj_bit(bit_ch0=ch0[1], bit_ch1=ch1[1], bit_ch2=ch2[1])
        nvalue_result = (v0, v1)
        return nvalue_result

    def nvalue_polymorphic(self, nvalue):
        '''
        将一个nvalue值（包含两个1bit逻辑值）附加一次多态属性，即(a, b) -> (a, b')

        :param nvalue:
        :return:
        '''
        assert nvalue in NVALUELIST_ALL
        v0 = nvalue[0]
        v1 = self.nvalue_negate_bit(b=nvalue[1])
        nvalue_result = (v0, v1)
        return nvalue_result

    def nvalue_update_value_of_a_node(self, node_id, node_value, enforce = False, replace = False):
        '''
        更新_pmig_nodes_list中记录的某个node的逻辑值。

        选项：

        enforce：若为True，则无视逻辑值类型是否为NTYPELIST_VAR，强制更改逻辑值。默认为False。

        replace：若为True，则允许替换已有的逻辑值。默认为False，即只允许在原逻辑值为None时更改。

        :param node_id:
        :param node_value:
        :param enforce:
        :param replace:
        :return:
        '''
        assert 0 <= node_id < len(self._pmig_nodes_list)
        target_node, nv_value, nv_type = self._pmig_nodes_list[node_id]
        if not enforce:
            assert nv_type in NTYPELIST_VAR
        if not replace:
            assert nv_value is None
        new_tuple = (target_node, node_value, nv_type)
        self._pmig_nodes_list[node_id] = new_tuple


    def nvalue_get_value_of_a_node(self, node_id):
        '''
        获取一个node的当前逻辑值。如果它已经被赋予逻辑值，或者它的逻辑值已被计算过，那么就直接返回这个值。如果当前它的值为空，那么就调用nvalue_calculate_value_of_a_node，并更新它的值。

        :param node_id: INT
        :return: INT
        '''

        assert 0 <= node_id < len(self._pmig_nodes_list)
        target_node, nv_value, nv_type = self._pmig_nodes_list[node_id]
        if nv_value is not None:
            return nv_value
        else:
            new_value = self.nvalue_calculate_value_of_a_node(node_id=node_id)
            self.nvalue_update_value_of_a_node(node_id=node_id, node_value=new_value, enforce=False, replace=False)
            return new_value

    def nvalue_get_nvalue_with_attr(self, literal):
        '''
        Get the logic value of a literal.
        首先得到相应node的逻辑值，然后附加上literal所具有的属性。

        :param literal:
        :return:
        '''
        target_id = literal >> 2
        target_node_obj, nv_value, nv_type = self._pmig_nodes_list[target_id]
        assert target_node_obj == self._pmig_obj.attribute_nodes_get_copy(target_id)

        if nv_value is None:
            v = self.nvalue_get_value_of_a_node(node_id=target_id)
        else:
            v = nv_value

        if PMIG.is_negated_literal(literal):
            v_ne = self.nvalue_negate(nvalue=v)
        else:
            v_ne = v

        if PMIG.is_polymorphic_literal(literal):
            v_ne_po = self.nvalue_polymorphic(nvalue=v_ne)
        else:
            v_ne_po = v_ne

        return v_ne_po

    def nvalue_calculate_value_of_a_node(self, node_id):
        '''
        计算并返回一个node的逻辑值。注意：仅依据get_value_of_a_node获得的扇入值以及该node的类型来确定输出，没有考虑在当前仿真中该node本身是否被固定为了某个值。

        :param node_id: INT -
        :return: INT
        '''

        assert 0 <= node_id < len(self._pmig_nodes_list)
        target_node, nv_value, nv_type = self._pmig_nodes_list[node_id]
        assert nv_value is None
        assert target_node == self._pmig_obj.attribute_nodes_get_copy(node_id)
        assert isinstance(target_node, graphs._MIG_Node)

        # MAJ
        if target_node.is_maj():
            ch0_literal = target_node.get_maj_child0()
            ch1_literal = target_node.get_maj_child1()
            ch2_literal = target_node.get_maj_child2()
            ch0 = self.nvalue_get_nvalue_with_attr(literal=ch0_literal)
            ch1 = self.nvalue_get_nvalue_with_attr(literal=ch1_literal)
            ch2 = self.nvalue_get_nvalue_with_attr(literal=ch2_literal)
            maj_value = self.nvalue_calculate_value_of_a_maj(ch0=ch0, ch1=ch1, ch2=ch2)
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









