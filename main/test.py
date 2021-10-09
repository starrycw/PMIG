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
from pmig import pmig_logic
from pmig import exact_synthesis as ex_syn

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

for root_l in range(1000, 800, -4):
    pmig_ops.PMIG_operator.op_cut_exact_synthesis_size(pmig_obj_r=copy.deepcopy(mig_1), root_l=root_l, n_leaves=4)

# mf_1 = pmig_ops.PMIG_operator.op_get_all_nodes_with_multiple_fanouts(pmig_obj_r=copy.deepcopy(mig_1))
# mf_2 = pmig_ops.PMIG_operator.op_get_all_nodes_with_multiple_fanouts_fast(pmig_obj_r=copy.deepcopy(mig_1))
# print(mf_1)
# print(mf_2)
# print(mf_1 == mf_2)

# print(pmig_ops.PMIG_operator.op_reconvergence_driven_cut_computation_with_stop_list(pmig_obj_r=copy.deepcopy(mig_1), root_l=64, n=4))
# print(pmig_ops.PMIG_operator.op_reconvergence_driven_cut_computation_with_multifanout_checks(pmig_obj_r=copy.deepcopy(mig_1), root_l=64, n=4, multi_fanout_nodes_list=mf_2))

# cut_1, cut_map_pi, cut_map_po, nodeset_leaves, nodeset_visited  = pmig_ops.PMIG_operator.op_get_n_cut_pmig_with_multifanout_checks(pmig_obj_r=copy.deepcopy(mig_1), root_l=1000, n=6)
# print("CUT:", cut_1)
# print("CUT MAP PI", cut_map_pi)
# print("CUT MAP PO", cut_map_po)
# print("LEAVES", nodeset_leaves)
# print("VISITED", nodeset_visited)
# assert False
# logicsimu1 = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=mig_1)
#
# logicsimu1.print_pis_id(more_info=True)
#
#
# LV_00 = pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_00
# LV_01 = pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_P01
# LV_10 = pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_P10
# LV_11 = pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_11
# LV_X0 = pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_PX0
# LV_X1 = pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_PX1
# LV_XX = pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_PXX
# LV_0X = pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_P0X
# LV_1X = pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_P1X
# print(logicsimu1.simu_pos_value(pi_vec=[LV_10, LV_11, LV_10, LV_11]))

# logicsimu2 = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=cut_1[0])
#
# logicsimu2.print_pis_id(more_info=True)
#
# fvec1, fvec2, is_po = logicsimu2.simu_for_exact_synthesis()
# print(fvec1)
# print(fvec2)
#
# vvv1 = (False, True, False, True, True, False, False, True, True, False, False, True, False, True, False, False)
# vvv2 = (False, True, False, True, True, False, False, True, True, False, False, True, False, True, False, False)
#
# exsyn_obj1 = ex_syn.PMIG_Cut_ExactSynthesis(func1=vvv1, func2=vvv2, allow_polymorphic=(vvv1 == vvv2))
#
# ifsat, nlist, polist, new_obj = exsyn_obj1.search_minimum_mig(upper_limit_n=6)
# print('*****************************************')
# print(ifsat)
# print(nlist)
# print(polist)
# print(new_obj)