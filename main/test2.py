# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/16
# @Author  : c
# @File    : benchmark_LGSynth91.py

import sys
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
task_id = 1
assert task_id in range(0, 16)

task_type = 'pedge'
task_allow_0contributation = True
assert task_type in ('pedge', 'pnode')

task_n_leaves = 5
task_n_random_veri = 20
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
    ('pda.pla', 'vda.blif'), # C13
    ('apex1.pla', 'k2.blif'), # C14
    ('misex3.pla', 'misex3c.pla'), # C15
)

################################################
# Get global variables from global_vars
echo_mode = g_vars.get_value("echo_mode")
path_abc_srcdir = g_vars.get_value("path_srcdir") + "/LGSynth91/C{}".format(task_id)
print(path_abc_srcdir)
path_aiger_dir = g_vars.get_value("path_aiger_dir")

################################################

path_abc_srcfile = input_file_list[task_id-1][0]

status, warnings = convert_to_graph.convert_to_aiger(path_abc_srcdir, path_abc_srcfile, path_aiger_dir, ("strash", 'rewrite'), echo_mode=1)
print(status, warnings)

aig_1 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
aig_1.fill_pi_names()
aig_1.fill_po_names()

mig_1 = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_1)
print(mig_1)




path_abc_srcfile = input_file_list[task_id-1][1]

status, warnings = convert_to_graph.convert_to_aiger(path_abc_srcdir, path_abc_srcfile, path_aiger_dir, ("strash", 'rewrite'), echo_mode=1)
print(status, warnings)

aig_2 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
aig_2.fill_pi_names()
aig_2.fill_po_names()

mig_2 = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_2)
print(mig_2)




pmig_gen_pnode = graphs_polymorphic.PMIG_Gen_Comb_2to1_PNode()
pmig_gen_pnode.initialization(mig1=mig_1, mig2=mig_2)
pmig_gen_pnode.set_merged_pis()
pmig_gen_pnode.set_muxed_pos()
pmig_gen_pnode.pmig_generation(obsolete_muxed_pos=True)
mig_pnode = pmig_gen_pnode._pmig_generated
print(mig_pnode)

pmig_gen_pedge = graphs_polymorphic.PMIG_Gen_Comb_2to1_PEdge()
pmig_gen_pedge.initialization(mig1=mig_1, mig2=mig_2)
pmig_gen_pedge.set_merged_pis()
pmig_gen_pedge.set_muxed_pos()
pmig_gen_pedge.pmig_generation(obsolete_muxed_pos=True)
mig_pedge = pmig_gen_pedge._pmig_generated
print(mig_pedge)


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
