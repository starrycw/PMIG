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

mf_1 = pmig_ops.PMIG_operator.op_get_all_nodes_with_multiple_fanouts(pmig_obj_r=copy.deepcopy(mig_1))
mf_2 = pmig_ops.PMIG_operator.op_get_all_nodes_with_multiple_fanouts_fast(pmig_obj_r=copy.deepcopy(mig_1))
print(mf_1)
print(mf_2)
print(mf_1 == mf_2)

# print(pmig_ops.PMIG_operator.op_reconvergence_driven_cut_computation_with_stop_list(pmig_obj_r=copy.deepcopy(mig_1), root_l=64, n=4))
# print(pmig_ops.PMIG_operator.op_reconvergence_driven_cut_computation_with_multifanout_checks(pmig_obj_r=copy.deepcopy(mig_1), root_l=64, n=4, multi_fanout_nodes_list=mf_2))

cut_1 = pmig_ops.PMIG_operator.op_get_n_cut_pmig_with_multifanout_checks(pmig_obj_r=copy.deepcopy(mig_1), root_l=800, n=6)
print("CUT:", cut_1)

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

logicsimu2 = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=cut_1[0])

logicsimu2.print_pis_id(more_info=True)

fvec1, fvec2, is_po = logicsimu2.simu_for_exact_synthesis()
print(fvec1)
print(fvec2)

exsyn_obj1 = ex_syn.PMIG_Cut_ExactSynthesis(func1=fvec1, func2=fvec2, allow_polymorphic=is_po)
mm = exsyn_obj1.create_solver(n_maj_nodes=1)
print('ch0 idx', mm[exsyn_obj1._z3_ch0_idx])
print('ch1 idx', mm[exsyn_obj1._z3_ch1_idx])
print('ch2 idx', mm[exsyn_obj1._z3_ch2_idx])

print('ch0 ne', mm[exsyn_obj1._z3_ch0_negated])
print('ch1 ne', mm[exsyn_obj1._z3_ch1_negated])
print('ch2 ne', mm[exsyn_obj1._z3_ch2_negated])

print('ch0 po', mm[exsyn_obj1._z3_ch0_polymorphic])
print('ch1 po', mm[exsyn_obj1._z3_ch1_polymorphic])
print('ch2 po', mm[exsyn_obj1._z3_ch2_polymorphic])

print('PO idx', mm[exsyn_obj1._z3_po_idx])
print('PO ne', mm[exsyn_obj1._z3_po_negated])
print('PO po', mm[exsyn_obj1._z3_po_polymorphic])
