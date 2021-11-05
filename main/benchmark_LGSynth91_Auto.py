# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/05
# @Author  : c
# @File    : benchmark_LGSynth91.py

import sys
import time
import os
import copy
sys.path.append("..")
import global_vars as g_vars
g_vars._init()
from pmig import convert_to_graph
from pmig import graphs
from pmig import graphs_io
from pmig import pmig_ops
from pmig import pmig_logic
from pmig import exact_synthesis as ex_syn
from pmig import graphs_polymorphic





################################################
list_tasks_to_be_exec = (
    #(task_id, task_type, task_allow_0contribution, task_n_leaves)
    (15, 'pedge', True, 4),
    (15, 'pnode', True, 4)
)

log_file_name = 'aaaaa'

task_n_random_veri = 20


################################################
# IO

# 控制台输出记录到文件
# class Logger(object):
#     def __init__(self, file_name="Default.log", stream=sys.stdout):
#         self.terminal = stream
#         self.log = open(file_name, "a")
#
#     def write(self, message):
#         self.terminal.write(message)
#         self.log.write(message)
#
#     def flush(self):
#         pass
#
#
# if __name__ == '__main__':
#     # 自定义目录存放日志文件
#     log_path = g_vars.get_value("path_srcdir") + '/Logs/'
#     if not os.path.exists(log_path):
#         os.makedirs(log_path)
#     # 日志文件名按照程序运行时间设置
#     log_file_name = log_path + 'log-' + time.strftime("%Y%m%d-%H%M%S", time.localtime()) + '.log'
#     # 记录正常的 print 信息
#     sys.stdout = Logger(log_file_name)
#     # 记录 traceback 异常信息
#     sys.stderr = Logger(log_file_name)

################################################
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
for task_to_be_exec in list_tasks_to_be_exec:
    print("##############################################")
    print("##############################################")
    print("Current Task: {}".format(task_to_be_exec))
    task_id = task_to_be_exec[0]
    assert task_id in range(0, 16)
    task_type = task_to_be_exec[1]
    task_allow_0contributation = task_to_be_exec[2]
    assert task_type in ('pedge', 'pnode')
    task_n_leaves = task_to_be_exec[3]


    echo_mode = g_vars.get_value("echo_mode")
    path_abc_srcdir = g_vars.get_value("path_srcdir") + "/LGSynth91/C{}".format(task_id)
    # print(path_abc_srcdir)
    path_aiger_dir = g_vars.get_value("path_aiger_dir")

    path_abc_srcfile = input_file_list[task_id - 1][0]
    aig_1 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
    aig_1.fill_pi_names()
    aig_1.fill_po_names()

    mig_1 = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_1, echo_mode=1)
    print(mig_1)

    path_abc_srcfile = input_file_list[task_id - 1][1]
    aig_2 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
    aig_2.fill_pi_names()
    aig_2.fill_po_names()

    mig_2 = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_2, echo_mode=1)
    print(mig_2)

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

    if task_type == 'pedge':
        opti_obj = pmig_ops.PMIG_optimization()
        opti_obj.initialization(mig_obj=mig_pedge, n_random_veri=task_n_random_veri)
        opti_obj.opti_clean_pos_by_type()
        opti_obj.opti_clean_irrelevant_nodes()
        if task_allow_0contributation:
            opti_obj.opti_exact_synthesis_size_frompo_allow_0contribution(n_leaves=task_n_leaves)
        else:
            opti_obj.opti_exact_synthesis_size_frompo(n_leaves=task_n_leaves)
        opti_obj.opti_clean_irrelevant_nodes()

        pmig_writer_mig_pedge = graphs_io.pmig_writer(pmig_obj=mig_pedge)
        f_path = path_abc_srcdir + '/result'
        pmig_writer_mig_pedge.write_to_file(f_name='mig_pedge.pmig', f_path=f_path)

        pmig_obj_opti = opti_obj.get_current_pmig()
        pmig_writer_mig_opti = graphs_io.pmig_writer(pmig_obj=pmig_obj_opti)
        f_path = path_abc_srcdir + '/result'
        pmig_writer_mig_opti.write_to_file(f_name='mig_pedge_opti_{}_{}_{}.pmig'.format(task_type, task_allow_0contributation, task_n_leaves), f_path=f_path)

    elif task_type == 'pnode':
        opti_obj = pmig_ops.PMIG_optimization()
        opti_obj.initialization(mig_obj=mig_pnode, n_random_veri=task_n_random_veri)
        opti_obj.opti_clean_pos_by_type()
        opti_obj.opti_clean_irrelevant_nodes()
        if task_allow_0contributation:
            opti_obj.opti_exact_synthesis_size_frompo_allow_0contribution(n_leaves=task_n_leaves)
        else:
            opti_obj.opti_exact_synthesis_size_frompo(n_leaves=task_n_leaves)
        opti_obj.opti_clean_irrelevant_nodes()

        pmig_writer_mig_pnode = graphs_io.pmig_writer(pmig_obj=mig_pnode)
        f_path = path_abc_srcdir + '/result'
        pmig_writer_mig_pnode.write_to_file(f_name='mig_pnode.pmig', f_path=f_path)

        pmig_obj_opti = opti_obj.get_current_pmig()
        pmig_writer_mig_opti = graphs_io.pmig_writer(pmig_obj=pmig_obj_opti)
        f_path = path_abc_srcdir + '/result'
        pmig_writer_mig_opti.write_to_file(f_name='mig_pnode_opti_{}_{}_{}.pmig'.format(task_type, task_allow_0contributation, task_n_leaves), f_path=f_path)


    pmig_writer_mig1 = graphs_io.pmig_writer(pmig_obj=mig_1)
    f_path = path_abc_srcdir + '/result'
    pmig_writer_mig1.write_to_file(f_name='mig_1.pmig', f_path=f_path)

    pmig_writer_mig2 = graphs_io.pmig_writer(pmig_obj=mig_2)
    f_path = path_abc_srcdir + '/result'
    pmig_writer_mig2.write_to_file(f_name='mig_2.pmig', f_path=f_path)


################################################