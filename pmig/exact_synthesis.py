# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/7/11
# @Author  : c
# @File    : exact_synthesis.py

import z3
from pmig import graphs
# AIG = graphs.AIG # alias
PMIG = graphs.PMIG # alias
from pmig import pmig_verification

from prettytable import PrettyTable
import copy
import numpy


class Z3Solver_PMIG:
    def __init__(self, po_v_1, po_v_2, n_node):
        self._po_value_1 = copy.deepcopy(po_v_1)
        self._po_value_2 = copy.deepcopy(po_v_2)
        self._n_node = n_node
        n_pis_f = numpy.log2(len(po_v_1))
        assert n_pis_f == numpy.log2(len(po_v_2))
        if n_pis_f % 1 == 0:
            self._n_pis = int(n_pis_f)
        else:
            assert False

        self._solver_main = z3.Solver()





class ExactSynthesis_Base:
    def __init__(self, mig_obj):
        assert self._mig_checker(mig_obj)
        self._mig_original = mig_obj
        self._n_pis = mig_obj.n_pis
        self._po_value_1 = None
        self._po_value_2 = None
        self._is_polymorphic = None

    def _mig_checker(self, mig_obj):
        '''
        检查MIG是否符合要求

        :param mig_obj:
        :return:
        '''

        if not isinstance(mig_obj, PMIG):
            return False
        return True

    def _update_po_value(self):
        '''
        对mig进行仿真，获得两种模式下的输出逻辑值元组
        :return:
        '''
        pmig_v = pmig_verification.PMIG_Verification(pmig_obj=copy.deepcopy(self._mig_original))
        self._po_value_1, self._po_value_2, self._is_polymorphic = pmig_v.simu_auto_for_exact_synthesis()

    def get_po_value(self):
        return self._po_value_1, self._po_value_2, self._is_polymorphic












class ExactSynthesis_4Cut(ExactSynthesis_Base):
    def __init__(self, mig_obj):
        super().__init__(mig_obj=mig_obj)

    def _mig_checker(self, mig_obj):
        if not isinstance(mig_obj, PMIG):
            return False
        if mig_obj.n_pis() > 4:
            print(mig_obj.n_pis(), ">4")
            return False
        if mig_obj.n_pos() != 1:
            print(mig_obj.n_pos(), "!=1")
            return False
        return True



