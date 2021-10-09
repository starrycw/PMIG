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
        func1和func2均为元组，元素为False或True,长度相等且应为2的正整数被。
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

        # print('n_PIs = ', numpy.log2(func1_len))
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
        assert n_maj_nodes > 0

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
        assert n_maj_nodes > 0

        # const0
        for ii_f in range(0, self._n_func):
            self._z3_solver.add(self._z3_nodes_func1[ii_f](0) == False)
            self._z3_solver.add(self._z3_nodes_func2[ii_f](0) == False)

        # polymorphic
        if not self._allow_polymorphic:
            self._z3_solver.add(self._z3_po_polymorphic == False)
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
        assert n_maj_nodes > 0
        assert isinstance(self._z3_solver, Solver)

        for ii in range((1 + self.get_n_pis()), (1 + self.get_n_pis() + n_maj_nodes)):
            # 对于每个MAJ node，其三个扇入nodes的idx都必须具有小于该MAJ node的idx
            self._z3_solver.add(self._z3_ch0_idx(ii) < ii)
            self._z3_solver.add(self._z3_ch1_idx(ii) < ii)
            self._z3_solver.add(self._z3_ch2_idx(ii) < ii)

            # 对于扇入node的idx应当为非负数
            self._z3_solver.add(self._z3_ch0_idx(ii) >= 0)
            self._z3_solver.add(self._z3_ch1_idx(ii) >= 0)
            self._z3_solver.add(self._z3_ch2_idx(ii) >= 0)

            # MAJ功能
            for ii_f in range(0, self._n_func):
                # 功能1：MAJ实际的扇入值为扇入node的值附加上取反属性
                self._z3_solver.add(
                    self._z3_ch0_func1[ii_f](ii) == ( self._z3_nodes_func1[ii_f](self._z3_ch0_idx(ii)) != self._z3_ch0_negated(ii) )
                )
                self._z3_solver.add(
                    self._z3_ch1_func1[ii_f](ii) == ( self._z3_nodes_func1[ii_f](self._z3_ch1_idx(ii)) != self._z3_ch1_negated(ii))
                )
                self._z3_solver.add(
                    self._z3_ch2_func1[ii_f](ii) == ( self._z3_nodes_func1[ii_f](self._z3_ch2_idx(ii)) != self._z3_ch2_negated(ii))
                )
                # 功能2：MAJ实际的扇入值为扇入node的值附加上取反属性和多态属性
                self._z3_solver.add(
                    self._z3_ch0_func2[ii_f](ii) == ( self._z3_nodes_func2[ii_f](self._z3_ch0_idx(ii)) != (self._z3_ch0_negated(ii) != self._z3_ch0_polymorphic(ii)) )
                )
                self._z3_solver.add(
                    self._z3_ch1_func2[ii_f](ii) == ( self._z3_nodes_func2[ii_f](self._z3_ch1_idx(ii)) != (self._z3_ch1_negated(ii) != self._z3_ch1_polymorphic(ii)) )
                )
                self._z3_solver.add(
                    self._z3_ch2_func2[ii_f](ii) == ( self._z3_nodes_func2[ii_f](self._z3_ch2_idx(ii)) != (self._z3_ch2_negated(ii) != self._z3_ch2_polymorphic(ii)) )
                )
                # 功能1：MAJ的值为三个实际扇入值取多数
                self._z3_solver.add(
                    self._z3_nodes_func1[ii_f](ii) == Or(
                        And( self._z3_ch0_func1[ii_f](ii), self._z3_ch1_func1[ii_f](ii) ),
                        And( self._z3_ch1_func1[ii_f](ii), self._z3_ch2_func1[ii_f](ii) ),
                        And( self._z3_ch2_func1[ii_f](ii), self._z3_ch0_func1[ii_f](ii) )
                    )
                )
                # 功能2：MAJ的值为三个实际扇入值取多数
                self._z3_solver.add(
                    self._z3_nodes_func2[ii_f](ii) == Or(
                        And( self._z3_ch0_func2[ii_f](ii), self._z3_ch1_func2[ii_f](ii) ),
                        And( self._z3_ch1_func2[ii_f](ii), self._z3_ch2_func2[ii_f](ii) ),
                        And( self._z3_ch2_func2[ii_f](ii), self._z3_ch0_func2[ii_f](ii) )
                    )
                )


#######
    def _subtask_constraint_symmetry_breaking(self, n_maj_nodes):
        '''
        Symmetry breaking

        :param n_maj_nodes:
        :return:
        '''

        assert n_maj_nodes > 0

        for ii in range((1 + self.get_n_pis()), (1 + self.get_n_pis() + n_maj_nodes)):
            # MAJ的三个扇入nodes的idx：ch0 <= ch1 <= ch2。注意由于多态属性的存在，因此允许=。
            self._z3_solver.add(
                self._z3_ch0_idx(ii) <= self._z3_ch1_idx(ii)
            )
            self._z3_solver.add(
                self._z3_ch1_idx(ii) <= self._z3_ch2_idx(ii)
            )

        # 可选 - 优化edge属性
        #
        # 1. 禁止MAJ的超过2个扇入edge具有取反属性
        # 2. 禁止MAJ的超过2个扇入edge具有多态属性
        for ii in range((1 + self.get_n_pis()), (1 + self.get_n_pis() + n_maj_nodes)):
            # 1. 禁止MAJ的超过2个扇入edge具有取反属性
            self._z3_solver.add(
                False == Or(
                    And(self._z3_ch0_negated(ii), self._z3_ch1_negated(ii)),
                    And(self._z3_ch1_negated(ii), self._z3_ch2_negated(ii)),
                    And(self._z3_ch2_negated(ii), self._z3_ch0_negated(ii))
                )
            )
            # 2. 禁止MAJ的超过2个扇入edge具有多态属性
            self._z3_solver.add(
                False == Or(
                    And(self._z3_ch0_polymorphic(ii), self._z3_ch1_polymorphic(ii)),
                    And(self._z3_ch1_polymorphic(ii), self._z3_ch2_polymorphic(ii)),
                    And(self._z3_ch2_polymorphic(ii), self._z3_ch0_polymorphic(ii))
                )
            )


#######
    def _subtask_constraint_po_function(self, n_maj_nodes):
        '''
        PO的逻辑值应当正确

        :param n_maj_nodes:
        :return:
        '''

        assert n_maj_nodes > 0

        # PO的扇入idx应当为实际存在的nodes
        self._z3_solver.add(
            self._z3_po_idx < (1 + self.get_n_pis() + n_maj_nodes)
        )
        # PO的扇入idx只考虑MAJ
        self._z3_solver.add(
            self._z3_po_idx >= (1 + self.get_n_pis())
        )

        # 功能应当正确
        for ii_f in range(0, self._n_func):
            # 功能1,PO输出为PO扇入node附加取反属性
            self._z3_solver.add(
                self._func1[ii_f] == ( self._z3_nodes_func1[ii_f](self._z3_po_idx) != self._z3_po_negated )
            )
            # 功能2,PO输出为PO扇入node附加取反和多态属性
            self._z3_solver.add(
                self._func2[ii_f] == ( self._z3_nodes_func2[ii_f](self._z3_po_idx) != (self._z3_po_negated != self._z3_po_polymorphic) )
            )


#######
    def _subtask_constraint_pi_vector(self, n_maj_nodes):

        assert n_maj_nodes > 0

        # 指定PI输入向量。注意：具有最小idx的PI位于MSB！
        for ii_f in range(0, self._n_func):
            vec_bin = bin(ii_f)[2:]
            vec_tuple = tuple(str.zfill(vec_bin, self.get_n_pis()))
            assert len(vec_tuple) == self.get_n_pis()
            vec_pis_tuple = vec_tuple # [::-1]
            assert len(vec_pis_tuple) == self.get_n_pis()

            # print(vec_pis_tuple, self.get_n_pis())

            ii_idx = 1  # 别忘了CONST 0
            for ii_v in vec_pis_tuple:
                if int(ii_v) == 0:
                    self._z3_solver.add(
                        self._z3_nodes_func1[ii_f](ii_idx) == False
                    )
                    self._z3_solver.add(
                        self._z3_nodes_func2[ii_f](ii_idx) == False
                    )
                elif int(ii_v) == 1:
                    self._z3_solver.add(
                        self._z3_nodes_func1[ii_f](ii_idx) == True
                    )
                    self._z3_solver.add(
                        self._z3_nodes_func2[ii_f](ii_idx) == True
                    )
                else:
                    assert False
                ii_idx = ii_idx + 1
            assert ii_idx == 1 + self.get_n_pis()

#######
    def _subtask_constraint_for_0maj_case(self, n_maj_nodes):
        assert n_maj_nodes == 0

        #####################
        ####### create vars
        #####################
        # Z3 Solver
        self._z3_solver = Solver()

        # Z3 列表
        self._z3_nodes_func1 = [Function('NodeFunc1_{}'.format(ii), IntSort(), BoolSort()) for ii in
                                range(0, self._n_func)]
        self._z3_nodes_func2 = [Function('NodeFunc2_{}'.format(ii), IntSort(), BoolSort()) for ii in
                                range(0, self._n_func)]
        # Nodes的主列表，列表元素为Function。列表索引从0开始，长度为self._n_func，代表输入向量。每个Function的自变量代表着node的索引。

        # Z3 PO
        self._z3_po_idx = Int('PO_idx')  # 是PO的扇入node在主列表中的idx
        self._z3_po_negated = Bool('PO_ne')  # 表示PO的扇入edge是否取反
        self._z3_po_polymorphic = Bool('PO_po')  # 表示PO的扇入edge是否多态

        #####################
        ####### lock vars
        #####################
        # const0
        for ii_f in range(0, self._n_func):
            self._z3_solver.add(self._z3_nodes_func1[ii_f](0) == False)
            self._z3_solver.add(self._z3_nodes_func2[ii_f](0) == False)

        # polymorphic
        if not self._allow_polymorphic:
            self._z3_solver.add(self._z3_po_polymorphic == False)

        #####################
        ####### po function
        #####################
        # PO的扇入idx应当为实际存在的nodes
        self._z3_solver.add(
            self._z3_po_idx < (1 + self.get_n_pis())
        )

        self._z3_solver.add(
            self._z3_po_idx >= 0
        )

        # 功能应当正确
        for ii_f in range(0, self._n_func):
            # 功能1,PO输出为PO扇入node附加取反属性
            self._z3_solver.add(
                self._func1[ii_f] == (self._z3_nodes_func1[ii_f](self._z3_po_idx) != self._z3_po_negated)
            )
            # 功能2,PO输出为PO扇入node附加取反和多态属性
            self._z3_solver.add(
                self._func2[ii_f] == (self._z3_nodes_func2[ii_f](self._z3_po_idx) != (
                            self._z3_po_negated != self._z3_po_polymorphic))
            )

        #####################
        ####### pi vec
        #####################
        # 指定PI输入向量。注意：具有最小idx的PI位于MSB！
        for ii_f in range(0, self._n_func):
            vec_bin = bin(ii_f)[2:]
            vec_tuple = tuple(str.zfill(vec_bin, self.get_n_pis()))
            assert len(vec_tuple) == self.get_n_pis()
            vec_pis_tuple = vec_tuple  # [::-1]
            assert len(vec_pis_tuple) == self.get_n_pis()

            # print(vec_pis_tuple, self.get_n_pis())

            ii_idx = 1  # 别忘了CONST 0
            for ii_v in vec_pis_tuple:
                if int(ii_v) == 0:
                    self._z3_solver.add(
                        self._z3_nodes_func1[ii_f](ii_idx) == False
                    )
                    self._z3_solver.add(
                        self._z3_nodes_func2[ii_f](ii_idx) == False
                    )
                elif int(ii_v) == 1:
                    self._z3_solver.add(
                        self._z3_nodes_func1[ii_f](ii_idx) == True
                    )
                    self._z3_solver.add(
                        self._z3_nodes_func2[ii_f](ii_idx) == True
                    )
                else:
                    assert False
                ii_idx = ii_idx + 1
            assert ii_idx == 1 + self.get_n_pis()




#######
    def create_solver(self, n_maj_nodes):
        '''
        重建z3 solver，创建z3变量，并添加约束。
        n_maj_nodes为MAJ nodes数目。

        :param n_maj_nodes:
        :return:
        '''
        assert isinstance(n_maj_nodes, int)
        if n_maj_nodes > 0:
            assert n_maj_nodes > 0

            # 重建Solver和变量
            self._subtask_create_vars(n_maj_nodes=n_maj_nodes)
            assert isinstance(self._z3_solver, Solver)

            # 约束不可变变量
            self._subtask_constraint_lock_vars(n_maj_nodes=n_maj_nodes)

            # MAJ功能
            self._subtask_constraint_majority_functionality(n_maj_nodes=n_maj_nodes)

            # Symmetry breaking
            self._subtask_constraint_symmetry_breaking(n_maj_nodes=n_maj_nodes)

            # PO功能
            self._subtask_constraint_po_function(n_maj_nodes=n_maj_nodes)

            # 设置PI输入向量
            self._subtask_constraint_pi_vector(n_maj_nodes=n_maj_nodes)

            return copy.deepcopy(self._z3_solver)

        else:
            assert n_maj_nodes == 0

            self._subtask_constraint_for_0maj_case(n_maj_nodes=n_maj_nodes)

            return copy.deepcopy(self._z3_solver)




#######
    def check_solver(self, n_maj_nodes):
        '''
        求解solver。

        return if_sat, model_nodes_list, model_po

        if_sat: 即solver.check()的返回值

        model_nodes_list：若非sat，则为None。若sat，则为[
                                                        ( (M1-ch0 idx, M1-ch0 ne, M1-ch0 po), (M1-ch1 idx, M1-ch1 ne, M1-ch1 po), (M1-ch2 idx, M1-ch2 ne, M1-ch2 po) ),
                                                        ( (M2-ch0 idx, M2-ch0 ne, M2-ch0 po), (M2-ch1 idx, M2-ch1 ne, M2-ch1 po), (M2-ch2 idx, M2-ch2 ne, M2-ch2 po) ),
                                                        ......
                                                    ]

        model_po：若非sat，则为None。若sat，则为 (po_idx, po_ne, po_po)

        :return:
        '''

        assert isinstance(self._z3_solver, Solver)
        if_sat = self._z3_solver.check()

        if if_sat == sat:
            z3_model = self._z3_solver.model()

            # MAJ nodes
            # model_nodes = [
            #                   ( (M1-ch0 idx, M1-ch0 ne, M1-ch0 po), (M1-ch1 idx, M1-ch1 ne, M1-ch1 po), (M1-ch2 idx, M1-ch2 ne, M1-ch2 po) ),
            #                   ( (M2-ch0 idx, M2-ch0 ne, M2-ch0 po), (M2-ch1 idx, M2-ch1 ne, M2-ch1 po), (M2-ch2 idx, M2-ch2 ne, M2-ch2 po) ),
            #                   ......
            #                   ]
            model_nodes_list = []
            for ii in range((1 + self.get_n_pis()), (1 + self.get_n_pis() + n_maj_nodes)):
                # ch0
                tuple_node_ch0 = ( (z3_model.evaluate(self._z3_ch0_idx(ii))).as_long(), z3_model.evaluate(self._z3_ch0_negated(ii)), z3_model.evaluate(self._z3_ch0_polymorphic(ii)) )

                # ch1
                tuple_node_ch1 = ( (z3_model.evaluate(self._z3_ch1_idx(ii))).as_long(), z3_model.evaluate(self._z3_ch1_negated(ii)), z3_model.evaluate(self._z3_ch1_polymorphic(ii)) )

                # ch2
                tuple_node_ch2 = ( (z3_model.evaluate(self._z3_ch2_idx(ii))).as_long(), z3_model.evaluate(self._z3_ch2_negated(ii)), z3_model.evaluate(self._z3_ch2_polymorphic(ii)) )

                tuple_node_3chs = ( copy.deepcopy(tuple_node_ch0), copy.deepcopy(tuple_node_ch1), copy.deepcopy(tuple_node_ch2) )
                model_nodes_list.append(copy.deepcopy(tuple_node_3chs))


            # PO
            po_fanin_idx = (z3_model.evaluate(self._z3_po_idx)).as_long()
            po_fanin_ne = z3_model.evaluate(self._z3_po_negated)
            po_fanin_po = z3_model.evaluate(self._z3_po_polymorphic)

            model_po = (copy.deepcopy(po_fanin_idx), copy.deepcopy(po_fanin_ne), copy.deepcopy(po_fanin_po))

        else:
            model_nodes_list = None
            model_po = None


        return if_sat, model_nodes_list, model_po

#######
    def search_minimum_mig(self, upper_limit_n, echo_mode = True):
        '''
        main

        :return:
        '''
        if echo_mode:
            print("############################# exact_synthesis/search_minimum_mig #############################")
            print("##############################################################################################")
            print("########################################### Func1 ############################################")
            print(self._func1)
            print("########################################### Func2 ############################################")
            print(self._func2)
            print("##################################### Allow polymorphic ######################################")
            print(self._allow_polymorphic)
            print("########################################### START ############################################")

        n_maj_nodes = 0
        sat_flag = False
        while( (sat_flag == False) & (n_maj_nodes <= upper_limit_n) ):
            if echo_mode:
                print("Constraint: {}-MAJ MIG ......".format(n_maj_nodes))
            self.create_solver(n_maj_nodes=n_maj_nodes)
            if_sat, model_nodes_list, model_po = self.check_solver(n_maj_nodes=n_maj_nodes)
            if if_sat == sat:
                sat_flag = True
            if echo_mode:
                print(sat_flag)
            n_maj_nodes = n_maj_nodes + 1

        if echo_mode:
            print("############################################ END #############################################")
            print('MAJ: ')
            print(model_nodes_list)
            print("PO: ")
            print(model_po)
            print("##############################################################################################")

        new_pmig_obj = None
        if sat_flag:
            new_pmig_obj = PMIG_Cut_ExactSynthesis.construct_from_z3_model_list(n_pi_nodes=self.get_n_pis(), model_nodes_list=copy.deepcopy(model_nodes_list), model_po=copy.deepcopy(model_po))
        return sat_flag, model_nodes_list, model_po, new_pmig_obj

#######
    @staticmethod
    def construct_from_z3_model_list(n_pi_nodes, model_nodes_list, model_po):
        assert isinstance(n_pi_nodes, int)
        assert n_pi_nodes > 0
        new_mig_obj = PMIG()
        map_literal = {PMIG.get_literal_const0():PMIG.get_literal_const0()} # idx映射字典
        # PIs
        for ii in range(0, n_pi_nodes):
            pi_l = new_mig_obj.create_pi()
            assert ii == (pi_l >> 2) - 1
            map_literal[pi_l] = pi_l

        # MAJ
        cnt_idx = n_pi_nodes + 1
        for ii_maj in model_nodes_list:
            ch0_tuple = ii_maj[0] # (idx, ne, po)
            ch1_tuple = ii_maj[1]
            ch2_tuple = ii_maj[2]

            # ch0 literal
            ch0_idx_old = ch0_tuple[0]
            ch0_l_old = ch0_idx_old << 2
            assert ch0_l_old in map_literal
            ch0_l = map_literal[ch0_l_old]
            if ch0_tuple[1]:
                ch0_l = ch0_l + 1
            if ch0_tuple[2]:
                ch0_l = ch0_l + 2

            # ch1 literal
            ch1_idx_old = ch1_tuple[0]
            ch1_l_old = ch1_idx_old << 2
            assert ch1_l_old in map_literal
            ch1_l = map_literal[ch1_l_old]
            if ch1_tuple[1]:
                ch1_l = ch1_l + 1
            if ch1_tuple[2]:
                ch1_l = ch1_l + 2

            # ch2 literal
            ch2_idx_old = ch2_tuple[0]
            ch2_l_old = ch2_idx_old << 2
            assert ch2_l_old in map_literal
            ch2_l = map_literal[ch2_l_old]
            if ch2_tuple[1]:
                ch2_l = ch2_l + 1
            if ch2_tuple[2]:
                ch2_l = ch2_l + 2

            # create MAJ
            # print("++++++++++",ch0_l, ch1_l, ch2_l )
            maj_l = new_mig_obj.create_maj(child0=ch0_l, child1=ch1_l, child2=ch2_l)
            assert (cnt_idx << 2) not in map_literal
            map_literal[(cnt_idx << 2)] = maj_l
            # print("===", cnt_idx, maj_l)

            cnt_idx = cnt_idx + 1

        assert cnt_idx == 1 + n_pi_nodes + len(model_nodes_list)

        # PO
        po_idx_old, po_ne, po_po = model_po
        po_fanin_l_old = po_idx_old << 2
        assert po_fanin_l_old in map_literal
        po_fanin_l = map_literal[po_fanin_l_old]
        if po_ne:
            po_fanin_l = po_fanin_l + 1
        if po_po:
            po_fanin_l = po_fanin_l + 2
        po_l = new_mig_obj.create_po(f=po_fanin_l)

        # print("+++++++++++")
        # for majiii in new_mig_obj.get_iter_majs():
        #     print(majiii)

        return copy.deepcopy(new_mig_obj)





























