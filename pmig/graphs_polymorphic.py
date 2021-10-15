# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/6/22
# @Time    : 2021/9/23
# @Author  : c
# @File    : graphs_polymorphic.py


####### import
from pmig import graphs
PMIG = graphs.PMIG # alias

from prettytable import PrettyTable
import copy



########################################################################################################################
# class Literal_Mapping
#
# @Time    : 2021/09
# @Author  : c
#
# 在使用mux生成合并两个图时，使用这个类来存储合并前后的映射关系。
#
########################################################################################################################
class Literal_Mapping:
    def __init__(self):
        self._Dict_A_to_new = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
        self._Dict_new_to_A = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
        self._Dict_B_to_new = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
        self._Dict_new_to_B = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}

        self._Dict_BPi_to_APi = {}

    def reset_all(self):
        self._Dict_A_to_new = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
        self._Dict_new_to_A = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
        self._Dict_B_to_new = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
        self._Dict_new_to_B = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}

        self._Dict_BPi_to_APi = {}

    def _map_A_to_new_literal(self, l_A, l_new):
        assert PMIG.is_noattribute_literal(l_A)
        assert l_A not in self._Dict_A_to_new
        assert l_new not in self._Dict_new_to_A
        self._Dict_A_to_new[l_A] = l_new
        self._Dict_new_to_A[l_new] = l_A

    def _map_B_to_new_literal(self, l_B, l_new):
        assert PMIG.is_noattribute_literal(l_B)
        assert l_B not in self._Dict_B_to_new
        assert l_new not in self._Dict_new_to_B
        self._Dict_B_to_new[l_B] = l_new
        self._Dict_new_to_B[l_new] = l_B

    def map_to_new_literal(self, l_original, l_new, subgraph):
        if subgraph == 'A':
            self._map_A_to_new_literal(l_A=l_original, l_new=l_new)
        elif subgraph == 'B':
            self._map_B_to_new_literal(l_B=l_original, l_new=l_new)
        else:
            assert False

    def get_new_literal(self, l_original, subgraph):
        l_original_noattr = PMIG.get_noattribute_literal(f=l_original)
        if subgraph == 'A':
            assert l_original_noattr in self._Dict_A_to_new
            l_new = self._Dict_A_to_new[l_original_noattr]
            l_new_withattr = PMIG.add_attr_if_has_attr(f=l_new, c=l_original)
        elif subgraph == 'B':
            assert l_original_noattr in self._Dict_B_to_new
            l_new = self._Dict_B_to_new[l_original_noattr]
            l_new_withattr = PMIG.add_attr_if_has_attr(f=l_new, c=l_original)
        else:
            assert False
        return l_new_withattr

    def add_pi_merge_rules(self, merge_list):
        for pi_a, pi_b in merge_list:
            assert PMIG.is_noattribute_literal(pi_a)
            assert PMIG.is_noattribute_literal(pi_b)
            self._Dict_BPi_to_APi[pi_b] = (pi_a, False)

    def if_BPi_merged_to_APi(self, pi_b):
        assert PMIG.is_noattribute_literal(pi_b)
        if pi_b in self._Dict_BPi_to_APi:
            return True
        else:
            return False

    def apply_pi_merge(self, pi_b):
        assert self.if_BPi_merged_to_APi(pi_b=pi_b)
        pi_a, merge_state = self._Dict_BPi_to_APi[pi_b]
        assert not merge_state
        new_l = self.get_new_literal(l_original=pi_a, subgraph='A')
        self.map_to_new_literal(l_original=pi_b, l_new=new_l, subgraph='B')
        self._Dict_BPi_to_APi[pi_b] = (pi_a, True)
        return new_l


########################################################################################################################
# class MuxMap
#
# @Time    : 2021/09
# @Author  : c
#
# 在使用mux生成合并两个图时，使用这个类来存储mux本身映射前后的映射关系。
#
########################################################################################################################
class MuxMap:
    def __init__(self):
        self._Dict_mux_to_new = {}

    def add_map(self, l_mux, l_new):
        assert PMIG.is_noattribute_literal(f=l_mux)
        assert l_mux not in self._Dict_mux_to_new
        self._Dict_mux_to_new[l_mux] = l_new

    def if_mapped(self, l_mux):
        l_mux_noattr = PMIG.get_noattribute_literal(f=l_mux)
        if l_mux_noattr in self._Dict_mux_to_new:
            return True
        else:
            return False

    def get_new_l(self, l_mux):
        l_mux_noattr = PMIG.get_noattribute_literal(f=l_mux)
        l_new_temp = self._Dict_mux_to_new[l_mux_noattr]
        l_new = PMIG.add_attr_if_has_attr(f=l_new_temp, c=l_mux)
        return l_new



########################################################################################################################
# class _Base_PMIG_Gen_Comb_2to1
#
# @Time    : 2021/09
# @Author  : c
#
# 将2个非多态图通过pmux合并为多态图
# 仅作为基类，不允许使用
########################################################################################################################
class _Base_PMIG_Gen_Comb_2to1:
    def __init__(self):
        self._mig_a = None
        self._mig_b = None
        self._pmux = None
        self._pmux_literals = None
        self._ptype = None
        self._merged_pis_list = None
        self._muxed_pos_list = None
        self._pmig_generated = None
        self._pmig_generated_modified = None

        self._log_PO_id_map = None
        self._log_Literal_map = None

    def initialization(self, mig1, mig2):
        assert False

    def input_mig_checks(self, mig_obj):
        assert isinstance(mig_obj, PMIG)
        for i in mig_obj.get_iter_nodes_with_polymorphic_edge():
            return False
        for po_i in mig_obj.get_iter_pos_with_polymorphic_fanin():
            return False
        for i in mig_obj.get_iter_latches():
            return False
        return True

    def get_pmux(self):
        assert False

####### Print
    def print_pos_of_mig(self):
        '''
        Print the POs of PMIG A and PMIG B.

        :return:
        '''
        po_table = PrettyTable(["A-ID", "A-Fanin", "A-Name", "A-Type", " ", "B-ID", "B-Fanin", "B-Name", "B-Type"])
        n_pos_max = self._mig_a.n_pos()
        if self._mig_b.n_pos() > self._mig_a.n_pos():
            n_pos_max = self._mig_b.n_pos()
        for po_i in range(0, n_pos_max):
            if po_i < self._mig_a.n_pos():
                info_a = (
                self._mig_a.get_po_fanin(po_i), self._mig_a.get_name_by_po_if_has(po_i), self._mig_a.get_po_type(po_i))
            else:
                info_a = ("N/A", "N/A", "N/A")
            if po_i < self._mig_b.n_pos():
                info_b = (
                self._mig_b.get_po_fanin(po_i), self._mig_b.get_name_by_po_if_has(po_i), self._mig_b.get_po_type(po_i))
            else:
                info_b = ("N/A", "N/A", "N/A")
            assert not ("N/A" in info_a and "N/A" in info_b)
            po_table.add_row([po_i, info_a[0], info_a[1], info_a[2], ' ', po_i, info_b[0], info_b[1], info_b[2]])
        print(po_table)
        print("Type: PO_OUTPUT = 0, PO_UNDEFINED = 1")


    def print_pis_of_mig(self):
        '''
        Print the PIs of PMIG A and PMIG B.

        :return:
        '''
        pi_table = PrettyTable(["NO.", "-", "A-Literal", "A-Name", " ", "B-Literal", "B-Name"])
        n_pis_max = self._mig_a.n_pis()
        if self._mig_b.n_pis() > self._mig_a.n_pis():
            n_pis_max = self._mig_b.n_pis()
        for pi_i in range(0, n_pis_max):
            if pi_i < self._mig_a.n_pis():
                pi_a_literal = self._mig_a.get_pi_by_id(pi_i)
                if self._mig_a.has_name(pi_a_literal):
                    pi_a_name = self._mig_a.get_name_by_id(pi_a_literal)
                else:
                    pi_a_name = None
            else:
                pi_a_literal, pi_a_name = 'N/A', 'N/A'

            if pi_i < self._mig_b.n_pis():
                pi_b_literal = self._mig_b.get_pi_by_id(pi_i)
                if self._mig_b.has_name(pi_b_literal):
                    pi_b_name = self._mig_b.get_name_by_id(pi_b_literal)
                else:
                    pi_b_name = None
            else:
                pi_b_literal, pi_b_name = 'N/A', 'N/A'
            assert not ("N/A" in (pi_a_literal, pi_a_name) and "N/A" in (pi_b_literal, pi_b_name))
            pi_table.add_row([pi_i, ' ', pi_a_literal, pi_a_name, ' ', pi_b_literal, pi_b_name])

        print(pi_table)


####### Set Configurations
    # Muxed POs 应当以id指定，而merged PIs应当以literal（no attr）的方式指定
    def set_muxed_pos(self, fanin_list=None):
        '''
        Set self._muxed_pos_list list. If fanin_list == None, then the first min(_mig_b.n_pis(), __mig_a.n_pis()) POs will be added to the list.

        :param fanin_list:
        :return:
        '''
        if fanin_list is None:
            n_pos_min = self._mig_a.n_pos()
            if self._mig_b.n_pos() < self._mig_a.n_pos():
                n_pos_min = self._mig_b.n_pos()
            fanin_list = []
            for i in range(0, n_pos_min):
                fanin_list.append((i, i))

        self._muxed_pos_list = fanin_list

    def set_merged_pis(self, pi_list=None):
        '''
        Set self._merged_pis list. If pi_list == None, then the first min(_mig_b.n_pis(), __mig_a.n_pis()) PIs will be added to the list.

        :param pi_list:
        :return:
        '''
        if pi_list is None:
            n_pis_min = self._mig_a.n_pis()
            if self._mig_b.n_pis() < self._mig_a.n_pis():
                n_pis_min = self._mig_b.n_pis()
            pi_list = []
            for i in range(0, n_pis_min):
                pi_list.append((self._mig_a.get_pi_by_id(i), self._mig_b.get_pi_by_id(i)))

        self._merged_pis_list = pi_list

    def set_muxed_pos_auto(self, method="name"):
        '''
        Set _muxed_pos_list list automatically.

        :param method:
        :return: INT - Number of created connections.
        '''
        pos_a = []
        pos_b = []
        for po_obj in self._mig_a.get_iter_pos():
            po_info = (po_obj[0], po_obj[1], po_obj[2], self._mig_a.get_name_by_po_if_has(po_obj[0]))
            pos_a.append(po_info)
        for po_obj in self._mig_b.get_iter_pos():
            po_info = (po_obj[0], po_obj[1], po_obj[2], self._mig_b.get_name_by_po_if_has(po_obj[0]))
            pos_b.append(po_info)
        # Elements in pos_a & pos_b: (id, fanin, type, name)

        if method == "name":
            self._muxed_pos_list = []
            log_list = []
            for a_i in pos_a:
                for b_i in pos_b:
                    if a_i[3] == b_i[3]:
                        self._muxed_pos_list.append((a_i[0], b_i[0]))
                        # pos_a.remove(a_i)
                        pos_b.remove(b_i)
                        log_list.append("Name:{}, ID in A:{}, ID in B:{}.".format(a_i[3], a_i[0], b_i[0]))
            print("Set muxed POs by name - Finished! Number:{}".format(len(log_list)))
            for info in log_list:
                print(info)
            return len(log_list)

    def set_merged_pis_auto(self, method="name"):
        '''
        Set _merged_pis_list list automatically.

        :param method:
        :return: INT - Number of created connections.
        '''

        if method == "name":
            pis_named_a = []
            pis_named_b = []
            for pi_l in self._mig_a.get_iter_pis():
                if self._mig_a.has_name(pi_l):
                    pis_named_a.append((pi_l, self._mig_a.get_name_by_id(pi_l)))
            for pi_l in self._mig_b.get_iter_pis():
                if self._mig_b.has_name(pi_l):
                    pis_named_b.append((pi_l, self._mig_b.get_name_by_id(pi_l)))

            self._merged_pis_list = []
            log_list = []
            for a_i in pis_named_a:
                for b_i in pis_named_b:
                    if a_i[1] == b_i[1]:
                        self._merged_pis_list.append((a_i[0], b_i[0]))
                        # pis_named_a.remove(a_i)
                        pis_named_b.remove(b_i)
                        log_list.append("Name:{}, Literal in A:{}, Literal in B:{}.".format(a_i[1], a_i[0], b_i[0]))
            print("Set merged PIs by name - Finished! Number: {} ".format(len(log_list)))
            for info in log_list:
                print(info)
            return len(log_list)

    def muxed_pos_list_get(self):
        '''
        Return list(self._muxed_pos_list)

        :return:
        '''
        return list(self._muxed_pos_list)

    def merged_pis_list_get(self):
        '''
        Return list(self._merged_pis_list)

        :return:
        '''
        return list(self._merged_pis_list)

    def muxed_pos_list_add(self, t):
        '''
        Add new items to self._muxed_pos_list list.

        :param t: TUPLE or LIST - Containing tuples with 2 PO IDs.
        :return: LIST - New self._mux_fanin list
        '''
        # assert isinstance(t, tuple)
        for i in t:
            assert isinstance(i, tuple)
            assert len(i) == 2
            assert i not in self._muxed_pos_list
            self._muxed_pos_list.append(i)
        return self.muxed_pos_list_get()

    def merged_pis_list_add(self, t):
        '''
        Add new items to self._merged_pis list.

        :param t: TUPLE or LIST - Containing tuples with 2 PI literals.
        :return: LIST - New self._merged_pis list
        '''
        # assert isinstance(t, tuple)
        for i in t:
            assert isinstance(i, tuple)
            assert len(i) == 2
            assert not i in self._merged_pis_list
            self._merged_pis_list.append(i)
        return self.merged_pis_list_get()

    def muxed_pos_list_remove(self, t):
        for i in t:
            assert isinstance(i, tuple)
            assert len(i) == 2
            if i in self._muxed_pos_list:
                self._muxed_pos_list.remove(i)
        return self.muxed_pos_list_get()

    def merged_pis_list_remove(self, t):
        for i in t:
            assert isinstance(i, tuple)
            assert len(i) == 2
            if i in self._merged_pis_list:
                self._merged_pis_list.remove(i)
        return self.merged_pis_list_get()


####### 合并
    def pmig_generation(self, obsolete_muxed_pos = False):
        assert isinstance(self._mig_a, PMIG)
        assert isinstance(self._mig_b, PMIG)

        # Checks
        for ii_a, ii_b in self._muxed_pos_list:
            assert 0 <= ii_a < self._mig_a.n_pos()
            assert 0 <= ii_b < self._mig_b.n_pos()
        for ii_a, ii_b in self._merged_pis_list:
            assert PMIG.is_noattribute_literal(ii_a)
            assert PMIG.is_noattribute_literal(ii_b)
            assert self._mig_a.is_pi(ii_a)
            assert self._mig_b.is_pi(ii_b)

        pmig_new = PMIG(polymorphic_type=self._ptype)

        # Initialize Literal_Mapping obj
        LMap = Literal_Mapping()
        LMap.add_pi_merge_rules(merge_list=self._merged_pis_list)

        # Nodes of subgraph A
        for l_i in self._mig_a.get_iter_nodes_all():
            if self._mig_a.has_name(f=l_i):
                nnew_name = self._mig_a.get_name_by_id(f=l_i)
            else:
                nnew_name = None


            if self._mig_a.is_const0(f=l_i):
                assert l_i == self._mig_a.get_literal_const0()

            elif self._mig_a.is_pi(f=l_i):
                if nnew_name is not None:
                    nnew_name = 'APi-' + nnew_name
                nnew_l = pmig_new.create_pi(name=nnew_name)
                LMap.map_to_new_literal(l_original=l_i, l_new=nnew_l, subgraph='A')

            elif self._mig_a.is_maj(f=l_i):
                old_ch0 = self._mig_a.get_maj_child0(f=l_i)
                old_ch1 = self._mig_a.get_maj_child1(f=l_i)
                old_ch2 = self._mig_a.get_maj_child2(f=l_i)
                nnew_ch0 = LMap.get_new_literal(l_original=old_ch0, subgraph='A')
                nnew_ch1 = LMap.get_new_literal(l_original=old_ch1, subgraph='A')
                nnew_ch2 = LMap.get_new_literal(l_original=old_ch2, subgraph='A')
                nnew_l = pmig_new.create_maj(child0=nnew_ch0, child1=nnew_ch1, child2=nnew_ch2)
                if nnew_name is not None:
                    nnew_name = 'AMaj-' + nnew_name
                    pmig_new.set_name(f=nnew_l, name=nnew_name)
                LMap.map_to_new_literal(l_original=l_i, l_new=nnew_l, subgraph='A')

            elif self._mig_a.is_latch(f=l_i):
                assert False

            else:
                assert False

        # Nodes of subgraph B
        for l_i in self._mig_b.get_iter_nodes_all():
            if self._mig_b.has_name(f=l_i):
                nnew_name = self._mig_b.get_name_by_id(f=l_i)
            else:
                nnew_name = None


            if self._mig_b.is_const0(f=l_i):
                assert l_i == self._mig_b.get_literal_const0()

            elif self._mig_b.is_pi(f=l_i):
                if nnew_name is not None:
                    nnew_name = 'BPi-' + nnew_name
                if LMap.if_BPi_merged_to_APi(pi_b=l_i):
                    nnew_l = LMap.apply_pi_merge(pi_b=l_i)
                else:
                    nnew_l = pmig_new.create_pi(name=nnew_name)
                    LMap.map_to_new_literal(l_original=l_i, l_new=nnew_l, subgraph='B')

            elif self._mig_b.is_maj(f=l_i):
                old_ch0 = self._mig_b.get_maj_child0(f=l_i)
                old_ch1 = self._mig_b.get_maj_child1(f=l_i)
                old_ch2 = self._mig_b.get_maj_child2(f=l_i)
                nnew_ch0 = LMap.get_new_literal(l_original=old_ch0, subgraph='B')
                nnew_ch1 = LMap.get_new_literal(l_original=old_ch1, subgraph='B')
                nnew_ch2 = LMap.get_new_literal(l_original=old_ch2, subgraph='B')
                nnew_l = pmig_new.create_maj(child0=nnew_ch0, child1=nnew_ch1, child2=nnew_ch2)
                if nnew_name is not None:
                    nnew_name = 'BMaj-' + nnew_name
                    pmig_new.set_name(f=nnew_l, name=nnew_name)
                LMap.map_to_new_literal(l_original=l_i, l_new=nnew_l, subgraph='B')

            elif self._mig_b.is_latch(f=l_i):
                assert False

            else:
                assert False

        # POs of A
        Dict_APO_id_map = {}
        for po_id, po_fanin, po_type in self._mig_a.get_iter_pos():
            newpo_fanin = LMap.get_new_literal(l_original=po_fanin, subgraph='A')
            newpo_type = po_type
            newpo_name = "APo-" + self._mig_a.get_name_by_po_if_has(po=po_id)
            po_id_new = pmig_new.create_po(f=newpo_fanin, name=newpo_name, po_type=newpo_type)
            Dict_APO_id_map[po_id] = po_id_new

        # POs of B
        Dict_BPO_id_map = {}
        for po_id, po_fanin, po_type in self._mig_b.get_iter_pos():
            newpo_fanin = LMap.get_new_literal(l_original=po_fanin, subgraph='B')
            newpo_type = po_type
            newpo_name = "BPo-" + self._mig_b.get_name_by_po_if_has(po=po_id)
            po_id_new = pmig_new.create_po(f=newpo_fanin, name=newpo_name, po_type=newpo_type)
            Dict_BPO_id_map[po_id] = po_id_new

        # Muxed POs
        cnt_for_new_po_name = 0
        if 'ctl' in self._pmux_literals:
            ctl_newl = pmig_new.create_pi(name='PMUX_ctl')
        for fanin_a_id, fanin_b_id in self._muxed_pos_list:
            fanin_a_l = self._mig_a.get_po_fanin(po=fanin_a_id)
            fanin_b_l = self._mig_b.get_po_fanin(po=fanin_b_id)
            tobemuxed_in_a = LMap.get_new_literal(l_original=fanin_a_l, subgraph='A')
            tobemuxed_in_b = LMap.get_new_literal(l_original=fanin_b_l, subgraph='B')

            MMap = MuxMap()
            MMap.add_map(l_mux=PMIG.get_literal_const0(), l_new=PMIG.get_literal_const0())
            mux_in_a = self._pmux_literals['fanin_A']
            mux_in_b = self._pmux_literals['fanin_B']
            MMap.add_map(l_mux=mux_in_a, l_new=tobemuxed_in_a)
            MMap.add_map(l_mux=mux_in_b, l_new=tobemuxed_in_b)
            if 'ctl' in self._pmux_literals:
                ctl_oldl = self._pmux_literals['ctl']
                MMap.add_map(l_mux=ctl_oldl, l_new=ctl_newl)

            assert isinstance(self._pmux, PMIG)
            for mux_n_l in self._pmux.get_iter_nodes_all():
                if self._pmux.is_const0(f=mux_n_l):
                    assert mux_n_l == PMIG.get_literal_const0()
                elif self._pmux.is_pi(f=mux_n_l):
                    # print("################ {}, {}, {}".format(mux_n_l, mux_in_a, mux_in_b))
                    if 'ctl' in self._pmux_literals:
                        assert (mux_n_l == mux_in_a) or (mux_n_l == mux_in_b) or (mux_n_l == ctl_oldl)
                    else:
                        assert (mux_n_l == mux_in_a) or (mux_n_l == mux_in_b)

                elif self._pmux.is_maj(f=mux_n_l):
                    mux_maj_ch0 = self._pmux.get_maj_child0(f=mux_n_l)
                    mux_maj_ch1 = self._pmux.get_maj_child1(f=mux_n_l)
                    mux_maj_ch2 = self._pmux.get_maj_child2(f=mux_n_l)
                    new_maj_ch0 = MMap.get_new_l(l_mux=mux_maj_ch0)
                    new_maj_ch1 = MMap.get_new_l(l_mux=mux_maj_ch1)
                    new_maj_ch2 = MMap.get_new_l(l_mux=mux_maj_ch2)
                    new_maj_l = pmig_new.create_maj(child0=new_maj_ch0, child1=new_maj_ch1, child2=new_maj_ch2)
                    MMap.add_map(l_mux=mux_n_l, l_new=new_maj_l)
                else:
                    assert False

            if obsolete_muxed_pos:
                for po_id_new_temp in (Dict_APO_id_map[fanin_a_id], Dict_BPO_id_map[fanin_b_id]):
                    pmig_new.set_po_type(po=po_id_new_temp, po_type=PMIG.PO_OBSOLETE)

            mux_po_old_fanin = self._pmux_literals['po']
            mux_po_new_fanin = MMap.get_new_l(l_mux=mux_po_old_fanin)
            mux_po_new_name = "MUXPO-{}".format(cnt_for_new_po_name)
            pmig_new.create_po(f=mux_po_new_fanin, name=mux_po_new_name)
            cnt_for_new_po_name = cnt_for_new_po_name + 1

        # Apply
        self._pmig_generated = copy.deepcopy(pmig_new)
        self._pmig_generated_modified = copy.deepcopy(pmig_new)
        self._pmig_generated_modified = self._pmig_generated_modified.pmig_clean_pos_by_type(po_type_tuple=(graphs.PMIG.PO_OBSOLETE,))

        # Save logs
        self._log_PO_id_map = (copy.deepcopy(Dict_APO_id_map), copy.deepcopy(Dict_BPO_id_map))
        self._log_Literal_map = copy.deepcopy(LMap)


    def get_generated_pmig(self):
        return copy.deepcopy(self._pmig_generated)

    def get_generated_pmig_modified(self):
        return copy.deepcopy(self._pmig_generated_modified)


########################################################################################################################
# class PMIG_Gen_Comb_2to1_PEdge
#
# @Time    : 2021/09
# @Author  : c
#
# 将2个非多态图通过pmux合并为具有多态edge的多态图
# 多态edge是指edge允许具有多态属性
#
########################################################################################################################
class PMIG_Gen_Comb_2to1_PEdge(_Base_PMIG_Gen_Comb_2to1):
    def __init__(self):
        super().__init__()

    def initialization(self, mig1, mig2):
        self._ptype = PMIG.PTYPE_ALL

        assert isinstance(mig1, PMIG)
        assert isinstance(mig2, PMIG)

        self._mig_a = copy.deepcopy(mig1)
        self._mig_b = copy.deepcopy(mig2)
        self._pmux, self._pmux_literals = self.get_pmux()

        assert self.input_mig_checks(mig_obj=self._mig_a)
        assert self.input_mig_checks(mig_obj=self._mig_b)

        self._merged_pis_list = []
        self._muxed_pos_list = []
        self._pmig_generated = PMIG(polymorphic_type=self._ptype)
        self._pmig_generated_modified = PMIG(polymorphic_type=self._ptype)

        self._log_PO_id_map = None
        self._log_Literal_map = None

    def get_pmux(self):
        '''
        Get a PMIG obj of a 2 to 1 MUX with polymorphic edges, with 2 PIs: "in_a", "in_b" , and a 1 output: "mux_PO".

        :return: PMIG_obj, DICT - The PMIG of 2 to 1 MUX, and a dict.
        '''
        pmux = PMIG(polymorphic_type=self._ptype)
        literal_a = pmux.create_pi(name='in_a')
        literal_b = pmux.create_pi(name='in_b')
        literal_ac = pmux.create_maj(literal_a, pmux.get_literal_const0(), pmux.get_literal_const_1_0())  # M(a, 0, 1/0)
        literal_bc = pmux.create_maj(literal_b, pmux.get_literal_const0(), pmux.get_literal_const_0_1())  # M(b, 0, 0/1)
        literal_abc = pmux.create_maj(literal_ac, literal_bc,
                                      pmux.get_literal_const1())  # M( M(a, 0, 1/0), M(b, 0, 0/1), 1)
        pmux.create_po(literal_abc, name="mux_PO")
        return pmux, {'fanin_A': literal_a, 'fanin_B': literal_b, 'po':literal_abc}













########################################################################################################################
# class PMIG_Gen_Comb_2to1_PNode
#
# @Time    : 2021/09
# @Author  : c
#
# 将2个非多态图通过pmux合并为具有多态node的多态图
# 多态node是指edge不允许具有多态属性，但是会有一个代表多态的PI
#
# todo: 尚未完成！
#
########################################################################################################################
class PMIG_Gen_Comb_2to1_PNode(_Base_PMIG_Gen_Comb_2to1):
    def __init__(self):
        super().__init__()

    def initialization(self, mig1, mig2):
        self._ptype = PMIG.PTYPE_NO

        assert isinstance(mig1, PMIG)
        assert isinstance(mig2, PMIG)

        self._mig_a = copy.deepcopy(mig1)
        self._mig_b = copy.deepcopy(mig2)
        self._pmux, self._pmux_literals = self.get_pmux()

        assert self.input_mig_checks(mig_obj=self._mig_a)
        assert self.input_mig_checks(mig_obj=self._mig_b)

        self._merged_pis_list = []
        self._muxed_pos_list = []
        self._pmig_generated = PMIG(polymorphic_type=self._ptype)
        self._pmig_generated_modified = PMIG(polymorphic_type=self._ptype)

        self._log_PO_id_map = None
        self._log_Literal_map = None

        # self._list_majs_with_const_fanin_in_1 =
        # self._list_majs_with_const_fanin_in_2 =

    # def _get_list_majs_with_const_fanin(self, pmig_obj):
    #     '''
    #     获取一个PMIG中以const作为扇入的的MAJ的信息。注意：本方法会检查MAJ是否可消除。若
    #
    #     :param pmig_obj:
    #     :return:
    #     '''
    #     assert isinstance(pmig_obj, PMIG)
    #     for ii_maj in pmig_obj.get_iter_majs():


    def get_pmux(self):
        '''
        Get a PMIG obj of a 2 to 1 MUX, with 3 PIs: "in_a", "in_b" and "ctl"(select signal), and a 1 output: "mux_PO".

        :return: PMIG_obj, DICT - The PMIG of 2 to 1 MUX, and a dict.
        '''
        pmux = PMIG(polymorphic_type=self._ptype)
        literal_a = pmux.create_pi(name='in_a')
        literal_b = pmux.create_pi(name='in_b')
        literal_c = pmux.create_pi(name='ctl')
        literal_ac = pmux.create_maj(literal_a, literal_c, pmux.get_literal_const0())  # M(a, c, 0)
        literal_bc = pmux.create_maj(literal_b, pmux.negate_literal_if(literal_c, True),
                                     pmux.get_literal_const0())  # M(b, c', 0)
        literal_abc = pmux.create_maj(literal_ac, literal_bc, pmux.get_literal_const1())  # M( M(a,c,0), M(b, c', 0), 1)
        pmux.create_po(literal_abc, name="mux_PO")
        return pmux, {'fanin_A': literal_a, 'fanin_B': literal_b, 'ctl': literal_c, 'po':literal_abc}

    