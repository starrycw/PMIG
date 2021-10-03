# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/5/19 下午8:48
# @Author  : c
# @File    : test.py

import sys
import copy
sys.path.append("..")
import global_vars as g_vars
g_vars._init()
from pmig import convert_to_graph
from pmig import graphs
from pmig import graphs_io
from pmig import pmig_ops

# Get global variables from global_vars
echo_mode = g_vars.get_value("echo_mode")
path_abc_srcdir = g_vars.get_value("path_srcdir")
print(path_abc_srcdir)
path_aiger_dir = g_vars.get_value("path_aiger_dir")

# Set Variables
# path_abc_srcfile = "rca2.v"
path_abc_srcfile = "ripple_64.blif"

status, warnings = convert_to_graph.convert_to_aiger(path_abc_srcdir, path_abc_srcfile, path_aiger_dir, ("strash", "rewrite"), echo_mode)
print(status, warnings)

aig_1 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
aig_1.fill_pi_names()
aig_1.fill_po_names()

mig_1 = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_1)
print(mig_1)

mf_1 = pmig_ops.PMIG_operator.op_get_all_nodes_with_multiple_fanouts(pmig_obj_r=copy.deepcopy(mig_1))
mf_2 = pmig_ops.PMIG_operator.op_get_all_nodes_with_multiple_fanouts_fast(pmig_obj_r=copy.deepcopy(mig_1))
print(mf_1)
print(mf_2)
print(mf_1 == mf_2)

print(pmig_ops.PMIG_operator.op_reconvergence_driven_cut_computation_with_stop_list(pmig_obj_r=copy.deepcopy(mig_1), root_l=1000, n=6))
print(pmig_ops.PMIG_operator.op_reconvergence_driven_cut_computation_with_multifanout_checks(pmig_obj_r=copy.deepcopy(mig_1), root_l=1000, n=6, multi_fanout_nodes_list=mf_2))

cut_1 = pmig_ops.PMIG_operator.op_get_n_cut_pmig_with_multifanout_checks(pmig_obj_r=copy.deepcopy(mig_1), root_l=1000, n=6)
print(cut_1)