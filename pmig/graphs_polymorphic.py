# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/6/22
# @Author  : c
# @File    : graphs_polymorphic.py
#

from pmig import graphs
# AIG = graphs.AIG # alias
PMIG = graphs.PMIG # alias

from prettytable import PrettyTable
import copy


class Literal_Map:
    '''
    这个类是为了在使用mux合并两个PMIG图时，存储nodes的新旧literal映射关系
    '''
    def __init__(self):
        self._nodemap_A_to_new = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
        self._nodemap_new_to_A = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
        self._nodemap_B_to_new = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
        self._nodemap_new_to_B = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
        self._node_id_A = 1
        self._node_id_B = 1
        self._merge_pi_A_to_B = {}
        self._merge_pi_B_to_A = {}

    def reset_all(self):
        self._nodemap_A_to_new = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
        self._nodemap_new_to_A = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
        self._nodemap_B_to_new = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
        self._nodemap_new_to_B = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
        self._node_id_A = 1
        self._node_id_B = 1
        self._merge_pi_A_to_B = {}
        self._merge_pi_B_to_A = {}

    def add_A_mapping(self, literal_A, literal_new):
        l_A = PMIG.get_positive_normal_literal(literal_A)
        l_new = PMIG.get_positive_normal_literal(literal_new)
        # assert l_new == self._node_id_A << 2
        assert l_A not in self._nodemap_A_to_new
        assert l_new not in self._nodemap_new_to_A
        self._nodemap_A_to_new[l_A] = l_new
        self._nodemap_new_to_A[l_new] = l_A
        self._node_id_A = self._node_id_A + 1

    def add_B_mapping(self, literal_B, literal_new):
        l_B = PMIG.get_positive_normal_literal(literal_B)
        l_new = PMIG.get_positive_normal_literal(literal_new)
        # assert l_new == (self._node_id_B + len(self._nodemap_A_to_new) - 1) << 2
        assert l_B not in self._nodemap_B_to_new
        assert l_new not in self._nodemap_new_to_B
        self._nodemap_B_to_new[l_B] = l_new
        self._nodemap_new_to_B[l_new] = l_B
        self._node_id_B = self._node_id_B + 1

    def add_new_mapping(self, literal_original, literal_new, subgraph):
        if subgraph == 'A':
            self.add_A_mapping(literal_original, literal_new)
        elif subgraph == 'B':
            self.add_B_mapping(literal_original, literal_new)
        else:
            assert False

    def get_new_literal(self, literal_original, subgraph):
        l_original = PMIG.get_positive_normal_literal(literal_original)
        # assert subgraph in ('A', 'B')
        if subgraph == 'A':
            assert l_original in self._nodemap_A_to_new
            l_new = self._nodemap_A_to_new[l_original]
            return PMIG.add_attr_if_has_attr(l_new, literal_original)
        elif subgraph == 'B':
            assert l_original in self._nodemap_B_to_new
            l_new = self._nodemap_B_to_new[l_original]
            return PMIG.add_attr_if_has_attr(l_new, literal_original)
        else:
            assert False

    def init_pi_merger_dict(self, merger_list):
        '''
        Load PI merge list

        :param merger_list:
        :return:
        '''
        for pi_a, pi_b in merger_list:
            self._merge_pi_A_to_B[pi_a] = (pi_b, False)
            self._merge_pi_B_to_A[pi_b] = (pi_a, False)

    def get_pi_merge_info(self, pi_l, subgraph):
        '''
        Query if a PI of mig A or B is in the merge list.

        :param pi_l: INT - Literal of a PI in A or B
        :param subgraph: STRING - 'A' or 'B'
        :return: Bool, Tuple - If the PI is in the merge list, then return True and (another PI, if defined). If not, return False and None.
        '''
        if subgraph == 'A':
            if pi_l in self._merge_pi_A_to_B:
                return True, self._merge_pi_A_to_B[pi_l]
            else:
                return False, None
        elif subgraph == 'B':
            if pi_l in self._merge_pi_B_to_A:
                return True, self._merge_pi_B_to_A[pi_l]
            else:
                return False, None
        else:
            assert False

    def active_pi_merge(self, pi_l, new_l, subgraph):
        '''
        If a pair of PIs in the merge dict is defined in PMIG, then this function must be called to complete the merger process.

        :param pi_l: INT - The literal of PI in mig A or B
        :param new_l: INT - The new literal of PI
        :param subgraph: String - 'A' or 'B'
        :return:
        '''
        if subgraph == 'A':
            assert pi_l in self._merge_pi_A_to_B
            pi_ll, flag = self._merge_pi_A_to_B[pi_l]
            assert not flag
            self._merge_pi_A_to_B[pi_l] = (pi_ll, True)
            self._merge_pi_B_to_A[pi_ll] = (pi_l, True)
            self.add_A_mapping(literal_A=pi_l, literal_new=new_l)
            self.add_B_mapping(literal_B=pi_ll, literal_new=new_l)
        elif subgraph == 'B':
            assert pi_l in self._merge_pi_B_to_A
            pi_ll, flag = self._merge_pi_B_to_A[pi_l]
            assert not flag
            self._merge_pi_B_to_A[pi_l] = (pi_ll, True)
            self._merge_pi_A_to_B[pi_ll] = (pi_l, True)
            self.add_B_mapping(literal_B=pi_l, literal_new=new_l)
            self.add_A_mapping(literal_A=pi_ll, literal_new=new_l)
        else:
            assert False

class Cut_Mapping:
    '''
    这个类是为了存储n-cut与原图之间的nodes映射关系
    '''
    def __init__(self):
        self._nodes_mapping = {} # 原图中的nodes literal（无属性）：cut图中的nodes literal（无属性）

    def add_nodes_mapping(self, l_old, l_new):
        assert not PMIG.is_negated_literal(l_old)
        assert not PMIG.is_polymorphic_literal(l_old)
        assert not PMIG.is_negated_literal(l_new)
        assert not PMIG.is_polymorphic_literal(l_new)
        assert l_old not in self._nodes_mapping
        self._nodes_mapping[l_old] = l_new

    def get_new_literal(self, l_old):
        l_old_noattr = PMIG.get_positive_normal_literal(f=l_old)
        assert l_old_noattr in self._nodes_mapping
        l_new_noattr = self._nodes_mapping[l_old_noattr]
        l_new = PMIG.add_attr_if_has_attr(f=l_new_noattr, c=l_old)
        return l_new


class PMIG_Generation_combinational:
    # 注意：不允许存在buffer与latch
    def __init__(self, mig1, mig2):
        assert isinstance(mig1, PMIG)
        assert isinstance(mig2, PMIG)
        assert not self.is_polymorphic_mig(mig1), "[ERROR]graphs_polymorphic: The input PMIG (mig1) cannot be polymorphic!"
        assert not self.is_polymorphic_mig(mig2), "[ERROR]graphs_polymorphic: The input PMIG (mig2) cannot be polymorphic!"
        assert self.is_combinational_mig(mig1)
        assert self.is_combinational_mig(mig2)
        assert not self.is_mig_with_buffer(mig1)
        assert not self.is_mig_with_buffer(mig2)
        self._mig_a = mig1 # The PMIG obj of function A
        self._mig_b = mig2 # The PMIG obj of function B
        self._pmux, self._pmux_literals = self.get_pmux() # The PMIG obj of MUX, and the dict literals.
                                                          # Example of self._pmux_literals:
                                                          # {'fanin_A':literal_a, 'fanin_B':literal_b, 'ctl':literal_c, 'PI':None}

        self._mux_fanins = [] # A list with tuple elements.
                             # Each tuple contains 2 literals, which are the literals of a PO literal of mig_a and the corresponding PO of mig_b.
                             # The two PO will be connected with a pmux.
        self._merged_pis = [] # A list with tuple elements.
                             # Each tuple contains 2 literals, which are the literals of a PI to be merged.
        self._conversion_map = Literal_Map()

    def is_polymorphic_mig(self, mig_obj):
        '''
        Return True if mig_obj is a PMIG with polymorphic nodes or polymorphic edges.

        :param mig_obj: PMIG obj
        :return: Boolean
        '''
        assert isinstance(mig_obj, PMIG)
        for i in mig_obj.get_iter_nodes_with_polymorphic_pi():
            return True
        for i in mig_obj.get_iter_nodes_with_polymorphic_edge():
            return True
        for po_i in mig_obj.get_iter_pos_with_polymorphic_fanin():
            return True
        return False

    def is_combinational_mig(self, mig_obj):
        '''
        Return True if mig_obj has no LATCH-TYPE node.


        :param mig_obj:
        :return:
        '''
        assert isinstance(mig_obj, PMIG)
        for i in mig_obj.get_iter_latches():
            return False
        return True

    def is_mig_with_buffer(self, mig_obj):
        '''
        Return True if mig_obj has BUFFER-TYPE node.

        :param mig_obj:
        :return:
        '''

        assert isinstance(mig_obj, PMIG)
        for i in mig_obj.get_iter_buffers():
            return True
        return False

    # def get_pmux(self):
    #     '''
    #     It should be defined in sub-class!
    #
    #     :return:
    #     '''
    #     # Assert False, "[ERROR] graphs_polymorphic: PMIG_Generation_combinational.get_pmux() should not be called! It should be defined in sub-class."
    #     return PMIG(), None

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
                info_a = (self._mig_a.get_po_fanin(po_i), self._mig_a.get_name_by_po_if_has(po_i), self._mig_a.get_po_type(po_i))
            else:
                info_a = ("N/A", "N/A", "N/A")
            if po_i < self._mig_b.n_pos():
                info_b =(self._mig_b.get_po_fanin(po_i), self._mig_b.get_name_by_po_if_has(po_i), self._mig_b.get_po_type(po_i))
            else:
                info_b = ("N/A", "N/A", "N/A")
            assert not ("N/A" in info_a and "N/A" in info_b)
            po_table.add_row( [ po_i, info_a[0], info_a[1], info_a[2],' ' , po_i, info_b[0], info_b[1], info_b[2] ] )
        print(po_table)
        print("Type: PO_OUTPUT = 0, PO_UNDEFINED = 1, PO_JUSTICE = 2")

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

    def set_mux_fanins(self, fanin_list = None):
        '''
        Set self._mux_fanins list. If fanin_list == None, then the first min(_mig_b.n_pis(), __mig_a.n_pis()) POs will be added to the list.

        :param fanin_list:
        :return:
        '''
        if fanin_list is None:
            n_pos_min = self._mig_a.n_pos()
            if self._mig_b.n_pos() < self._mig_a.n_pos():
                n_pos_min = self._mig_b.n_pos()
            fanin_list = []
            for i in range(0, n_pos_min):
                fanin_list.append( (i, i) )

        self._mux_fanins = fanin_list

    def set_merged_pis(self, pi_list = None):
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
                pi_list.append( (self._mig_a.get_pi_by_id(i), self._mig_b.get_pi_by_id(i)) )

        self._merged_pis = pi_list

    def set_mux_auto(self, method = "name"):
        '''
        Set _mux_fanin list automatically.

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
            self._mux_fanins = []
            log_list = []
            for a_i in pos_a:
                for b_i in pos_b:
                    if a_i[3] == b_i[3]:
                        self._mux_fanins.append( (a_i[0], b_i[0]) )
                        #pos_a.remove(a_i)
                        pos_b.remove(b_i)
                        log_list.append( "Name:{}, ID in A:{}, ID in B:{}.".format(a_i[3], a_i[0], b_i[0]) )
            print("Finished! {} connection created!".format(len(log_list)))
            for info in log_list:
                print(info)
            return len(log_list)

    def set_merged_pis_auto(self, method = "name"):
        '''
        Set _merged_pis list automatically.

        :param method:
        :return: INT - Number of created connections.
        '''

        if method == "name":
            pis_named_a = []
            pis_named_b = []
            for pi_l in self._mig_a.get_iter_pis():
                if self._mig_a.has_name(pi_l):
                    pis_named_a.append( (pi_l, self._mig_a.get_name_by_id(pi_l)) )
            for pi_l in self._mig_b.get_iter_pis():
                if self._mig_b.has_name(pi_l):
                    pis_named_b.append( (pi_l, self._mig_b.get_name_by_id(pi_l)) )

            self._merged_pis = []
            log_list = []
            for a_i in pis_named_a:
                for b_i in pis_named_b:
                    if a_i[1] == b_i[1]:
                        self._merged_pis.append( (a_i[0], b_i[0]) )
                        #pis_named_a.remove(a_i)
                        pis_named_b.remove(b_i)
                        log_list.append( "Name:{}, Literal in A:{}, Literal in B:{}.".format(a_i[1], a_i[0], b_i[0]) )
            print("Finished! {} connection created!".format(len(log_list)))
            for info in log_list:
                print(info)
            return len(log_list)

    def mux_fanin_list_get(self):
        '''
        Return list(self._mux_fanins)

        :return:
        '''
        return list(self._mux_fanins)

    def merged_pis_list_get(self):
        '''
        Return list(self._merged_pis)

        :return:
        '''
        return list(self._merged_pis)

    def mux_fanin_list_add(self, t):
        '''
        Add new items to self._mux_fanin list.

        :param t: TUPLE or LIST - Containing tuples with 2 PO IDs.
        :return: LIST - New self._mux_fanin list
        '''
        # assert isinstance(t, tuple)
        for i in t:
            assert isinstance(i, tuple)
            assert len(i) == 2
            assert not i in self._mux_fanins
            self._mux_fanins.append(i)
        return self.mux_fanin_list_get()

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
            assert not i in self._merged_pis
            self._merged_pis.append(i)
        return self.merged_pis_list_get()

    def mux_fanin_list_remove(self, t):
        for i in t:
            assert isinstance(i, tuple)
            assert len(i) == 2
            if i in self._mux_fanins:
                self._mux_fanins.remove(i)
        return self.mux_fanin_list_get()

    def merged_pis_list_remove(self, t):
        for i in t:
            assert isinstance(i, tuple)
            assert len(i) == 2
            if i in self._merged_pis:
                self._merged_pis.remove(i)
        return self.merged_pis_list_get()

    def _convert_nodes_to_new(self, mig_obj, subgraph):
        assert isinstance(mig_obj, PMIG)
        assert isinstance(self._pmig_generated, PMIG)
        assert subgraph in ('A', 'B')
        # Nodes
        for l in mig_obj.get_iter_nodes_all():
            if mig_obj.has_name(l):
                new_name = subgraph+'-'+mig_obj.get_name_by_id(l)
                original_name = mig_obj.get_name_by_id(l)
            else:
                new_name = None
                original_name = None

            if mig_obj.is_const0(l):
                assert l == mig_obj.get_literal_const0()

            elif mig_obj.is_pi(l):
                merge_if, merge_info = self._conversion_map.get_pi_merge_info(pi_l=l, subgraph=subgraph)
                if merge_if:
                    if merge_info[1]:
                        pass
                    else:
                        if subgraph == 'A':
                            new_name ="M-A{}B{}".format(l, merge_info[0])
                        elif subgraph == 'B':
                            new_name = "M-A{}B{}".format(merge_info[0], l)
                        new_l = self._pmig_generated.create_pi(name=new_name)
                        self._conversion_map.active_pi_merge(pi_l=l, new_l=new_l, subgraph=subgraph)

                else:
                    new_l = self._pmig_generated.create_pi(name=new_name)
                    self._conversion_map.add_new_mapping(l, new_l, subgraph)

            elif mig_obj.is_maj(l):
                ch0 = mig_obj.get_maj_child0(l)
                ch1 = mig_obj.get_maj_child1(l)
                ch2 = mig_obj.get_maj_child2(l)
                new_ch0 = self._conversion_map.get_new_literal(ch0, subgraph)
                new_ch1 = self._conversion_map.get_new_literal(ch1, subgraph)
                new_ch2 = self._conversion_map.get_new_literal(ch2, subgraph)
                new_l = self._pmig_generated.create_maj(child0=new_ch0,child1=new_ch1,child2=new_ch2)
                self._conversion_map.add_new_mapping(l, new_l, subgraph)

            elif mig_obj.is_latch(l):
                assert False
                l_init = mig_obj.get_latch_init(l)
                l_next = mig_obj.get_latch_next(l)
                new_init = self._conversion_map.get_new_literal(l_init, subgraph)
                new_next = self._conversion_map.get_new_literal(l_next, subgraph)
                new_l = self._pmig_generated.create_latch(name=new_name, init=new_init, next=new_next)
                self._conversion_map.add_new_mapping(l, new_l, subgraph)

            elif mig_obj.is_buffer(l):
                assert False
                buf_in = mig_obj.get_buffer_in(l)
                new_in = self._conversion_map.get_new_literal(buf_in, subgraph)
                new_l = self._pmig_generated.create_buffer(buf_in=new_in, name=new_name)
                self._conversion_map.add_new_mapping(l, new_l, subgraph)

            else:
                assert False

    def _convert_pos_to_new(self, mig_obj, subgraph):
        assert isinstance(mig_obj, PMIG)
        assert subgraph in ('A', 'B')
        assert isinstance(self._pmig_generated, PMIG)
        for po_id, po_fanin, po_type in mig_obj.get_iter_pos():
            new_name = subgraph + '-' + mig_obj.get_name_by_po_if_has(po_id)
            new_fanin = self._conversion_map.get_new_literal(po_fanin, subgraph)
            new_type = po_type
            self._pmig_generated.create_po(f=new_fanin, name=new_name, po_type=new_type)

    def _create_mux(self, fanin_a, fanin_b, obsolete_muxed_pos = False, ctl_mapping = 'PI', ctl_pi_literal = None):
        '''
        注意： 若self._pmux_literals中存在‘ctl’项，那么将其映射为PI(ctl_mapping = 'PI',默认)或0/1(ctl_mapping = 'CONST')。若不存在，则不映射。

        :param fanin_a:
        :param fanin_b:
        :param obsolete_muxed_pos:
        :return:
        '''
        assert isinstance(self._pmig_generated, PMIG)
        assert isinstance(self._pmux, PMIG)
        new_ctl_pi_literal = None
        map_mux_to_new = {self._pmux.get_literal_const0(): self._pmig_generated.get_literal_const0()}
        l_mux_a = self._pmux_literals['fanin_A']
        l_mux_b = self._pmux_literals['fanin_B']
        if 'ctl' in self._pmux_literals:
            l_ctl = self._pmux_literals['ctl']
        else:
            l_ctl = None
        l_pis = self._pmux_literals['PI']
        # l_pis_shared = self._pmux_literals['shared_PI']
        if l_pis is not None:
            for l_pi in l_pis:
                new_l = self._pmig_generated.create_pi()
                map_mux_to_new[l_pi] = new_l
        map_mux_to_new[l_mux_a] = fanin_a
        map_mux_to_new[l_mux_b] = fanin_b
        if l_ctl is not None:
            if ctl_mapping == 'PI':
                if ctl_pi_literal is None:
                    new_ctl_pi_literal = self._pmig_generated.create_pi("polymorphic_ctl_pi")
                    map_mux_to_new[l_ctl] = new_ctl_pi_literal
                else:
                    map_mux_to_new[l_ctl] = ctl_pi_literal
                    new_ctl_pi_literal = ctl_pi_literal
            elif ctl_mapping == 'CONST':
                map_mux_to_new[l_ctl] = self._pmig_generated.get_literal_const_0_1()
            else:
                assert False
        # Nodes
        for l in self._pmux.get_iter_nodes_all():
            if self._pmux.is_const0(l):
                assert l == self._pmux.get_literal_const0()
            elif self._pmux.is_pi(l):
                if l_pis is not None:
                    if l_ctl is None:
                        assert (l in l_pis) or (l in (l_mux_a, l_mux_b))
                    else:
                        assert (l in l_pis) or (l in (l_mux_a, l_mux_b, l_ctl))
                else:
                    if l_ctl is None:
                        assert l in (l_mux_a, l_mux_b, l_ctl)
                    else:
                        assert l in (l_mux_a, l_mux_b, l_ctl)

            elif self._pmux.is_maj(l):
                ch0 = self._pmux.get_maj_child0(l)
                ch1 = self._pmux.get_maj_child1(l)
                ch2 = self._pmux.get_maj_child2(l)
                ch0_normal = self._pmux.negate_literal_if_negated(self._pmux.polymorphic_literal_if_polyedged(ch0, ch0), ch0)
                ch1_normal = self._pmux.negate_literal_if_negated(self._pmux.polymorphic_literal_if_polyedged(ch1, ch1), ch1)
                ch2_normal = self._pmux.negate_literal_if_negated(self._pmux.polymorphic_literal_if_polyedged(ch2, ch2), ch2)
                assert ch0_normal in map_mux_to_new
                new_ch0 = self._pmux.polymorphic_literal_if_polyedged( self._pmux.negate_literal_if_negated(map_mux_to_new[ch0_normal], ch0), ch0 )
                assert ch1_normal in map_mux_to_new
                new_ch1 = self._pmux.polymorphic_literal_if_polyedged( self._pmux.negate_literal_if_negated(map_mux_to_new[ch1_normal], ch1), ch1 )
                assert ch2_normal in map_mux_to_new
                new_ch2 = self._pmux.polymorphic_literal_if_polyedged( self._pmux.negate_literal_if_negated(map_mux_to_new[ch2_normal], ch2), ch2 )
                new_l = self._pmig_generated.create_maj(child0=new_ch0,child1=new_ch1,child2=new_ch2)
                assert not l in map_mux_to_new
                map_mux_to_new[l] = new_l

            elif self._pmux.is_latch(l):
                assert False
                l_init = self._pmux.get_latch_init(l)
                l_next = self._pmux.get_latch_next(l)
                l_init_normal = self._pmux.negate_literal_if_negated(self._pmux.polymorphic_literal_if_polyedged(l_init, l_init), l_init)
                l_next_normal = self._pmux.negate_literal_if_negated(self._pmux.polymorphic_literal_if_polyedged(l_next, l_next), l_next)
                assert l_init_normal in map_mux_to_new
                new_init = self._pmux.polymorphic_literal_if_polyedged( self._pmux.negate_literal_if_negated(map_mux_to_new[l_init_normal], l_init), l_init)
                assert l_next_normal in map_mux_to_new
                new_next = self._pmux.polymorphic_literal_if_polyedged( self._pmux.negate_literal_if_negated(map_mux_to_new[l_next_normal], l_next), l_next)
                new_l = self._pmig_generated.create_latch(init=new_init, next=new_next)
                assert not l in map_mux_to_new
                map_mux_to_new[l] = new_l

            elif self._pmux.is_buffer(l):
                assert False
                buf_in = self._pmux.get_buffer_in(l)
                buf_in_normal = self._pmux.negate_literal_if_negated( self._pmux.polymorphic_literal_if_polyedged(buf_in, buf_in), buf_in)
                assert buf_in_normal in map_mux_to_new
                new_in = self._pmux.polymorphic_literal_if_polyedged( self._pmux.negate_literal_if_negated(map_mux_to_new[buf_in_normal], buf_in), buf_in)
                new_l = self._pmig_generated.create_buffer(buf_in=new_in)
                assert not l in map_mux_to_new
                map_mux_to_new[l] = new_l

            else:
                assert False

        # PO
        po_cnt = 0
        for po_id, po_fanin, po_type in self._pmux.get_iter_pos():
            po_fanin_normal = self._pmux.negate_literal_if_negated( self._pmux.polymorphic_literal_if_polyedged(po_fanin, po_fanin), po_fanin)
            assert po_fanin_normal in map_mux_to_new
            new_fanin = self._pmux.polymorphic_literal_if_polyedged( self._pmux.negate_literal_if_negated(map_mux_to_new[po_fanin_normal], po_fanin), po_fanin)
            new_name = 'MPO-{}_{}_{}'.format(fanin_a, fanin_b, po_cnt)
            po_cnt = po_cnt + 1
            self._pmig_generated.create_po(f=new_fanin, name=new_name, po_type=po_type)

        # Set original POs obsolete
        if obsolete_muxed_pos:
            for original_po_fanin in (fanin_a, fanin_b):
                original_po = self._pmig_generated.get_iter_pos_by_fanin(original_po_fanin)
                cnt_temp = 0
                for po_id, po_fanin, po_type in original_po:
                    print("#####################",po_id, po_fanin, po_type)
                    self._pmig_generated.set_po_obsolete(po_id)
                    cnt_temp = cnt_temp + 1
                # assert cnt_temp <= 2

        return new_ctl_pi_literal



    def pmig_generation(self, obsolete_muxed_pos = False):
        self._conversion_map.reset_all()
        self.reset_pmig()
        self._conversion_map.init_pi_merger_dict(merger_list=self._merged_pis)
        # Nodes
        self._convert_nodes_to_new(mig_obj=self._mig_a, subgraph='A')
        self._convert_nodes_to_new(mig_obj=self._mig_b, subgraph='B')
        # Original POs
        self._convert_pos_to_new(mig_obj=self._mig_a, subgraph='A')
        self._convert_pos_to_new(mig_obj=self._mig_b, subgraph='B')
        # Mux
        ctl_pi_literal = None
        for po_id_a, po_id_b in self._mux_fanins:
            po_in_a = self._mig_a.get_po_fanin(po_id_a)
            po_in_b = self._mig_b.get_po_fanin(po_id_b)
            new_po_in_a = self._conversion_map.get_new_literal(literal_original=po_in_a, subgraph='A')
            new_po_in_b = self._conversion_map.get_new_literal(literal_original=po_in_b, subgraph='B')
            new_ctl_pi_literal = self._create_mux(fanin_a=new_po_in_a, fanin_b=new_po_in_b, obsolete_muxed_pos=obsolete_muxed_pos, ctl_mapping='PI', ctl_pi_literal=ctl_pi_literal)
            ctl_pi_literal = new_ctl_pi_literal

        # Copy to self._pmig_generated_opti
        self._pmig_generated_opti = copy.deepcopy(self._pmig_generated)


    def get_pmig_generated_original(self):
        pmig_obj = copy.deepcopy(self._pmig_generated)
        assert isinstance(pmig_obj, PMIG)
        return pmig_obj

    def get_pmig_generated(self):
        pmig_obj = copy.deepcopy(self._pmig_generated_opti)
        assert isinstance(pmig_obj, PMIG)
        return pmig_obj

# 优化方法opti_xxx，以及优化所需的对生成的图进行操作的方法op_xxx

    def opti_clean_pos_by_type(self, po_type_tuple=(PMIG.PO_OBSOLETE, )):
        assert isinstance(self._pmig_generated_opti, PMIG)
        self._pmig_generated_opti = self._pmig_generated_opti.pmig_clean_pos_by_type(po_type_tuple=po_type_tuple)
        return self._pmig_generated_opti

    def _op_reconvergence_driven_cut_computation(self, root_l, n, stop_list_with_fanout_literals = []):

        def check_inner_nodes(nodeset_leaves, nodeset_visited, nlist):
            if_satisfied = True
            return_literals = []
            worst_literal = None
            worst_n = 0
            # 获得leaves中最大的literal
            leaves_max = 0
            for leaves_i in nodeset_leaves:
                if leaves_i > leaves_max:
                    leaves_max = leaves_i
            # 若一个node的扇出不在visited中，并且literal大于最大的leaves literal， 那么应当加入stop_list
            # 同时，会记录worst node（即不在visited中的fanout的数目最多的node），作为备选。
            for mfn in nlist:
                n = 0
                mfn_l = mfn[0]
                mfn_llist = mfn[1]
                if ( (mfn_l in nodeset_visited) and (mfn_l not in nodeset_leaves) ):
                    for mfn_llist_i in mfn_llist:
                        if mfn_llist_i not in nodeset_visited:
                            if_satisfied = False
                            n = n + 1
                            if ( (mfn_llist_i > leaves_max) and (mfn_l not in return_literals) ):
                                return_literals.append(mfn_l)
                if n > worst_n:
                    worst_literal = mfn_l
                    worst_n = n

            if (not if_satisfied) and (len(return_literals) == 0):
                return_literals.append(worst_literal)

            return if_satisfied, return_literals

        # 将不可包含的点加入stop_list，这些点至少有一个扇出到的node具有比root大的literal
        stop_list_current = []
        for mfn in stop_list_with_fanout_literals:
            i = 0
            mfn_l = mfn[0]
            mfn_llist = mfn[1]
            for ll in mfn_llist:
                if ll > root_l:
                    i = i+1
            if i > 0:
                stop_list_current.append( mfn_l )

        if_satisfied = False
        while (not if_satisfied):
            nodeset_leaves, nodeset_visited = self.op_reconvergence_driven_cut_computation_with_stop_list(root_l=root_l, n=n, stop_list=stop_list_current)
            if_satisfied, additional_stop_nodes = check_inner_nodes(nodeset_leaves=nodeset_leaves, nodeset_visited=nodeset_visited,
                              nlist=stop_list_with_fanout_literals)
            for l_i in additional_stop_nodes:
                stop_list_current.append(l_i)

        return nodeset_leaves, nodeset_visited


    def op_reconvergence_driven_cut_computation_with_stop_list(self, root_l, n, stop_list = []):
        '''
        输入一个root_l（literal)，以及整数n，返回一个以root_l对应的node为root的n割集PMIG对象。
        使用reconvergence-driven cut computation算法。
        注意：stop_list应当包含一些node的literal（无属性），默认为空。
        该列表中的literal所对应的node在本方法中被视为类似于PI，即无扇入。
        该列表的意义是：避免列表中的node被作为一个cut的leaves与root之间的中间node。
        例如，某个node具有多个扇出，因此不希望它作为一个cut的中间node被优化掉，此时就可以借助stop_list。

        :param root_id:
        :param n:
        :return:
        '''

        # 迭代执行，尝试将nodeset_leaves中node的扇入来替换该node作为leaves。每次被替换的node都是非stop的并且具有最低cost的，并且替换必须不能使leaves数目超过限制。
        def construct_cut_rec( nodeset_leaves, nodeset_visited, size_limit, stop_list ):
            def is_stop_node(l):
                if self._pmig_generated_opti.is_pi(l):
                    return True
                if self._pmig_generated_opti.is_const0(l):
                    return True
                if l in stop_list:
                    return True
                return False

            assert isinstance(nodeset_leaves, list)
            assert isinstance(nodeset_visited, list)

            if if_all_nodes_are_stop_nodes(leaves=nodeset_leaves, stop_list=stop_list):
                return nodeset_leaves, nodeset_visited

            min_cost = 10
            node_with_min_cost = None
            for n_i in ( l_nodes for l_nodes in nodeset_leaves if not is_stop_node(l=l_nodes) ):
                cost_i = leaf_cost(node_m=n_i, visited=nodeset_visited)
                if cost_i < min_cost:
                    min_cost = cost_i
                    node_with_min_cost = n_i
            assert (min_cost<10) and (node_with_min_cost is not None)
            if ( len(nodeset_leaves) + min_cost ) > (size_limit + 1):  #  size_limit+1是由于考虑到存在一个CONST0
                return nodeset_leaves, nodeset_visited

            for fanin_i in self._pmig_generated_opti.get_maj_fanins(node_with_min_cost):
                if (PMIG.get_positive_normal_literal(f=fanin_i)) not in nodeset_leaves:
                    nodeset_leaves.append(PMIG.get_positive_normal_literal(f=fanin_i))
            assert node_with_min_cost in nodeset_leaves
            nodeset_leaves.remove(node_with_min_cost)
            assert node_with_min_cost not in nodeset_leaves

            for fanin_i in self._pmig_generated_opti.get_maj_fanins(node_with_min_cost):
                if (PMIG.get_positive_normal_literal(f=fanin_i)) not in nodeset_visited:
                    nodeset_visited.append(PMIG.get_positive_normal_literal(f=fanin_i))

            return construct_cut_rec(nodeset_leaves=nodeset_leaves, nodeset_visited=nodeset_visited, size_limit=size_limit, stop_list=stop_list)

        # 用于检查leaves列表中的nodes是否全部都不可被扇入替代了。这作为迭代的终止条件之一。
        def if_all_nodes_are_stop_nodes(leaves, stop_list):
            def is_stop_node(l):
                if self._pmig_generated_opti.is_pi(l):
                    return True
                if self._pmig_generated_opti.is_const0(l):
                    return True
                if l in stop_list:
                    return True
                return False

            for l in leaves:
                if not is_stop_node(l):
                    return False
            return True

        # cost函数
        def leaf_cost(node_m, visited):
            cost = -1
            # print(node_m)
            for ch_l in self._pmig_generated_opti.get_maj_fanins(node_m):
                if PMIG.get_positive_normal_literal(ch_l) not in visited:
                    cost = cost + 1
            return cost

        # main
        nodeset_leaves = [root_l, PMIG.get_literal_const0()]
        nodeset_visited = [root_l]
        stop_list = tuple(stop_list)
        return construct_cut_rec(nodeset_leaves=nodeset_leaves, nodeset_visited=nodeset_visited, size_limit=n, stop_list=stop_list)

    def op_get_n_cut_with_multifanout_checks(self, root_l, n):
        '''
        获得以root_l(literal)为root的n-cut，并将获得的cut构建一个PMIG用于优化。

        :param root_l: INT - root node的literal
        :param n: INT - leaves数目上限
        :return:
        '''
        cut_computation = self._op_reconvergence_driven_cut_computation
        stop_list = self.op_get_all_nodes_with_multiple_fanouts()
        # Get n-cut
        nodeset_leaves, nodeset_visited = cut_computation(root_l=root_l, n=n, stop_list_with_fanout_literals=stop_list)
        nodeset_cone = self._pmig_generated_opti.get_cone(roots=(root_l,), stop=nodeset_leaves)
        # checks
        for i in nodeset_visited:
            assert (i in nodeset_leaves) or (i in nodeset_cone)
        for i in nodeset_cone:
            assert i in nodeset_visited
        for i in nodeset_leaves:
            assert i in nodeset_visited
        assert len(nodeset_leaves) + len(nodeset_cone) == len(nodeset_visited)

        # Create PMIG
        pmig_cut = PMIG(enable_polymorphic=(self._pmig_generated_opti.attribute_polymorphic_edges_flag_get(), self._pmig_generated_opti.attribute_polymorphic_nodes_flag_get()), allow_buffer_type_node=False)
        cut_map = Cut_Mapping()
        # PI
        for i in nodeset_leaves:
            if i == pmig_cut.get_literal_const0():
                cut_map.add_nodes_mapping(l_old=i, l_new=i)
            else:
                new_l = pmig_cut.create_pi()
                cut_map.add_nodes_mapping(l_old=i, l_new=new_l)
        # MAJ
        for i in nodeset_cone:
            assert self._pmig_generated_opti.is_maj(f=i)
            ch0, ch1, ch2 = self._pmig_generated_opti.get_maj_fanins(f=i)
            ch0_new = cut_map.get_new_literal(l_old=ch0)
            ch1_new = cut_map.get_new_literal(l_old=ch1)
            ch2_new = cut_map.get_new_literal(l_old=ch2)
            new_l = pmig_cut.create_maj(child0=ch0_new, child1=ch1_new, child2=ch2_new)
            cut_map.add_nodes_mapping(l_old=i, l_new=new_l)

        # PO
        pmig_cut.create_po(f=cut_map.get_new_literal(root_l))

        # Collect info
        cut_map_po = (cut_map.get_new_literal(root_l), root_l)
        cut_map_pi = {}
        for i in nodeset_leaves:
            key = cut_map.get_new_literal(l_old=i)
            cut_map_pi[key] = i

        # return
        return copy.deepcopy(pmig_cut), cut_map_pi, cut_map_po, nodeset_leaves, nodeset_visited

    # def op_get_n_cut(self, root_l, n, stop_list=[], cut_computation_method=None):
    #     '''
    #     获得以root_l(literal)为root的n-cut，并将获得的cut构建一个PMIG用于优化。
    #
    #     :param root_l: INT - root node的literal
    #     :param n: INT - leaves数目上限
    #     :param stop_list: TUPLE - stop nodes， 默认为空
    #     :param cut_computation_method: 获得n-cut的方法
    #     :return:
    #     '''
    #     if cut_computation_method is None:
    #         cut_computation = self.op_reconvergence_driven_cut_computation
    #     # Get n-cut
    #     nodeset_leaves, nodeset_visited = cut_computation(root_l=root_l, n=n, stop_list_with_fanout_literals=stop_list)
    #     nodeset_cone = self._pmig_generated_opti.get_cone(roots=(root_l,), stop=nodeset_leaves)
    #     # checks
    #     for i in nodeset_visited:
    #         assert (i in nodeset_leaves) or (i in nodeset_cone)
    #     for i in nodeset_cone:
    #         assert i in nodeset_visited
    #     for i in nodeset_leaves:
    #         assert i in nodeset_visited
    #     assert len(nodeset_leaves) + len(nodeset_cone) == len(nodeset_visited)
    #
    #     # Create PMIG
    #     pmig_cut = PMIG(enable_polymorphic=(self._pmig_generated_opti.attribute_polymorphic_edges_flag_get(), self._pmig_generated_opti.attribute_polymorphic_nodes_flag_get()), allow_buffer_type_node=False)
    #     cut_map = Cut_Mapping()
    #     # PI
    #     for i in nodeset_leaves:
    #         if i == pmig_cut.get_literal_const0():
    #             cut_map.add_nodes_mapping(l_old=i, l_new=i)
    #         else:
    #             new_l = pmig_cut.create_pi()
    #             cut_map.add_nodes_mapping(l_old=i, l_new=new_l)
    #     # MAJ
    #     for i in nodeset_cone:
    #         assert self._pmig_generated_opti.is_maj(f=i)
    #         ch0, ch1, ch2 = self._pmig_generated_opti.get_maj_fanins(f=i)
    #         ch0_new = cut_map.get_new_literal(l_old=ch0)
    #         ch1_new = cut_map.get_new_literal(l_old=ch1)
    #         ch2_new = cut_map.get_new_literal(l_old=ch2)
    #         new_l = pmig_cut.create_maj(child0=ch0_new, child1=ch1_new, child2=ch2_new)
    #         cut_map.add_nodes_mapping(l_old=i, l_new=new_l)
    #
    #     # PO
    #     pmig_cut.create_po(f=cut_map.get_new_literal(root_l))
    #
    #     # Collect info
    #     cut_map_po = (cut_map.get_new_literal(root_l), root_l)
    #     cut_map_pi = {}
    #     for i in nodeset_leaves:
    #         key = cut_map.get_new_literal(l_old=i)
    #         cut_map_pi[key] = i
    #
    #     # return
    #     return copy.deepcopy(pmig_cut), cut_map_pi, cut_map_po

    def op_number_of_fanouts(self, target_l):
        '''
        输入一个node的literal， 返回这个node的扇出数目, 以及扇出到的node的literals列表。

        :param l:
        :return:
        '''

        n_fanout = 0
        fanout_list = []
        target_id = target_l >> 2
        for node_l in self._pmig_generated_opti.get_iter_nodes_all():
            if self._pmig_generated_opti.is_maj(f=node_l):
                for ch_l in self._pmig_generated_opti.get_maj_fanins(f=node_l):
                    ch_id = ch_l >> 2
                    if ch_id == target_id:
                        n_fanout = n_fanout + 1
                        if node_l not in fanout_list:
                            fanout_list.append(node_l)
            elif self._pmig_generated_opti.is_latch(f=node_l):
                assert False
            elif self._pmig_generated_opti.is_buffer(f=node_l):
                assert False
            else:
                assert (self._pmig_generated_opti.is_pi(f=node_l) or self._pmig_generated_opti.is_const0(f=node_l))
        return n_fanout, fanout_list

    def op_get_all_nodes_with_multiple_fanouts(self, limit_number = 1):
        '''
        返回一个元组，包含扇出数目大于limit_number(默认为1)的node的literal及扇出literals。

        :param limit_number:
        :return:
        '''
        node_list = []
        for node_l in self._pmig_generated_opti.get_iter_nodes_all():
            n, ls = self.op_number_of_fanouts(target_l=node_l)
            if n > limit_number:
                node_list.append( (node_l, ls) )
        node_tuple = tuple(copy.deepcopy(node_list))
        return node_tuple





class PMIG_PNode_comb(PMIG_Generation_combinational):
    def __init__(self, mig1, mig2):
        super().__init__(mig1, mig2)
        self._pmig_generated = PMIG(enable_polymorphic=(False, False)) # The PMIG generated by self.pmig_generation
        self._pmig_generated_opti = PMIG(enable_polymorphic=(False, False)) # The PMIG generated by self.pmig_generation and optimized by self.opti_* functions.

    def reset_pmig(self):
        self._pmig_generated = PMIG(enable_polymorphic=(False, False))
        self._pmig_generated_opti = PMIG(enable_polymorphic=(False, False))


    def get_pmux(self):
        '''
        Get a PMIG obj of a 2 to 1 MUX, with 3 PIs: "mig_a", "mig_b" and "ctl"(select signal), and a 1 output: "mux_PO".

        :return: PMIG_obj, DICT - The PMIG of 2 to 1 MUX, and a dict.
        '''
        pmux = PMIG(enable_polymorphic=[False, False])
        literal_a = pmux.create_pi(name='mig_a')
        literal_b = pmux.create_pi(name='mig_b')
        literal_c = pmux.create_pi(name='ctl')
        literal_ac = pmux.create_maj(literal_a, literal_c, pmux.get_literal_const0()) # M(a, c, 0)
        literal_bc = pmux.create_maj(literal_b, pmux.negate_literal_if(literal_c, True), pmux.get_literal_const0()) # M(b, c', 0)
        literal_abc = pmux.create_maj(literal_ac, literal_bc, pmux.get_literal_const1()) # M( M(a,c,0), M(b, c', 0), 1)
        pmux.create_po(literal_abc, name="mux_PO")
        return pmux, {'fanin_A':literal_a, 'fanin_B':literal_b, 'ctl':literal_c, 'PI':None}

class PMIG_PEdge_comb(PMIG_Generation_combinational):
    def __init__(self, mig1, mig2):
        super().__init__(mig1, mig2)
        self._pmig_generated = PMIG(enable_polymorphic=(True, False)) # The PMIG generated by self.pmig_generation
        self._pmig_generated_opti = PMIG(enable_polymorphic=(True, False)) # The PMIG generated by self.pmig_generation and optimized by self.opti_* functions.

    def reset_pmig(self):
        self._pmig_generated = PMIG(enable_polymorphic=(True, False))
        self._pmig_generated_opti = PMIG(enable_polymorphic=(True, False))

    def get_pmux(self):
        '''
        Get a PMIG obj of a 2 to 1 MUX with polymorphic edges, with 2 PIs: "mig_a", "mig_b" , and a 1 output: "mux_PO".

        :return: PMIG_obj, DICT - The PMIG of 2 to 1 MUX, and a dict.
        '''
        pmux = PMIG(enable_polymorphic=[True, False])
        literal_a = pmux.create_pi(name='mig_a')
        literal_b = pmux.create_pi(name='mig_b')
        literal_ac = pmux.create_maj(literal_a, pmux.get_literal_const0(), pmux.get_literal_const_1_0()) # M(a, 0, 1/0)
        literal_bc = pmux.create_maj(literal_b, pmux.get_literal_const0(), pmux.get_literal_const_0_1()) # M(b, 0, 0/1)
        literal_abc = pmux.create_maj(literal_ac, literal_bc, pmux.get_literal_const1()) # M( M(a, 0, 1/0), M(b, 0, 0/1), 1)
        pmux.create_po(literal_abc, name="mux_PO")
        return pmux, {'fanin_A':literal_a, 'fanin_B':literal_b, 'PI':None}














