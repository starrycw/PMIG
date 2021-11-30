# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/12
# @Author  : c
# @File    : benchmark_LGSynth91_SubgraphsOptiAuto.py

import sys
import time
import os
import copy
import datetime

import pmig.graphs

sys.path.append("../..")
import global_vars as g_vars
g_vars._init()
# from pmig import convert_to_graph
from pmig import graphs
from pmig import graphs_io
from pmig import pmig_ops
from pmig import pmig_logic
from pmig import exact_synthesis as ex_syn
from pmig import graphs_polymorphic





################################################
# Configurations
tasks_configuration = ('size_default', 4)

# 在这里设置随机验证的数量
task_n_random_veri = 50


################################################
# benchmark
input_file_list = (
    ('cht.blif', 'apex7.blif'), # C1
    ('lal.blif', 'c8.blif'), # C2
    ('misex2.pla', 'c8.blif'), # C3
    ('pcler8.blif', 'c8.blif'), # C4
    ('my_adder.blif', 'count.blif'), # C5
    ('misex2.pla', 'lal.blif'), # C6
    ('ttt2.blif', 'lal.blif'), # C7
    ('ttt2.blif', 'misex2.pla'), # C8
    ('lal.blif', 'pcler8.blif'), # C9
    ('C499.blif', 'C1355.blif'), # C10
    ('count.blif', 'unreg.blif'), # C11
    ('my_adder.blif', 'unreg.blif'), # C12
    ('pdc.pla', 'vda.blif'), # C13
    ('apex1.pla', 'k2.blif'), # C14
    ('misex3.pla', 'misex3c.pla'), # C15
)

################################################
# 用于存储结果的变量
result_dict = {}

# 存储结果的文件夹名称
now_time_str = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')





################################################
task_id = 0
for benchmark_i in input_file_list:
    task_id = task_id + 1
    assert task_id <= 15
    assert len(benchmark_i) == 2
    for subgraph_to_be_exec in benchmark_i:
        if subgraph_to_be_exec not in result_dict:
            print("############################################################################################")
            print("############################################################################################")
            print("Current Subgraph: {}".format(subgraph_to_be_exec))
            task_n_leaves = tasks_configuration[1]
            task_opti_method = tasks_configuration[0]

            echo_mode = g_vars.get_value("echo_mode")
            path_abc_srcdir = g_vars.get_value("path_srcdir") + "/LGSynth91/C{}".format(task_id)
            path_aiger_dir = g_vars.get_value("path_aiger_dir")

            # 生成存储结果的文件夹
            path_abc_resultdir = g_vars.get_value("path_srcdir") + "/LGSynth91/result2" # '{}/result'.format(path_abc_srcdir)
            if not (os.path.exists(path_abc_resultdir)):
                os.makedirs(path_abc_resultdir)

            path_abc_resultdir_current = '{}/TaskSubgraph-{}'.format(path_abc_resultdir, now_time_str)
            if not (os.path.exists(path_abc_resultdir_current)):
                os.makedirs(path_abc_resultdir_current)

            path_abc_srcfile = subgraph_to_be_exec
            aig_1 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
            aig_1.fill_pi_names()
            aig_1.fill_po_names()

            mig_1 = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_1, echo_mode=1)
            print(mig_1)

            opti_obj = pmig_ops.PMIG_optimization()
            opti_obj.initialization(mig_obj=mig_1, n_random_veri=task_n_random_veri)
            opti_obj.opti_clean_pos_by_type()
            opti_obj.opti_clean_irrelevant_nodes()

            # 优化策略
            if task_opti_method == 'size_default':
                cnt_opti_cycle = 0
                flag_continue = True
                while flag_continue:
                    cnt_opti_cycle = cnt_opti_cycle + 1
                    flag_continue = False
                    temp_current_pmig_obj = opti_obj.get_current_pmig()
                    assert isinstance(temp_current_pmig_obj, graphs.PMIG)
                    temp_current_pmig_size = temp_current_pmig_obj.n_majs()

                    # 每轮执行的操作 PI-PO
                    print(
                        "############################################################################################")
                    print('TASK {}, Cycle {}, rec_driven'.format(subgraph_to_be_exec, cnt_opti_cycle))
                    opti_obj.opti_exact_synthesis_size_frompi(n_leaves=task_n_leaves,
                                                              cut_computation_method='rec_driven')
                    opti_obj.opti_clean_irrelevant_nodes()

                    print(
                        "############################################################################################")
                    print('TASK {}, Cycle {}, rec_driven, allow 0 contribution'.format(subgraph_to_be_exec,
                                                                                       cnt_opti_cycle))
                    opti_obj.opti_exact_synthesis_size_frompi_allow_0contribution(n_leaves=task_n_leaves,
                                                                                  cut_computation_method='rec_driven')
                    opti_obj.opti_clean_irrelevant_nodes()

                    print(
                        "############################################################################################")
                    print('TASK {}, Cycle {}, rec_driven_mfc'.format(subgraph_to_be_exec, cnt_opti_cycle))
                    opti_obj.opti_exact_synthesis_size_frompi(n_leaves=task_n_leaves,
                                                              cut_computation_method='rec_driven_mfc')
                    opti_obj.opti_clean_irrelevant_nodes()

                    print(
                        "############################################################################################")
                    print('TASK {}, Cycle {}, rec_driven_mfc, allow 0 contribution'.format(subgraph_to_be_exec,
                                                                                           cnt_opti_cycle))
                    opti_obj.opti_exact_synthesis_size_frompi_allow_0contribution(n_leaves=task_n_leaves,
                                                                                  cut_computation_method='rec_driven_mfc')
                    opti_obj.opti_clean_irrelevant_nodes()


                    # 每轮执行的操作 PO-PI
                    print(
                        "############################################################################################")
                    print('TASK {}, Cycle {}, rec_driven'.format(subgraph_to_be_exec, cnt_opti_cycle))
                    opti_obj.opti_exact_synthesis_size_frompo(n_leaves=task_n_leaves,
                                                              cut_computation_method='rec_driven')
                    opti_obj.opti_clean_irrelevant_nodes()

                    print(
                        "############################################################################################")
                    print('TASK {}, Cycle {}, rec_driven, allow 0 contribution'.format(subgraph_to_be_exec, cnt_opti_cycle))
                    opti_obj.opti_exact_synthesis_size_frompo_allow_0contribution(n_leaves=task_n_leaves,
                                                                                  cut_computation_method='rec_driven')
                    opti_obj.opti_clean_irrelevant_nodes()

                    print(
                        "############################################################################################")
                    print('TASK {}, Cycle {}, rec_driven_mfc'.format(subgraph_to_be_exec, cnt_opti_cycle))
                    opti_obj.opti_exact_synthesis_size_frompo(n_leaves=task_n_leaves,
                                                              cut_computation_method='rec_driven_mfc')
                    opti_obj.opti_clean_irrelevant_nodes()

                    print(
                        "############################################################################################")
                    print('TASK {}, Cycle {}, rec_driven_mfc, allow 0 contribution'.format(subgraph_to_be_exec,
                                                                                           cnt_opti_cycle))
                    opti_obj.opti_exact_synthesis_size_frompo_allow_0contribution(n_leaves=task_n_leaves,
                                                                                  cut_computation_method='rec_driven_mfc')
                    opti_obj.opti_clean_irrelevant_nodes()

                    # 检查这一轮是否有优化
                    temp_new_pmig_obj = opti_obj.get_current_pmig()
                    assert isinstance(temp_new_pmig_obj, graphs.PMIG)
                    temp_new_pmig_size = temp_new_pmig_obj.n_majs()
                    print(
                        "############################################################################################")
                    print("Cycle {} finished! MIG nodes: {} -> {}".format(cnt_opti_cycle, temp_current_pmig_size,
                                                                          temp_new_pmig_size))
                    if temp_new_pmig_size < temp_current_pmig_size:
                        flag_continue = True
                    else:
                        assert temp_new_pmig_size == temp_current_pmig_size

            else:
                assert False

            pmig_obj_opti = opti_obj.get_current_pmig()
            result_dict[subgraph_to_be_exec] = (copy.deepcopy(mig_1), copy.deepcopy(pmig_obj_opti))

            pmig_writer_mig_raw = graphs_io.pmig_writer(pmig_obj=mig_1)
            f_path = path_abc_resultdir_current
            pmig_writer_mig_raw.write_to_file(f_name='{}.raw.pmig'.format(subgraph_to_be_exec), f_path=f_path)

            pmig_writer_mig_opti = graphs_io.pmig_writer(pmig_obj=pmig_obj_opti)
            f_path = path_abc_resultdir_current
            pmig_writer_mig_opti.write_to_file(f_name='{}.opti.pmig'.format(subgraph_to_be_exec), f_path=f_path)


# 所有任务都完成后，打印结果
print('################################################')
temp_ii = 0
for subgraphs_ii in input_file_list:
    temp_ii = temp_ii + 1

    print('################################################')
    print('################################################')
    print('####### RESULT {}, A'.format(temp_ii))
    print(result_dict[subgraphs_ii[0]][0])
    print("------->")
    print(result_dict[subgraphs_ii[0]][1])

    print('################################################')
    print('####### RESULT {}, B'.format(temp_ii))
    print(result_dict[subgraphs_ii[1]][0])
    print("------->")
    print(result_dict[subgraphs_ii[1]][1])



print("Time str: {}".format(now_time_str))




################################################
