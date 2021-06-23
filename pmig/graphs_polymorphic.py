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


class PMIG_Generation:
    def __init__(self, mig1, mig2):
        assert isinstance(mig1, PMIG)
        assert isinstance(mig2, PMIG)
        assert not self.is_polymorphic_mig(mig1), "[ERROR]graphs_polymorphic: The input PMIG (mig1) cannot be polymorphic!"
        assert not self.is_polymorphic_mig(mig2), "[ERROR]graphs_polymorphic: The input PMIG (mig2) cannot be polymorphic!"
        self._mig_a = mig1 # The PMIG obj of function A
        self._mig_b = mig2 # The PMIG obj of function B
        self._pmux, self._pmux_literals = self.get_pmux() # The PMIG obj of MUX, and the tuple of PI literals.

        self._mux_fanins = [] # A list with tuple elements.
                             # Each tuple contains 2 literals, which are the literals of a PO literal of mig_a and the corresponding PO of mig_b.
                             # The two PO will be connected with a pmux.

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

    def get_pmux(self):
        '''
        It should be defined in sub-class!

        :return:
        '''
        # Assert False, "[ERROR] graphs_polymorphic: PMIG_Generation.get_pmux() should not be called! It should be defined in sub-class."
        return PMIG(), None

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

    def set_mux_fanins(self, fanin_list = None):
        if fanin_list == None:
            n_pos_min = self._mig_a.n_pos()
            if self._mig_b.n_pos() < self._mig_a.n_pos():
                n_pos_min = self._mig_b.n_pos()
            fanin_list = []
            for i in range(0, n_pos_min):
                fanin_list.append( (i, i) )

        self._mux_fanins = fanin_list

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
                        pos_a.remove(a_i)
                        pos_b.remove(b_i)
                        log_list.append( "Name:{}, ID in A:{}, ID in B:{}.".format(a_i[3], a_i[0], b_i[0]) )
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

    def mux_fanin_list_remove(self, t):
        for i in t:
            assert isinstance(i, tuple)
            assert len(i) == 2
            if i in self._mux_fanins:
                self._mux_fanins.remove(i)
        return self.mux_fanin_list_get()

class PMIG_PNode(PMIG_Generation):
    def __init__(self, mig1, mig2):
        super().__init__(mig1, mig2)
        self._pmig_generated = PMIG(enable_polymorphic=(False, True))

    def get_pmux(self):
        '''
        Get a PMIG obj of a 2 to 1 MUX, with 3 PIs: "mig_a", "mig_b" and "ctl"(select signal), and a 1 output: "mux_PO".

        :return: PMIG_obj, TUPLE - The PMIG of 2 to 1 MUX, and a tuple with 3 literal: (literal of "mig_a", literal of "mig_b", and literal of "mig_c").
        '''
        pmux = PMIG(enable_polymorphic=[False, False])
        literal_a = pmux.create_pi(name='mig_a')
        literal_b = pmux.create_pi(name='mig_b')
        literal_c = pmux.create_pi(name='ctl')
        literal_ac = pmux.create_maj(literal_a, literal_c, pmux.get_literal_const0()) # M(a, c, 0)
        literal_bc = pmux.create_maj(literal_b, pmux.negate_literal_if(literal_c, True), pmux.get_literal_const0()) # M(b, c', 0)
        literal_abc = pmux.create_maj(literal_ac, literal_bc, pmux.get_literal_const1()) # M( M(a,c,0), M(b, c', 0), 1)
        pmux.create_po(literal_abc, name="mux_PO")
        return pmux, (literal_a, literal_b, literal_c)

class PMIG_PEdge(PMIG_Generation):
    def __init__(self, mig1, mig2):
        super().__init__(mig1, mig2)
        self._pmig_generated = PMIG(enable_polymorphic=(True, False))














