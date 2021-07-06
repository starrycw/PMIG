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
        self._pmig_nodes_list, self._pis_id, self._latches_id = self.return_pmig_nodes_list()
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
    def reset_all(self):
        new_pmig_nodes_list, new_pis_id, new_latches_id = self.return_pmig_nodes_list()
        self._pmig_nodes_list = copy.deepcopy(new_pmig_nodes_list)
        self._pis_id = copy.deepcopy(new_pis_id)
        self._latches_id = copy.deepcopy(new_latches_id)

    def return_pmig_nodes_list(self):
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

    def return_pmig_pos_list(self, returnmode=None):
        '''
        Return the list of all POs.

        :return: LIST - List with TUPLE elements: (po_fanin, PO_type)
        '''

        pos_list = []
        pos_fanin_list = []
        for po_id, po_fanin, po_type in self._pmig_obj.get_iter_pos():
            po_name = self._pmig_obj.get_name_by_po_if_has(po_id)
            pos_list.append( (po_fanin, po_type, (po_id, po_name)) )
            pos_fanin_list.append(po_fanin)
        if returnmode == 'fanins_only':
            return pos_fanin_list
        else:
            return pos_list

    def return_latch_fanin_as_po(self):
        '''
        将latch的fanin作为PO列表返回。返回值格式与return_pmig_pos_list相同。

        :return:
        '''
        latch_pos = []
        for l_literal in self._pmig_obj.get_iter_latches():
            l_fanin = self._pmig_obj.get_latch_next(l=l_literal)
            l_name = None
            if self._pmig_obj.has_name(l_literal):
                l_name = self._pmig_obj.get_name_by_id(l_literal)
            current_fanin_list = self.return_pmig_pos_list(returnmode='fanins_only')
            if not (l_fanin in current_fanin_list):
                latch_pos.append( (l_fanin, 'latch', ('latch_fanin', l_name)) )
        return latch_pos


    def reset_node_value(self):
        '''
        Reset the logic values in self._pmig_node_list
        在一次仿真中，设置不同的输入向量之前，先通过本方法使得所有的可变nvalue值变为None。
        注意：本方法不会改变非可变的nvalue值，例如，被固定为某个逻辑值的node，仍然被固定在该逻辑值。

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
        assert ch0 in NVALUELIST_ALL #, "ch0, value={}, is_int={}, xx{}".format(ch0, isinstance(ch0, int), isinstance(NVALUE_0, int))
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
            assert False
            init_literal = target_node.get_latch_init()
            next_literal = target_node.get_latch_next()
            # 目前对latch的处理方式是：只考虑next，忽略init
            latch_value = self.nvalue_get_nvalue_with_attr(literal=next_literal)
            return latch_value

        # Buffer
        elif target_node.is_buffer():
            bufin_literal = target_node.get_buf_in()
            buf_value = self.nvalue_get_nvalue_with_attr(literal=bufin_literal)
            return buf_value

        # PI
        elif target_node.is_pi():
            assert False, "[ERROR] pmig_variation: PI的逻辑值为空！"

        # CONST0
        elif target_node.is_const0():
            # return graphs._MIG_Node.CONST0
            return NVALUE_0

        #
        else:
            assert False





    def simu_pos_value(self, pi_vec, latch_vec, pos_selected=None, allow_node_with_fixed_value = False):
        '''
        输入PI逻辑值pi_vec，latch逻辑值latch_vec，以及要输出的PO列表。

        其中，对于PO列表pos_selected来说，它应当是一个列表或元组，其中每个元素对应一个PO的信息，也为元组，包含4个元素：(po_value, po_fanin, po_type, po_info_tuple)。
        其中po_info_tuple可以储存PO的信息（前两个元素应当分别为id和name）。pos_selected默认为None，即自动获取所有PO。

        PI逻辑值pi_vec以及latch逻辑值latch_vec都应当为列表或元组，并且元素个数应当恰好等于self._pis_id和self._latches_id中的元素数，每个元素都应该是NVALUELIST_ALL中定义过的逻辑值。

        allow_node_with_fixed_value默认为False，这意味着如果图中的某个node的nvalue类型为不变类型，会引发异常。
        如果为True，则只会显示警告文字。需要注意的是：按照目前的算法，某个node被固定为某个逻辑值的优先级大于设置PI的逻辑值，即可能会导致某些PI的逻辑值被屏蔽。

        :param pi_vec:
        :return: LIST, LIST, LIST - The first LIST contains tuple: (po_value, po_fanin, po_type)
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
        # Set PI value
        idx = 0
        for pi_value_i in pi_vec:
            assert pi_value_i in NVALUELIST_ALL
            node_idx = self._pis_id[idx]
            target_node, nv_value, nv_type = self._pmig_nodes_list[node_idx]
            assert nv_type == NTYPE_VARIABLE
            assert nv_value is None
            self.nvalue_update_value_of_a_node(node_id=node_idx, node_value=pi_value_i)
            idx = idx + 1
        # Set LATCH value
        idx = 0
        for latch_value_i in latch_vec:
            node_idx = self._latches_id[idx]
            target_node, nv_value, nv_type = self._pmig_nodes_list[node_idx]
            assert nv_type == NTYPELIST_VAR
            assert nv_value is None
            self.nvalue_update_value_of_a_node(node_id=node_idx, node_value=latch_value_i)
            idx = idx + 1


        if pos_selected is None:
            pos_selected = self.return_pmig_pos_list()
            for latch_po_i in self.return_latch_fanin_as_po():
                pos_selected.append(latch_po_i)
        result_pos_value = []
        for po_fanin, po_type, po_info_tuple in pos_selected:
            po_value = self.nvalue_get_nvalue_with_attr(literal=po_fanin)
            result_pos_value.append( (po_value, po_fanin, po_type, po_info_tuple) )

        return result_pos_value, pos_selected, pi_vec

    def run_simu(self, mode=None):
        if mode is None:
            result_list = []
            pos_list = None
            pi_len = len(self._pis_id)
            latch_len = len(self._latches_id)
            vec_max = pow( 2, (pi_len + latch_len) )
            for vec_value in range(0, vec_max):
                vec_bin = bin(vec_value)[2:]
                vec_tuple = tuple( str.zfill( vec_bin, (pi_len+latch_len) ) )
                # print(len(vec_tuple), pi_len, latch_len)
                assert len(vec_tuple) == pi_len + latch_len
                vec_pi_tuple = vec_tuple[:pi_len]
                vec_latch_tuple = vec_tuple[pi_len:]
                pi_vec = []
                latch_vec = []
                for i in vec_pi_tuple:
                    if int(i) == 0:
                        pi_vec.append(NVALUE_0)
                    elif int(i) == 1:
                        pi_vec.append(NVALUE_1)
                    else:
                        assert False
                for i in vec_latch_tuple:
                    if int(i) == 0:
                        latch_vec.append(NVALUE_0)
                    elif int(i) == 1:
                        latch_vec.append(NVALUE_1)
                    else:
                        assert False
                result_pos_value, pos_selected, pi_vec = self.simu_pos_value(pi_vec=pi_vec, latch_vec=latch_vec, allow_node_with_fixed_value=False)
                if vec_value == 0:
                    assert pos_list is None
                    pos_list = copy.deepcopy(pos_selected)
                else:
                    assert pos_selected == pos_list
                result_list.append(result_pos_value)
                print("PI:{}, latch:{}, result:{}".format(pi_vec, latch_vec, result_pos_value))
            # 整理结果
            pos_nvalue = []
            for nvalue_i in result_list:
                pos_ii = []
                for ii in nvalue_i:
                    pos_ii.append(ii[0])
                pos_nvalue.append( tuple(pos_ii) )
            nvalue_by_pi_vec = tuple(pos_nvalue)
            # return
            info_temp = []
            for pis_id_i in self._pis_id:
                pis_name = None
                pis_literal = pis_id_i << 2
                if self._pmig_obj.has_name(pis_literal):
                    pis_name = self._pmig_obj.get_name_by_id(pis_literal)
                info_temp.append( (pis_id_i, pis_name) )
            simu_info_pis = copy.deepcopy(info_temp)
            info_temp = []
            for lats_id_i in self._latches_id:
                lats_name = None
                lats_literal = lats_id_i << 2
                if self._pmig_obj.has_name(lats_literal):
                    lats_name = self._pmig_obj.get_name_by_id(lats_literal)
                lats_init = self._pmig_obj.get_latch_init(lats_literal)
                lats_next = self._pmig_obj.get_latch_next(lats_literal)
                info_temp.append((lats_id_i, lats_name, lats_init, lats_next))
            simu_info_latches = copy.deepcopy(info_temp)
            simu_info_pos = copy.deepcopy(pos_list)
            # 返回值包括：
            #
            #    (simu_info_pis, simu_info_latches, simu_info_pos)分别是本次仿真时的配置，包括Input vector所对应的pi和latch，以及所监测的po。
            #    其中，simu_info_pis中每一个元素为(PI的id， PI的name)
            #    simu_info_latches中每一个元素为(latch的id， latch的name， latch的init， latch的next)
            #    simu_info_pos中每一个元素为(fanin, type, info)
            #
            #    result_list是PO的逻辑值，格式为[ [vec0下第1个PO的信息, vec0下第2个PO的信息, ...], [vec1下第1个PO的信息, vec1下第2个PO的信息, ...] ]，
            #    其中veci下第j个PO的信息为一个元组: (逻辑值，对应literal， PO type， id和name等信息)
            #
            #    nvalue_by_pi_vec则是整理后的PO的逻辑值，它是一个元组，每一个元素都代表了一种输入向量下的PO值，是一个包含各个PO逻辑值的元组
            return ( simu_info_pis, simu_info_latches, simu_info_pos ), result_list, nvalue_by_pi_vec


















