# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/03
# @Author  : c
# @File    : exact_synthesis.py

from z3 import *
from pmig import graphs
# AIG = graphs.AIG # alias
PMIG = graphs.PMIG # alias

from prettytable import PrettyTable
import copy
import numpy

########################################################################################################################
# class PMIG_Cut_ExactSynthesis
#
# @Time    : 2021/10
# @Author  : c
#
# PMIG exact synthesis
#
#
#
########################################################################################################################
class PMIG_Cut_ExactSynthesis:
    def __init__(self, func1, func2, allow_polymorphic):
        '''
        func1和func2均为元组，元素为0或1,长度相等且应为2的正整数被。
        allow_polymorphic为bool类型，表示是否允许出现多态属性的edge。
        :param func1:
        :param func2:
        :param allow_polymorphic:
        '''
        assert isinstance(func1, tuple)
        assert isinstance(func2, tuple)
        assert isinstance(allow_polymorphic, bool)
        self._func1 = copy.deepcopy(func1)
        self._func2 = copy.deepcopy(func2)
        self._allow_polymorphic = allow_polymorphic
        self._n_pis, self._n_func = self._check_functions() # 分别为PI nodes的数目，以及PI向量的数目

        # Z3 Solver
        self._z3_solver = None

        # Z3 列表
        self._z3_nodes_func1 = None
        self._z3_nodes_func2 = None
        # Nodes的主列表，列表元素为Function。列表索引从0开始，长度为self._n_func，代表输入向量。每个Function的自变量代表着node的索引。

        self._z3_ch0_idx = None
        self._z3_ch1_idx = None
        self._z3_ch2_idx = None
        # 存储着Nodes的扇入idx。函数值为int，表示在主列表中的索引位置。
        # 对于const0和PIs来说，它们不存在扇入，因此对应函数值均为0即可。
        # 对于MAJs来说，这三个Function中分别是它的三个扇入nodes在主列表中的索引。

        self._z3_ch0_negated = None
        self._z3_ch1_negated = None
        self._z3_ch2_negated = None
        # 存储着Nodes的扇入取反属性。函数值为bool，表示是否有取反属性。
        # 对于const0和PIs来说，它们不存在扇入，因此对应函数值均为False即可。
        # 对于MAJs来说，这三个Function中分别是它的三个扇入edge的取反属性。

        self._z3_ch0_polymorphic = None
        self._z3_ch1_polymorphic = None
        self._z3_ch2_polymorphic = None
        # 存储着Nodes的扇入多态属性。函数值为bool，表示是否有多态属性。
        # 对于const0和PIs来说，它们不存在扇入，因此对应函数值均为False即可。
        # 对于MAJs来说，这三个Function中分别是它的三个扇入edge的多态属性。注意：若不允许多态，则所有函数值都应为False。

        self._z3_ch0_func1 = None
        self._z3_ch1_func1 = None
        self._z3_ch2_func1 = None

        self._z3_ch0_func2 = None
        self._z3_ch1_func2 = None
        self._z3_ch2_func2 = None
        # 存储着Nodes的扇入逻辑值（考虑edge属性)。列表元素为Function。列表索引从0开始，长度为self._n_func，代表输入向量。每个Function的自变量代表着node的索引。
        # 对于const0和PIs来说，它们不存在扇入，因此在这6个列表中对应值均为False即可。

        # Z3 PO
        self._z3_po_idx = None  # 是PO的扇入node在主列表中的idx
        self._z3_po_negated = None  # 表示PO的扇入edge是否取反
        self._z3_po_polymorphic = None  # 表示PO的扇入edge是否多态


    def _check_functions(self):
        '''
        对功能向量进行检查，并返回PI长度。
        :return:
        '''
        func1_len = len(self._func1)
        func2_len = len(self._func2)

        # 检查功能1和功能2是否长度相等
        assert func1_len == func2_len

        # 检查是否为2的整数次幂
        assert ( func1_len & (func1_len - 1) ) == 0

        # 若功能1和功能2不相等，那么应当允许多态
        if self._func1 != self._func2:
            assert self._allow_polymorphic

        print('n_PIs = ', numpy.log2(func1_len))
        # 返回PI长度和功能向量长度
        return int(numpy.log2(func1_len)), int(func1_len)

    def get_n_pis(self):
        '''
        return self._n_pis
        :return:
        '''
        return self._n_pis

#####################CREATE SOLVER
#######
    def _subtask_create_vars(self, n_maj_nodes):
        '''
        重建z3 solver，创建z3变量。
        n_maj_nodes为MAJ nodes数目。

        :param n_maj_nodes:
        :return:
        '''
        # Z3 Solver
        self._z3_solver = Solver()

        # Z3 列表
        self._z3_nodes_func1 = [ Function('NodeFunc1_{}'.format(ii), IntSort(), BoolSort()) for ii in range(0, self._n_func) ]
        self._z3_nodes_func2 = [ Function('NodeFunc2_{}'.format(ii), IntSort(), BoolSort()) for ii in range(0, self._n_func) ]
        # Nodes的主列表，列表元素为Function。列表索引从0开始，长度为self._n_func，代表输入向量。每个Function的自变量代表着node的索引。

        self._z3_ch0_idx = Function('CH0Idx', IntSort(), IntSort())
        self._z3_ch1_idx = Function('CH1Idx', IntSort(), IntSort())
        self._z3_ch2_idx = Function('CH2Idx', IntSort(), IntSort())
        # 存储着Nodes的扇入idx。函数值为int，表示在主列表中的索引位置。
        # 对于const0和PIs来说，它们不存在扇入，因此对应函数值均为0即可。
        # 对于MAJs来说，这三个Function中分别是它的三个扇入nodes在主列表中的索引。

        self._z3_ch0_negated = Function('CH0AttrNe', IntSort(), BoolSort())
        self._z3_ch1_negated = Function('CH1AttrNe', IntSort(), BoolSort())
        self._z3_ch2_negated = Function('CH2AttrNe', IntSort(), BoolSort())
        # 存储着Nodes的扇入取反属性。函数值为bool，表示是否有取反属性。
        # 对于const0和PIs来说，它们不存在扇入，因此对应函数值均为False即可。
        # 对于MAJs来说，这三个Function中分别是它的三个扇入edge的取反属性。

        self._z3_ch0_polymorphic = Function('CH0AttrPo', IntSort(), BoolSort())
        self._z3_ch1_polymorphic = Function('CH1AttrPo', IntSort(), BoolSort())
        self._z3_ch2_polymorphic = Function('CH2AttrPo', IntSort(), BoolSort())
        # 存储着Nodes的扇入多态属性。函数值为bool，表示是否有多态属性。
        # 对于const0和PIs来说，它们不存在扇入，因此对应函数值均为False即可。
        # 对于MAJs来说，这三个Function中分别是它的三个扇入edge的多态属性。注意：若不允许多态，则所有函数值都应为False。

        self._z3_ch0_func1 = [Function('CH0Func1_{}'.format(ii), IntSort(), BoolSort()) for ii in
                                range(0, self._n_func)]
        self._z3_ch1_func1 = [Function('CH1Func1_{}'.format(ii), IntSort(), BoolSort()) for ii in
                                range(0, self._n_func)]
        self._z3_ch2_func1 = [Function('CH2Func1_{}'.format(ii), IntSort(), BoolSort()) for ii in
                                range(0, self._n_func)]

        self._z3_ch0_func2 = [Function('CH0Func2_{}'.format(ii), IntSort(), BoolSort()) for ii in
                                range(0, self._n_func)]
        self._z3_ch1_func2 = [Function('CH1Func2_{}'.format(ii), IntSort(), BoolSort()) for ii in
                                range(0, self._n_func)]
        self._z3_ch2_func2 = [Function('CH2Func2_{}'.format(ii), IntSort(), BoolSort()) for ii in
                                range(0, self._n_func)]
        # 存储着Nodes的扇入逻辑值（考虑edge属性)。列表元素为Function。列表索引从0开始，长度为self._n_func，代表输入向量。每个Function的自变量代表着node的索引。
        # 对于const0和PIs来说，它们不存在扇入，因此在这6个列表中对应值均为False即可。

        # Z3 PO
        self._z3_po_idx = Int('PO_idx')  # 是PO的扇入node在主列表中的idx
        self._z3_po_negated = Bool('PO_ne')  # 表示PO的扇入edge是否取反
        self._z3_po_polymorphic = Bool('PO_po')  # 表示PO的扇入edge是否多态

#######
    def _subtask_constraint_lock_vars(self, n_maj_nodes):
        '''
        将具有固定值的变量（比如，不允许多态时，多态edge属性应为False）约束为应有的值。

        :param n_maj_nodes:
        :return:
        '''
        assert isinstance(self._z3_solver, Solver)

        # const0
        for ii_f in range(0, self._n_func):
            self._z3_solver.add(self._z3_nodes_func1[ii_f](0) == False)
            self._z3_solver.add(self._z3_nodes_func2[ii_f](0) == False)

        # polymorphic
        if not self._allow_polymorphic:
            for ii in range(0, (1 + self.get_n_pis() + n_maj_nodes)):
                self._z3_solver.add(self._z3_ch0_polymorphic(ii) == False)
                self._z3_solver.add(self._z3_ch1_polymorphic(ii) == False)
                self._z3_solver.add(self._z3_ch2_polymorphic(ii) == False)

#######
    def _subtask_constraint_majority_functionality(self, n_maj_nodes):
        '''
        MAJ nodes的值与三个扇入nodes值之间的关系。

        对于功能1来说，MAJ node的值为

        :param n_maj_nodes:
        :return:
        '''
        assert isinstance(self._z3_solver, Solver)

        for ii in range((1 + self.get_n_pis()), (1 + self.get_n_pis() + n_maj_nodes)):
            self._z3_solver.add(self._z3_ch0_idx(ii) < ii)
            for ii_f in range(0, self._n_func):
                # 功能1：MAJ实际的扇入值为扇入node的值附加上取反属性
                self._z3_solver.add(
                    self._z3_ch0_func1[ii_f](ii) == ( self._z3_nodes_func1[ii_f](self._z3_ch0_idx(ii)) == self._z3_ch0_negated(ii) )
                )






#######
    def create_solver(self, n_maj_nodes):
        '''
        重建z3 solver，创建z3变量，并添加约束。
        n_maj_nodes为MAJ nodes数目。

        :param n_maj_nodes:
        :return:
        '''

        assert isinstance(n_maj_nodes, int)
        assert n_maj_nodes > 0

        # 重建Solver和变量
        self._subtask_create_vars(n_maj_nodes=n_maj_nodes)
        # 约束不可变变量
        self._subtask_constraint_lock_vars(n_maj_nodes=n_maj_nodes)

        self._subtask_constraint_majority_functionality(n_maj_nodes=n_maj_nodes)















