# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/30
# @Author  : c


import sys
import time
import os
import copy
import datetime

import pmig.graphs

sys.path.append("..")
import global_vars as g_vars
g_vars._init()
# from pmig import convert_to_graph
from pmig import graphs
from pmig import graphs_io
from pmig import pmig_ops
from pmig import pmig_logic
from pmig import exact_synthesis as ex_syn
from pmig import graphs_polymorphic

class exact_synthesis_combination:
    def __init__(self):
        assert False

    @staticmethod
    def run_es(method_str, pmig_raw_obj, task_n_leaves, task_name = None):
        if method_str == 'no':
            return copy.deepcopy(pmig_raw_obj)
        elif method_str == 'pi_to_po_size_default':
            return exact_synthesis_combination.es_pi_to_po_size_default(pmig_raw_obj=pmig_raw_obj,
                                                                        task_n_leaves=task_n_leaves,
                                                                        task_name=task_name)
        elif method_str == 'po_to_pi_size_default':
            return exact_synthesis_combination.es_po_to_pi_size_default(pmig_raw_obj=pmig_raw_obj,
                                                                        task_n_leaves=task_n_leaves,
                                                                        task_name=task_name)
        elif method_str == 'paper2016_top_down':
            return exact_synthesis_combination.es_po_to_pi_size_paper2016_TopDownApproach(pmig_raw_obj=pmig_raw_obj,
                                                                        task_n_leaves=task_n_leaves,
                                                                        task_name=task_name)
        elif method_str == 'po_to_pi_size_rec_driven_only':
            return exact_synthesis_combination.es_po_to_pi_size_rec_driven_only(pmig_raw_obj=pmig_raw_obj,
                                                                        task_n_leaves=task_n_leaves,
                                                                        task_name=task_name)
        else:
            assert False

    @staticmethod
    def es_pi_to_po_size_default(pmig_raw_obj, task_n_leaves, task_name = None):
        assert isinstance(pmig_raw_obj, graphs.PMIG)
        opti_obj = pmig_ops.PMIG_optimization()
        opti_obj.initialization(mig_obj=pmig_raw_obj, n_random_veri=20)
        opti_obj.opti_clean_pos_by_type()
        opti_obj.opti_clean_irrelevant_nodes()

        cnt_opti_cycle = 0
        flag_continue = True
        while flag_continue:
            cnt_opti_cycle = cnt_opti_cycle + 1
            flag_continue = False
            temp_current_pmig_obj = opti_obj.get_current_pmig()
            assert isinstance(temp_current_pmig_obj, graphs.PMIG)
            temp_current_pmig_size = temp_current_pmig_obj.n_majs()

            # 每轮执行的操作 PI-PO
            print("############################################################################################")
            print('TASK {}, Cycle {}, rec_driven'.format(task_name, cnt_opti_cycle))
            opti_obj.opti_exact_synthesis_size_frompi(n_leaves=task_n_leaves, cut_computation_method='rec_driven')
            opti_obj.opti_clean_irrelevant_nodes()

            print("############################################################################################")
            print('TASK {}, Cycle {}, rec_driven, allow 0 contribution'.format(task_name, cnt_opti_cycle))
            opti_obj.opti_exact_synthesis_size_frompi_allow_0contribution(n_leaves=task_n_leaves,
                                                                          cut_computation_method='rec_driven')
            opti_obj.opti_clean_irrelevant_nodes()

            print("############################################################################################")
            print('TASK {}, Cycle {}, rec_driven_mfc'.format(task_name, cnt_opti_cycle))
            opti_obj.opti_exact_synthesis_size_frompi(n_leaves=task_n_leaves, cut_computation_method='rec_driven_mfc')
            opti_obj.opti_clean_irrelevant_nodes()

            print("############################################################################################")
            print('TASK {}, Cycle {}, rec_driven_mfc, allow 0 contribution'.format(task_name, cnt_opti_cycle))
            opti_obj.opti_exact_synthesis_size_frompi_allow_0contribution(n_leaves=task_n_leaves,
                                                                          cut_computation_method='rec_driven_mfc')
            opti_obj.opti_clean_irrelevant_nodes()



            # 检查这一轮是否有优化
            temp_new_pmig_obj = opti_obj.get_current_pmig()
            assert isinstance(temp_new_pmig_obj, graphs.PMIG)
            temp_new_pmig_size = temp_new_pmig_obj.n_majs()
            print("############################################################################################")
            print(
                "Cycle {} finished! MIG nodes: {} -> {}".format(cnt_opti_cycle, temp_current_pmig_size, temp_new_pmig_size))
            if temp_new_pmig_size < temp_current_pmig_size:
                flag_continue = True
            else:
                assert temp_new_pmig_size == temp_current_pmig_size

        return copy.deepcopy(opti_obj.get_current_pmig())

    @staticmethod
    def es_po_to_pi_size_default(pmig_raw_obj, task_n_leaves, task_name=None):
        assert isinstance(pmig_raw_obj, graphs.PMIG)
        opti_obj = pmig_ops.PMIG_optimization()
        opti_obj.initialization(mig_obj=pmig_raw_obj, n_random_veri=20)
        opti_obj.opti_clean_pos_by_type()
        opti_obj.opti_clean_irrelevant_nodes()

        cnt_opti_cycle = 0
        flag_continue = True
        while flag_continue:
            cnt_opti_cycle = cnt_opti_cycle + 1
            flag_continue = False
            temp_current_pmig_obj = opti_obj.get_current_pmig()
            assert isinstance(temp_current_pmig_obj, graphs.PMIG)
            temp_current_pmig_size = temp_current_pmig_obj.n_majs()

            # 每轮执行的操作 PO-PI
            print("############################################################################################")
            print('TASK {}, Cycle {}, rec_driven'.format(task_name, cnt_opti_cycle))
            opti_obj.opti_exact_synthesis_size_frompo(n_leaves=task_n_leaves, cut_computation_method='rec_driven')
            opti_obj.opti_clean_irrelevant_nodes()

            print("############################################################################################")
            print('TASK {}, Cycle {}, rec_driven, allow 0 contribution'.format(task_name, cnt_opti_cycle))
            opti_obj.opti_exact_synthesis_size_frompo_allow_0contribution(n_leaves=task_n_leaves,
                                                                          cut_computation_method='rec_driven')
            opti_obj.opti_clean_irrelevant_nodes()

            print("############################################################################################")
            print('TASK {}, Cycle {}, rec_driven_mfc'.format(task_name, cnt_opti_cycle))
            opti_obj.opti_exact_synthesis_size_frompo(n_leaves=task_n_leaves, cut_computation_method='rec_driven_mfc')
            opti_obj.opti_clean_irrelevant_nodes()

            print("############################################################################################")
            print('TASK {}, Cycle {}, rec_driven_mfc, allow 0 contribution'.format(task_name, cnt_opti_cycle))
            opti_obj.opti_exact_synthesis_size_frompo_allow_0contribution(n_leaves=task_n_leaves,
                                                                          cut_computation_method='rec_driven_mfc')
            opti_obj.opti_clean_irrelevant_nodes()

            # 检查这一轮是否有优化
            temp_new_pmig_obj = opti_obj.get_current_pmig()
            assert isinstance(temp_new_pmig_obj, graphs.PMIG)
            temp_new_pmig_size = temp_new_pmig_obj.n_majs()
            print("############################################################################################")
            print(
                "Cycle {} finished! MIG nodes: {} -> {}".format(cnt_opti_cycle, temp_current_pmig_size,
                                                                temp_new_pmig_size))
            if temp_new_pmig_size < temp_current_pmig_size:
                flag_continue = True
            else:
                assert temp_new_pmig_size == temp_current_pmig_size

        return copy.deepcopy(opti_obj.get_current_pmig())

    @staticmethod
    def es_po_to_pi_size_paper2016_TopDownApproach(pmig_raw_obj, task_n_leaves, task_name=None):
        assert isinstance(pmig_raw_obj, graphs.PMIG)
        opti_obj = pmig_ops.PMIG_optimization()
        opti_obj.initialization(mig_obj=pmig_raw_obj, n_random_veri=20)
        opti_obj.opti_clean_pos_by_type()
        opti_obj.opti_clean_irrelevant_nodes()

        cnt_opti_cycle = 0
        flag_continue = True
        while flag_continue:
            cnt_opti_cycle = cnt_opti_cycle + 1
            flag_continue = False
            temp_current_pmig_obj = opti_obj.get_current_pmig()
            assert isinstance(temp_current_pmig_obj, graphs.PMIG)
            temp_current_pmig_size = temp_current_pmig_obj.n_majs()

            # 每轮执行的操作 PO-PI
            print("############################################################################################")
            print('TASK {}, Cycle {}, rec_driven'.format(task_name, cnt_opti_cycle))
            opti_obj.opti_exact_synthesis_size_frompo(n_leaves=task_n_leaves, cut_computation_method='rec_driven')
            opti_obj.opti_clean_irrelevant_nodes()



            # 检查这一轮是否有优化
            temp_new_pmig_obj = opti_obj.get_current_pmig()
            assert isinstance(temp_new_pmig_obj, graphs.PMIG)
            temp_new_pmig_size = temp_new_pmig_obj.n_majs()
            print("############################################################################################")
            print(
                "Cycle {} finished! MIG nodes: {} -> {}".format(cnt_opti_cycle, temp_current_pmig_size,
                                                                temp_new_pmig_size))
            if temp_new_pmig_size < temp_current_pmig_size:
                flag_continue = True
            else:
                assert temp_new_pmig_size == temp_current_pmig_size

        return copy.deepcopy(opti_obj.get_current_pmig())

    @staticmethod
    def es_po_to_pi_size_rec_driven_only(pmig_raw_obj, task_n_leaves, task_name=None):
        assert isinstance(pmig_raw_obj, graphs.PMIG)
        opti_obj = pmig_ops.PMIG_optimization()
        opti_obj.initialization(mig_obj=pmig_raw_obj, n_random_veri=20)
        opti_obj.opti_clean_pos_by_type()
        opti_obj.opti_clean_irrelevant_nodes()

        cnt_opti_cycle = 0
        flag_continue = True
        while flag_continue:
            cnt_opti_cycle = cnt_opti_cycle + 1
            flag_continue = False
            temp_current_pmig_obj = opti_obj.get_current_pmig()
            assert isinstance(temp_current_pmig_obj, graphs.PMIG)
            temp_current_pmig_size = temp_current_pmig_obj.n_majs()

            # 每轮执行的操作 PO-PI
            print("############################################################################################")
            print('TASK {}, Cycle {}, rec_driven'.format(task_name, cnt_opti_cycle))
            opti_obj.opti_exact_synthesis_size_frompo(n_leaves=task_n_leaves, cut_computation_method='rec_driven')
            opti_obj.opti_clean_irrelevant_nodes()

            print("############################################################################################")
            print('TASK {}, Cycle {}, rec_driven, allow 0 contribution'.format(task_name, cnt_opti_cycle))
            opti_obj.opti_exact_synthesis_size_frompo_allow_0contribution(n_leaves=task_n_leaves,
                                                                          cut_computation_method='rec_driven')
            opti_obj.opti_clean_irrelevant_nodes()



            # 检查这一轮是否有优化
            temp_new_pmig_obj = opti_obj.get_current_pmig()
            assert isinstance(temp_new_pmig_obj, graphs.PMIG)
            temp_new_pmig_size = temp_new_pmig_obj.n_majs()
            print("############################################################################################")
            print(
                "Cycle {} finished! MIG nodes: {} -> {}".format(cnt_opti_cycle, temp_current_pmig_size,
                                                                temp_new_pmig_size))
            if temp_new_pmig_size < temp_current_pmig_size:
                flag_continue = True
            else:
                assert temp_new_pmig_size == temp_current_pmig_size

        return copy.deepcopy(opti_obj.get_current_pmig())
