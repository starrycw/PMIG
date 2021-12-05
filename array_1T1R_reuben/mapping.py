# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/05
# @Author  : c

import copy
from pmig import graphs
from array_1T1R_reuben import array_reuben2021

class Mapping_to_array:

    def __init__(self, pmig_obj, n_row, n_sa, n_col_per_sa, list_sa_polymorphic):
        assert isinstance(pmig_obj, graphs.PMIG)
        self._pmig_obj = copy.deepcopy(pmig_obj)
        self._array_obj = array_reuben2021.Array_Reuben2021_LiteralOnly(n_row=n_row,
                                                                        n_sa=n_sa,
                                                                        available_col_per_sa=n_col_per_sa,
                                                                        list_sa_polymorphic=list_sa_polymorphic)
        self._array_obj.init_rrams(method='LRS') # 将阵列中的可用RRAM全部初始化为LRS

    def get_pmig_obj(self):
        return copy.deepcopy(self._pmig_obj)

    def get_min_level_without_constraint(self):
        p = self.get_pmig_obj()
        assert isinstance(p, graphs.PMIG)
        list_maj_with_level = [[0]] # 列表，元素idx代表level索引，每一个元素都为列表，元素为该level内含的MAJ/PI literal。
        dict_level_of_maj = {0:0} # 字典，key为MAJ/PI的literal，value为level idx。
        max_level_idx_current = 0 # 当前的最大level idx。

        for pi_i in p.get_iter_pis():
            list_maj_with_level[0].append(pi_i)
            assert pi_i not in dict_level_of_maj
            dict_level_of_maj[pi_i] = 0

        for maj_i in p.get_iter_majs():
            assert isinstance(maj_i, int)
            max_level_of_ch = -1
            for ch_i in p.get_maj_fanins(f=maj_i):
                ch_i_noattr = graphs.PMIG.get_noattribute_literal(f=ch_i)
                assert ch_i_noattr in dict_level_of_maj
                temp_ch_i_level = dict_level_of_maj[ch_i_noattr]
                if temp_ch_i_level > max_level_of_ch:
                    max_level_of_ch = temp_ch_i_level
            level_of_maj_i = max_level_of_ch + 1
            if level_of_maj_i > max_level_idx_current:
                list_maj_with_level.append([])
                max_level_idx_current = max_level_idx_current + 1
                assert level_of_maj_i == max_level_idx_current
            list_maj_with_level[level_of_maj_i].append(maj_i)
            assert maj_i not in dict_level_of_maj
            dict_level_of_maj[maj_i] = level_of_maj_i

        return copy.deepcopy(list_maj_with_level), copy.deepcopy(dict_level_of_maj), max_level_idx_current


