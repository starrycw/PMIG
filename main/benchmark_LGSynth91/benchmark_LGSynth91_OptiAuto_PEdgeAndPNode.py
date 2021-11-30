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
import benchmark_optimization_methods

################################################
# 在这里指定任务
list_tasks_to_be_exec = (
    #(task_id, task_type, task_opti_method task_n_leaves)
    (9, 'size_default', 4),
    (9, 'size_default', 4)
)

# 在这里设置随机验证的数量
task_n_random_veri = 50

# Optimization for sub-graphs A and B
opti_method_sub_graphs = 'paper2016_top_down'

# Optimization for muxed graph
opti_method_muxed_graphs = 'po_to_pi_size_rec_driven_only'


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
result_of_each_task = []

# 存储结果的文件夹名称
now_time_str = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

################################################
for task_to_be_exec in list_tasks_to_be_exec:
    print("############################################################################################")
    print("############################################################################################")
    print("Current Task: {}".format(task_to_be_exec))
    task_id = task_to_be_exec[0]
    assert task_id in range(0, 16)
    # task_type = task_to_be_exec[1]
    # assert task_type in ('pedge', 'pnode')
    task_n_leaves = task_to_be_exec[2]
    task_opti_method = task_to_be_exec[1]


    echo_mode = g_vars.get_value("echo_mode")
    path_abc_srcdir = g_vars.get_value("path_srcdir") + "/LGSynth91/C{}".format(task_id)
    path_aiger_dir = g_vars.get_value("path_aiger_dir")

    # 生成存储结果的文件夹
    path_abc_resultdir = g_vars.get_value("path_srcdir") + "/LGSynth91/result/C{}".format(task_id)
    if not (os.path.exists(path_abc_resultdir)):
        os.makedirs(path_abc_resultdir)

    path_abc_resultdir_current = '{}/Task-{}'.format(path_abc_resultdir, now_time_str)
    if not (os.path.exists(path_abc_resultdir_current)):
        os.makedirs(path_abc_resultdir_current)


    path_abc_srcfile = input_file_list[task_id - 1][0]
    aig_1 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
    aig_1.fill_pi_names()
    aig_1.fill_po_names()

    mig_1_raw = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_1, echo_mode=1)
    print(mig_1_raw)

    path_abc_srcfile = input_file_list[task_id - 1][1]
    aig_2 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
    aig_2.fill_pi_names()
    aig_2.fill_po_names()

    mig_2_raw = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_2, echo_mode=1)
    print(mig_2_raw)

    # Opti sub-migs

    mig_1 = benchmark_optimization_methods.exact_synthesis_combination.run_es(method_str=opti_method_sub_graphs,
        pmig_raw_obj=mig_1_raw, task_n_leaves=task_n_leaves, task_name='sub1 of {}'.format(task_to_be_exec))
    mig_2 = benchmark_optimization_methods.exact_synthesis_combination.run_es(method_str=opti_method_sub_graphs,
        pmig_raw_obj=mig_2_raw, task_n_leaves=task_n_leaves, task_name='sub2 of {}'.format(task_to_be_exec))




    pmig_gen_pnode = graphs_polymorphic.PMIG_Gen_Comb_2to1_PNode()
    pmig_gen_pnode.initialization(mig1=mig_1, mig2=mig_2)
    pmig_gen_pnode.set_merged_pis()
    pmig_gen_pnode.set_muxed_pos()
    pmig_gen_pnode.pmig_generation(obsolete_muxed_pos=True)
    mig_pnode = pmig_gen_pnode._pmig_generated
    # print(mig_pnode)

    pmig_gen_pedge = graphs_polymorphic.PMIG_Gen_Comb_2to1_PEdge()
    pmig_gen_pedge.initialization(mig1=mig_1, mig2=mig_2)
    pmig_gen_pedge.set_merged_pis()
    pmig_gen_pedge.set_muxed_pos()
    pmig_gen_pedge.pmig_generation(obsolete_muxed_pos=True)
    mig_pedge = pmig_gen_pedge._pmig_generated
    # print(mig_pedge)

    for task_type in ('pedge', 'pnode'):
        task_to_be_exec_now = task_to_be_exec + (task_type, )
        if task_type == 'pedge':
            opti_obj_temp = pmig_ops.PMIG_optimization()
            opti_obj_temp.initialization(mig_obj=mig_pedge, n_random_veri=task_n_random_veri)
            opti_obj_temp.opti_clean_pos_by_type()
            opti_obj_temp.opti_clean_irrelevant_nodes()

        elif task_type == 'pnode':
            opti_obj_temp = pmig_ops.PMIG_optimization()
            opti_obj_temp.initialization(mig_obj=mig_pnode, n_random_veri=task_n_random_veri)
            opti_obj_temp.opti_clean_pos_by_type()
            opti_obj_temp.opti_clean_irrelevant_nodes()

        else:
            assert False

        pmig_obj_muxed_raw = opti_obj_temp.get_current_pmig()

        # 优化策略

        pmig_obj_opti = benchmark_optimization_methods.exact_synthesis_combination.run_es(method_str=opti_method_muxed_graphs,
            pmig_raw_obj=pmig_obj_muxed_raw, task_n_leaves=task_n_leaves, task_name=task_to_be_exec_now)


        # 保存结果

        if task_type == 'pedge':
            pmig_writer_mig_pedge = graphs_io.pmig_writer(pmig_obj=mig_pedge)
            f_path = path_abc_resultdir_current
            pmig_writer_mig_pedge.write_to_file(f_name='mig_pedge.pmig', f_path=f_path)
            info_pmig_raw = copy.deepcopy(mig_pedge)

            pmig_writer_mig_opti = graphs_io.pmig_writer(pmig_obj=pmig_obj_opti)
            f_path = path_abc_resultdir_current
            pmig_writer_mig_opti.write_to_file(f_name='mig_pedge_opti_{}_{}_{}.pmig'.format(task_type, task_opti_method, task_n_leaves), f_path=f_path)
            info_pmig_optimized = copy.deepcopy(pmig_obj_opti)

        elif task_type == 'pnode':
            pmig_writer_mig_pnode = graphs_io.pmig_writer(pmig_obj=mig_pnode)
            f_path = path_abc_resultdir_current
            pmig_writer_mig_pnode.write_to_file(f_name='mig_pnode.pmig', f_path=f_path)
            info_pmig_raw = copy.deepcopy(mig_pnode)

            pmig_writer_mig_opti = graphs_io.pmig_writer(pmig_obj=pmig_obj_opti)
            f_path = path_abc_resultdir_current
            pmig_writer_mig_opti.write_to_file(f_name='mig_pnode_opti_{}_{}_{}.pmig'.format(task_type, task_opti_method, task_n_leaves), f_path=f_path)
            info_pmig_optimized = copy.deepcopy(pmig_obj_opti)


        pmig_writer_mig1 = graphs_io.pmig_writer(pmig_obj=mig_1)
        f_path = path_abc_resultdir_current
        pmig_writer_mig1.write_to_file(f_name='optimized_mig_1.pmig', f_path=f_path)

        pmig_writer_mig2 = graphs_io.pmig_writer(pmig_obj=mig_2)
        f_path = path_abc_resultdir_current
        pmig_writer_mig2.write_to_file(f_name='optimized_mig_2.pmig', f_path=f_path)

        info_taskinfo = (copy.deepcopy(task_to_be_exec_now), opti_method_sub_graphs, opti_method_muxed_graphs)
        info_tuple_current = (info_taskinfo, info_pmig_raw, info_pmig_optimized)
        result_of_each_task.append(copy.deepcopy(info_tuple_current))


# 所有任务都完成后，打印结果
for result_of_task_i in result_of_each_task:
    print("############################################################################################")
    print(result_of_task_i[0])
    print(result_of_task_i[1])
    print('--------->')
    print(result_of_task_i[2])
    print('\n')

print("Time str: {}".format(now_time_str))




################################################
