# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/03
# @Author  : c
# @File    : pmig_logic.py

from pmig import graphs
# AIG = graphs.AIG # alias
PMIG = graphs.PMIG # alias

from prettytable import PrettyTable
import copy
import numpy

########################################################################################################################
# class PMIG_LogicSimu_Comb
#
# @Time    : 2021/10
# @Author  : c
#
# 无latch的PMIG的功能仿真。
#
#
#
########################################################################################################################
class PMIG_LogicSimu_Comb:
#######
    # Logic bit
    LBIT_V_0 = 0
    LBIT_V_1 = 1
    LBIT_V_X = -1

    LBIT_ALL = (LBIT_V_0, LBIT_V_1, LBIT_V_X)
    LBIT_CERTAIN = (LBIT_V_0, LBIT_V_1)

    # Logic Value
    LVALUE_V_00 = (LBIT_V_0, LBIT_V_0)
    LVALUE_V_11 = (LBIT_V_1, LBIT_V_1)
    LVALUE_V_P01 = (LBIT_V_0, LBIT_V_1)
    LVALUE_V_P10 = (LBIT_V_1, LBIT_V_0)
    LVALUE_V_PXX = (LBIT_V_X, LBIT_V_X)
    LVALUE_V_PX0 = (LBIT_V_X, LBIT_V_0)
    LVALUE_V_PX1 = (LBIT_V_X, LBIT_V_1)
    LVALUE_V_P0X = (LBIT_V_0, LBIT_V_X)
    LVALUE_V_P1X = (LBIT_V_1, LBIT_V_X)

    LVALUE_ALL = (LVALUE_V_00, LVALUE_V_11, LVALUE_V_P01, LVALUE_V_P10, LVALUE_V_PXX, LVALUE_V_PX0, LVALUE_V_PX1, LVALUE_V_P0X, LVALUE_V_P1X)
    LVALUE_CERTAIN = (LVALUE_V_00, LVALUE_V_11, LVALUE_V_P01, LVALUE_V_P10)

    # Logic Type
    LTYPE_T_VARIABLE = 0
    LTYPE_T_CONST = 1

#######
    def __init__(self, pmig_obj_r):
        assert isinstance(pmig_obj_r, PMIG)
        self._pmig_obj = copy.deepcopy(pmig_obj_r)
        self._pmig_nodes_list, self._pis_id = self._analyze_pmig_obj()
        # self._pmig_nodes_list：
        #     该列表应当包含self._pmig_obj中所有的nodes信息，每个元素为一个元组： (_MIG_Node对象, 逻辑值， 逻辑值类型)。
        #     逻辑值指的是在目前的仿真中该node具体的逻辑值（定义为LVALUE_V_xxx，默认应为None，即还未赋值）；逻辑值类型指的是该node在当前仿真中的角色（定义为LTYPE_T_xxx， 默认应当为LTYPE_T_VARIABLE，即普通变量）
        #     该列表中元素的顺序必须与在self._pmig_obj._nodes中相应的顺序完全相同！
        #
        # self._pis_id：
        #     用于指明PI的顺序
        #     元素是整数，对于每个元素i，self._pmig_nodes_list[i]所对应的是一个PI类型node。
        #     列表中应当包含所有的PI位置，不能遗漏。
        #     PI在列表中的顺序决定了相应变量在输入向量中的位置。
        #     如果要调整顺序，可以使用print_pis_id来显示列表详情，然后使用change_order_pis，输入新列表。

#######
    def reset_all(self):
        '''
        重建self._pmig_nodes_list和self._pis_id

        :return:
        '''
        self._pmig_nodes_list, self._pis_id = self._analyze_pmig_obj()

#######
    def reset_node_value_all(self):
        '''
        重建self._pmig_nodes_list

        :return:
        '''
        pmig_nodes_list_temp, pis_id_temp = self._analyze_pmig_obj()
        self._pmig_nodes_list = copy.deepcopy(pmig_nodes_list_temp)

#######
    def reset_node_value(self):
        '''
        Reset the logic values in self._pmig_node_list
        在一次仿真中，设置不同的输入向量之前，先通过本方法使得所有的可变logic value值变为None。
        注意：本方法不会改变非可变的logic value值，例如，被固定为某个逻辑值的node，仍然被固定在该逻辑值。

        :return:
        '''
        new_node_list = []
        for node_i, lv_value, lv_type in self._pmig_nodes_list:
            if lv_type == self.LTYPE_T_VARIABLE:
                new_node_list.append([copy.deepcopy(node_i), None, lv_type])
            elif lv_type == self.LTYPE_T_CONST:
                new_node_list.append([copy.deepcopy(node_i), lv_value, lv_type])
            else:
                assert False
        self._pmig_nodes_list = copy.deepcopy(new_node_list)

#######
    def _analyze_pmig_obj(self):
        '''
        返回self._pmig_obj的nodes信息列表（每个元素为元组(node对象，默认的逻辑值类型，默认的逻辑值)）和pis id列表。

        :return:
        '''
        pmig_temp = copy.deepcopy(self._pmig_obj)
        nodes_list = []
        pis_id = []

        node_id = 0
        for node_i in pmig_temp.attr_nodeslist_get():
            nodes_list.append( [copy.deepcopy(node_i), None, self.LTYPE_T_VARIABLE] )
            assert (node_id == 0 and node_i.is_const0()) or (node_id > 0 and node_i.is_maj()) or (node_id > 0 and node_i.is_pi())
            if node_i.is_pi():
                pis_id.append(node_id)
            node_id = node_id + 1
        return nodes_list, pis_id

#######
    def print_pis_id(self, more_info=False):
        '''
        Print the PIs info in self._pis_id.

        :param more_info: BOOLEAN
        :return:
        '''
        print("PIs id: ", self._pis_id)
        if more_info:
            table_pis = PrettyTable(['Index', 'Type', 'Literal', 'Name'])
            id = 0
            for i in self._pis_id:
                literal = i << 2
                node_n, nv_value, nv_type = self._pmig_nodes_list[i]
                assert node_n.is_pi()
                pi_name = None
                assert isinstance(self._pmig_obj, PMIG)
                if self._pmig_obj.has_name(literal):
                    pi_name = self._pmig_obj.get_name_by_id(literal)
                table_pis.add_row([id, 'PI', '{} ({})'.format(literal, i), pi_name])
                id = id + 1
            print(table_pis)

#######
    def change_pis_order(self, input_list, mode):
        '''
        更改_pis_id列表中的顺序。

        若mode为'replace'，则new_pis_list应为完整的pis顺序列表，它将覆盖掉原有的_pis_id列表

        若mode为'swap'，则new_pis_list应为一个列表，其元素为包含两个pi id的列表[id1, id2]，按照idx的顺序，交换每一组中id1和id2的顺序。


        :param input_list:
        :param mode:
        :return:
        '''
        assert mode in ('replace', 'swap')
        assert isinstance(self._pis_id, list)
        if mode == 'replace':
            assert len(input_list) == len(self._pis_id)
            for id in self._pis_id:
                assert id in input_list
            for id in input_list:
                assert id in self._pis_id
            self._pis_id = copy.deepcopy(input_list)
        elif mode == 'swap':
            pis_id_temp = copy.deepcopy(self._pis_id)
            for group_i in input_list:
                idx_old_1 = pis_id_temp.index(group_i[0])
                idx_old_2 = pis_id_temp.index(group_i[1])
                pis_id_temp[idx_old_1], pis_id_temp[idx_old_2] = pis_id_temp[idx_old_2], pis_id_temp[idx_old_1]
            self._pis_id = copy.deepcopy(pis_id_temp)


####### negate
    def nvalue_negate_bit(self, b):
        '''
        对1bit的逻辑值取反

        :param b:
        :return:
        '''
        assert b in self.LBIT_ALL
        if b == self.LBIT_V_1:
            return self.LBIT_V_0
        elif b == self.LBIT_V_0:
            return self.LBIT_V_1
        elif b == self.LBIT_V_X:
            return self.LBIT_V_X
        else:
            assert False


    def nvalue_negate(self, nvalue):
        '''
        对一个nvalue值（包含2 bits 逻辑值）取反。

        :param nvalue:
        :return:
        '''
        assert nvalue in self.LVALUE_ALL
        v0 = self.nvalue_negate_bit(nvalue[0])
        v1 = self.nvalue_negate_bit(nvalue[1])
        nvalue_result = (v0, v1)
        return nvalue_result



####### and
    def nvalue_and_bit(self, nbit1, nbit2):
        '''
        对两个1 bit逻辑值进行逻辑与

        :param nbit1:
        :param nbit2:
        :return:
        '''
        assert nbit1 in self.LBIT_ALL
        assert nbit2 in self.LBIT_ALL

        if (nbit1 == self.LBIT_V_0) or (nbit2 == self.LBIT_V_0):
            return self.LBIT_V_0
        elif nbit1 == self.LBIT_V_1:
            return nbit2
        elif nbit2 == self.LBIT_V_1:
            return nbit1
        elif (nbit1 == self.LBIT_V_X) and (nbit2 == self.LBIT_V_X):
            return self.LBIT_V_X
        else:
            assert False


    def nvalue_and(self, nvalue1, nvalue2):
        '''
        对两个nvalue值（包含2 bits逻辑值）进行逻辑与。

        :param nvalue1:
        :param nvalue2:
        :return:
        '''
        assert nvalue1 in self.LVALUE_ALL
        assert nvalue2 in self.LVALUE_ALL
        v0 = self.nvalue_and_bit(nbit1=nvalue1[0], nbit2=nvalue2[0])
        v1 = self.nvalue_and_bit(nbit1=nvalue1[1], nbit2=nvalue2[1])
        nvalue_result = (v0, v1)
        return nvalue_result

####### or
    def nvalue_or_bit(self, nbit1, nbit2):
        '''
        对两个1 bit逻辑值进行逻辑或。

        :param nbit1:
        :param nbit2:
        :return:
        '''
        assert nbit1 in self.LBIT_ALL
        assert nbit2 in self.LBIT_ALL
        if (nbit1 == self.LBIT_V_1) or (nbit2 == self.LBIT_V_1):
            return self.LBIT_V_1
        elif nbit1 == self.LBIT_V_0:
            return nbit2
        elif nbit2 == self.LBIT_V_0:
            return nbit1
        elif (nbit1 == self.LBIT_V_X) and (nbit2 == self.LBIT_V_X):
            return self.LBIT_V_X
        else:
            assert False


    def nvalue_or(self, nvalue1, nvalue2):
        '''
        对两个nvalue值（包含2 bits逻辑值）进行逻辑或。

        :param nvalue1:
        :param nvalue2:
        :return:
        '''
        assert nvalue1 in self.LVALUE_ALL
        assert nvalue2 in self.LVALUE_ALL
        v0 = self.nvalue_or_bit(nbit1=nvalue1[0], nbit2=nvalue2[0])
        v1 = self.nvalue_or_bit(nbit1=nvalue1[1], nbit2=nvalue2[1])
        nvalue_result = (v0, v1)
        return nvalue_result

####### MAJ
    def nvalue_maj_bit(self, bit_ch0, bit_ch1, bit_ch2):
        '''
        输入3个1bit逻辑值，返回三个逻辑值的MAJ结果。

        :param bit_ch0:
        :param bit_ch1:
        :param bit_ch2:
        :return:
        '''
        assert bit_ch0 in self.LBIT_ALL
        assert bit_ch1 in self.LBIT_ALL
        assert bit_ch2 in self.LBIT_ALL

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
        assert ch0 in self.LVALUE_ALL  # , "ch0, value={}, is_int={}, xx{}".format(ch0, isinstance(ch0, int), isinstance(self.LVALUE_V_00, int))
        assert ch1 in self.LVALUE_ALL
        assert ch2 in self.LVALUE_ALL

        v0 = self.nvalue_maj_bit(bit_ch0=ch0[0], bit_ch1=ch1[0], bit_ch2=ch2[0])
        v1 = self.nvalue_maj_bit(bit_ch0=ch0[1], bit_ch1=ch1[1], bit_ch2=ch2[1])
        nvalue_result = (v0, v1)
        return nvalue_result

####### polymorphic
    def nvalue_polymorphic(self, nvalue):
        '''
        将一个nvalue值（包含两个1bit逻辑值）附加一次多态属性，即(a, b) -> (a, b')

        :param nvalue:
        :return:
        '''
        assert nvalue in self.LVALUE_ALL
        v0 = nvalue[0]
        v1 = self.nvalue_negate_bit(b=nvalue[1])
        nvalue_result = (v0, v1)
        return nvalue_result



#######
    def nvalue_update_value_of_a_node(self, node_id, node_value, enforce=False, replace=False):
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
            assert nv_type == self.LTYPE_T_VARIABLE
        if not replace:
            assert nv_value is None
        new_tuple = (target_node, node_value, nv_type)
        self._pmig_nodes_list[node_id] = copy.deepcopy(new_tuple)

#######
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

#######
    def nvalue_get_nvalue_with_attr(self, literal):
        '''
        Get the logic value of a literal.
        首先得到相应node的逻辑值，然后附加上literal所具有的属性。

        :param literal:
        :return:
        '''
        target_id = literal >> 2
        target_node_obj, nv_value, nv_type = self._pmig_nodes_list[target_id]
        assert target_node_obj == self._pmig_obj.attr_nodes_get_copy(target_id)

        # if nv_value is None:
        #     v = self.nvalue_get_value_of_a_node(node_id=target_id)
        # else:
        #     v = nv_value
        v = self.nvalue_get_value_of_a_node(node_id=target_id)

        if PMIG.is_negated_literal(literal):
            v_ne = self.nvalue_negate(nvalue=v)
        else:
            v_ne = v

        if PMIG.is_polymorphic_literal(literal):
            v_ne_po = self.nvalue_polymorphic(nvalue=v_ne)
        else:
            v_ne_po = v_ne

        return v_ne_po

#######
    def nvalue_calculate_value_of_a_node(self, node_id):
        '''
        计算并返回一个node的逻辑值。注意：仅依据get_value_of_a_node获得的扇入值以及该node的类型来确定输出，没有考虑在当前仿真中该node本身是否被固定为了某个值。

        :param node_id: INT -
        :return: INT
        '''

        assert 0 <= node_id < len(self._pmig_nodes_list)
        target_node, nv_value, nv_type = self._pmig_nodes_list[node_id]
        assert nv_value is None
        assert target_node == self._pmig_obj.attr_nodes_get_copy(node_id)
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
            # init_literal = target_node.get_latch_init()
            # next_literal = target_node.get_latch_next()
            # # 目前对latch的处理方式是：只考虑next，忽略init
            # latch_value = self.nvalue_get_nvalue_with_attr(literal=next_literal)
            # return latch_value

        # PI
        elif target_node.is_pi():
            assert False, "[ERROR] pmig_variation: PI的逻辑值为空！"

        # CONST0
        elif target_node.is_const0():
            # return graphs._MIG_Node.CONST0
            return self.LVALUE_V_00

        #
        else:
            assert False

#######
    def get_node_with_const_ltype(self):
        '''
        Return a list, containing the items that are in self._pmig_nodes_list have const logic value.

        :return:
        '''
        fixed_nodes_list = []
        for node_i, nv_value, nv_type in self._pmig_nodes_list:
            if nv_type == self.LTYPE_T_CONST:
                fixed_nodes_list.append((node_i, nv_value, nv_type))
            else:
                assert nv_type == self.LTYPE_T_VARIABLE
        return fixed_nodes_list

#######
    def return_pmig_pos_list(self, returnmode=None):
        '''
        Return the list of all POs.

        :return: LIST - List with TUPLE elements: (po_fanin, PO_type)
        '''

        pos_list = []
        pos_fanin_list = []
        for po_id, po_fanin, po_type in self._pmig_obj.get_iter_pos():
            po_name = self._pmig_obj.get_name_by_po_if_has(po_id)
            pos_list.append((po_fanin, po_type, (po_id, po_name)))
            pos_fanin_list.append(po_fanin)
        if returnmode == 'fanins_only':
            return pos_fanin_list
        else:
            return pos_list

#######
    def simu_pos_value(self, pi_vec, pos_selected=None, allow_node_with_fixed_value = False):
        '''
        输入PI逻辑值pi_vec，以及要输出的PO列表。

        其中，对于PO列表pos_selected来说，它应当是一个列表或元组，其中每个元素对应一个PO的信息，也为元组，包含4个元素：(po_value, po_fanin, po_type, po_info_tuple)。
        其中po_info_tuple可以储存PO的信息（前两个元素应当分别为id和name）。pos_selected默认为None，即自动获取所有PO。

        PI逻辑值pi_vec应当为列表或元组，并且元素个数应当恰好等于self._pis_id中的元素数，每个元素都应该是LVALUE_ALL中定义过的逻辑值。

        allow_node_with_fixed_value默认为False，这意味着如果图中的某个node的nvalue类型为不变类型，会引发异常。可以预先使用reset_node_value_all方法来重建node列表，以去除所有已设置的不变类型nodes。
        如果为True，则只会显示警告文字。需要注意的是：按照目前的算法，某个node被固定为某个逻辑值的优先级大于设置PI的逻辑值，即可能会导致某些PI的逻辑值被屏蔽。

        return result_pos_value_simple, result_pos_value, pos_selected, pi_vec

        result_pos_value_simple contains po_value
        result_pos_value contains tuple: (po_value, po_fanin, po_type)

        :param pi_vec:
        :return: LIST, LIST, LIST, LIST
        '''
        assert len(pi_vec) == len(self._pis_id)
        self.reset_node_value()
        # checks
        fixed_nodes_list = self.get_node_with_const_ltype()
        if len(fixed_nodes_list) != 0:
            if allow_node_with_fixed_value:
                print("[WARNING] pmig_verification.simu_pos_value: _pmig_nodes_list中至少有一个node为固定值，这会导致某些指定的PI向量无效！\n", list(fixed_nodes_list))
            else:
                assert False, "[ERROR] pmig_verification.simu_pos_value: _pmig_nodes_list中至少有一个node为固定值，这会导致某些指定的PI向量无效！\n {}".format(list(fixed_nodes_list))
        # Set PI value
        idx = 0
        for pi_value_i in pi_vec:
            assert pi_value_i in self.LVALUE_ALL
            node_idx = self._pis_id[idx]
            target_node, nv_value, nv_type = self._pmig_nodes_list[node_idx]
            if nv_type == self.LTYPE_T_VARIABLE:
                assert nv_value is None
                self.nvalue_update_value_of_a_node(node_id=node_idx, node_value=pi_value_i, enforce=False, replace=False)
            else:
                assert nv_type == self.LTYPE_T_CONST
                assert nv_value is not None
                assert allow_node_with_fixed_value

            idx = idx + 1

        if pos_selected is None:
            pos_selected = self.return_pmig_pos_list()

        result_pos_value = []
        result_pos_value_simple = []
        for po_fanin, po_type, po_info_tuple in pos_selected:
            po_value = self.nvalue_get_nvalue_with_attr(literal=po_fanin)
            result_pos_value.append( (po_value, po_fanin, po_type, po_info_tuple) )
            result_pos_value_simple.append(po_value)

        return result_pos_value_simple, result_pos_value, pos_selected, pi_vec


    def simu_for_exact_synthesis(self):
        '''
        仿真一个单PO、无latch、无buffer的PMIG图的逻辑功能，用于exact synthesis。

        返回值包括：
        (1) 一个元组，元素依次为PI从全0到全1时PO在模式1下的输出逻辑值。逻辑值仅有0和1两种情况。
        (2) 一个元组，元素依次为PI从全0到全1时PO在模式2下的输出逻辑值。逻辑值仅有0和1两种情况。
        (3) Bool， 若上面两个元组相等，意味着该图的PO在两种模式下功能相同，可认为非多态，此时为False。繁反之为True。

        :return: TUPLE, TUPLE, BOOL
        '''
        self.reset_all()

        result_mixed = []
        pi_len = len(self._pis_id)

        vec_max = pow(2, pi_len)
        for vec_value in range(0, vec_max):
            vec_bin = bin(vec_value)[2:]
            vec_tuple = tuple(str.zfill(vec_bin, pi_len))
            # print(len(vec_tuple), pi_len, latch_len)
            assert len(vec_tuple) == pi_len
            vec_pi_tuple = vec_tuple[:pi_len]
            pi_vec = []
            for i in vec_pi_tuple:
                if int(i) == 0:
                    pi_vec.append(self.LVALUE_V_00)
                elif int(i) == 1:
                    pi_vec.append(self.LVALUE_V_11)
                else:
                    assert False

            assert len(self.return_pmig_pos_list()) == 1
            result_pos_value_simple, result_pos_value, pos_selected, pi_vec = self.simu_pos_value(pi_vec=pi_vec, allow_node_with_fixed_value=False)

            assert len(result_pos_value) == 1
            result_mixed.append(result_pos_value[0][0])

        # 分别将两种模式下的结果记录在两个列表中
        result_f1 = []
        result_f2 = []
        if_polymorphic = False
        for mixed_value in result_mixed:
            if mixed_value == self.LVALUE_V_00:
                result_f1.append(False)
                result_f2.append(False)
            elif mixed_value == self.LVALUE_V_11:
                result_f1.append(True)
                result_f2.append(True)
            elif mixed_value == self.LVALUE_V_P01:
                result_f1.append(False)
                result_f2.append(True)
                if_polymorphic = True
            elif mixed_value == self.LVALUE_V_P10:
                result_f1.append(True)
                result_f2.append(False)
                if_polymorphic = True
            else:
                print(mixed_value)
                assert False


        return tuple(copy.deepcopy(result_f1)), tuple(copy.deepcopy(result_f2)), if_polymorphic

