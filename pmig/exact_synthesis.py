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
        self._n_pis, self._n_func = self._check_functions()

        # Z3 Solver
        self._z3_solver = None

        # Z3 列表
        self._z3_nodes_list = None # Nodes的主列表，元素为布尔，表示node的值。从索引0开始，依次对应const 0，PIs，以及MAJs。

        self._z3_ch0_idx = None
        self._z3_ch1_idx = None
        self._z3_ch2_idx = None
        # 存储着Nodes的扇入idx。元素为int，表示在主列表中的索引位置。
        # 对于const0和PIs来说，它们不存在扇入，因此在这3个列表中对应值均为0即可。
        # 对于MAJs来说，这三个列表中分别是它的三个扇入nodes在主列表中的索引。

        self._z3_ch0_negated = None
        self._z3_ch1_negated = None
        self._z3_ch2_negated = None
        # 存储着Nodes的扇入取反属性。元素为bool，表示是否有取反属性。
        # 对于const0和PIs来说，它们不存在扇入，因此在这3个列表中对应值均为False即可。
        # 对于MAJs来说，这三个列表中分别是它的三个扇入edge的取反属性。

        self._z3_ch0_poltmorphic = None
        self._z3_ch1_polymorphic = None
        self._z3_ch2_polymorphic = None
        # 存储着Nodes的扇入多态属性。元素为bool，表示是否有多态属性。
        # 对于const0和PIs来说，它们不存在扇入，因此在这3个列表中对应值均为False即可。
        # 对于MAJs来说，这三个列表中分别是它的三个扇入edge的多态属性。注意：若不允许多态，则列表中所有元素都应为False。

        # Z3 PO
        self._z3_po_idx = None # int类型，是PO的扇入node在主列表中的idx
        self._z3_po_negated = None # bool， 表示PO的扇入edge是否取反
        self._z3_po_polymorphic = None # bool， 表示PO的扇入edge是否多态

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

        # 返回PI长度和功能向量长度
        return numpy.log2(func1_len), func1_len

    def get_n_pis(self):
        '''
        return self._n_pis
        :return:
        '''
        return self._n_pis

#####################CREATE SOLVER
#######
    def _createsolver_create_vars(self, n_maj_nodes):
        '''
        重建z3 solver，创建z3变量。
        n_maj_nodes为MAJ nodes数目。

        :param n_nodes:
        :return:
        '''
        # Z3 Solver
        self._z3_solver = Solver()

        # Z3 列表
        self._z3_nodes_list = BoolVector('Node', (
                    1 + self.get_n_pis() + n_maj_nodes))  # Nodes的主列表，元素为布尔，表示node的值。从索引0开始，依次对应const 0，PIs，以及MAJs。

        self._z3_ch0_idx = IntVector('Ch0_idx', (1 + self.get_n_pis() + n_maj_nodes))
        self._z3_ch1_idx = IntVector('Ch1_idx', (1 + self.get_n_pis() + n_maj_nodes))
        self._z3_ch2_idx = IntVector('Ch2_idx', (1 + self.get_n_pis() + n_maj_nodes))
        # 存储着Nodes的扇入idx。元素为int，表示在主列表中的索引位置。
        # 对于const0和PIs来说，它们不存在扇入，因此在这3个列表中对应值均为0即可。
        # 对于MAJs来说，这三个列表中分别是它的三个扇入nodes在主列表中的索引。

        self._z3_ch0_negated = BoolVector('Ch0_ne', (1 + self.get_n_pis() + n_maj_nodes))
        self._z3_ch1_negated = BoolVector('Ch1_ne', (1 + self.get_n_pis() + n_maj_nodes))
        self._z3_ch2_negated = BoolVector('Ch2_ne', (1 + self.get_n_pis() + n_maj_nodes))
        # 存储着Nodes的扇入取反属性。元素为bool，表示是否有取反属性。
        # 对于const0和PIs来说，它们不存在扇入，因此在这3个列表中对应值均为False即可。
        # 对于MAJs来说，这三个列表中分别是它的三个扇入edge的取反属性。

        self._z3_ch0_poltmorphic = BoolVector('Ch0_po', (1 + self.get_n_pis() + n_maj_nodes))
        self._z3_ch1_polymorphic = BoolVector('Ch1_po', (1 + self.get_n_pis() + n_maj_nodes))
        self._z3_ch2_polymorphic = BoolVector('Ch2_po', (1 + self.get_n_pis() + n_maj_nodes))
        # 存储着Nodes的扇入多态属性。元素为bool，表示是否有多态属性。
        # 对于const0和PIs来说，它们不存在扇入，因此在这3个列表中对应值均为False即可。
        # 对于MAJs来说，这三个列表中分别是它的三个扇入edge的多态属性。注意：若不允许多态，则列表中所有元素都应为False。

        # Z3 PO
        self._z3_po_idx = Int('PO_idx')  # int类型，是PO的扇入node在主列表中的idx
        self._z3_po_negated = Bool('PO_ne')  # bool， 表示PO的扇入edge是否取反
        self._z3_po_polymorphic = Bool('PO_po')  # bool， 表示PO的扇入edge是否多态

#######
    def create_solver(self, n_maj_nodes):
        '''
        重建z3 solver，创建z3变量，并添加约束。
        n_maj_nodes为MAJ nodes数目。

        :param n_nodes:
        :return:
        '''

        assert isinstance(n_maj_nodes, int)
        assert n_maj_nodes > 0

        # 重建Solver和变量
        self._createsolver_create_vars(n_maj_nodes=n_maj_nodes)













