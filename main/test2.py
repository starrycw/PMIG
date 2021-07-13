# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/6/20 下午8:48
# @Author  : c
# @File    : test2.py

import sys
import copy
sys.path.append("..")
import global_vars as g_vars
g_vars._init()
from pmig import convert_to_graph
from pmig import graphs
from pmig import graphs_io
from pmig import graphs_polymorphic
from pmig import pmig_verification as pmig_veri
from pmig import exact_synthesis

# Get global variables from global_vars
echo_mode = g_vars.get_value("echo_mode")
path_abc_srcdir = g_vars.get_value("path_srcdir")
print(path_abc_srcdir)
path_aiger_dir = g_vars.get_value("path_aiger_dir")

# Set Variables
path_abc_srcfile = "rca2.v"
#path_abc_srcfile = "ripple_8.blif"

status, warnings = convert_to_graph.convert_to_aiger(path_abc_srcdir, path_abc_srcfile, path_aiger_dir, ("strash", "rewrite"), echo_mode)
print(status, warnings)

aig_1 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
aig_1.fill_pi_names()
aig_1.fill_po_names()

mig_1 = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_1)
print(mig_1)

# Set Variables
path_abc_srcfile = "rca2_inv.v"
#path_abc_srcfile = "ripple_8.blif"

status, warnings = convert_to_graph.convert_to_aiger(path_abc_srcdir, path_abc_srcfile, path_aiger_dir, ("strash", "rewrite"), echo_mode)
print(status, warnings)

aig_2 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
aig_2.fill_pi_names()
aig_2.fill_po_names()

mig_2 = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_2)
print(mig_2)

print("##########ccc")
pnode_muxed = graphs_polymorphic.PMIG_PEdge_comb(mig1=mig_1, mig2=mig_2)
pnode_muxed.set_mux_auto()
pnode_muxed.set_merged_pis_auto()
pnode_muxed.pmig_generation(obsolete_muxed_pos=True)

mig_muxed = pnode_muxed.get_pmig_generated()
print(mig_muxed)
writer1 = graphs_io.pmig_writer(mig_muxed)
writer1.write_to_file(f_name="mig_muxed", f_path=path_abc_srcdir)
for pi_l in mig_muxed.get_iter_pis():
    name = mig_muxed.get_name_by_id(pi_l)
    print( (pi_l, name) )

node_with_multuple_fanout = pnode_muxed.op_get_all_nodes_with_multiple_fanouts()
print(node_with_multuple_fanout)


pnode_muxed.opti_clean_pos_by_type()
mig_muxed = pnode_muxed.get_pmig_generated()
print(mig_muxed)
writer1 = graphs_io.pmig_writer(mig_muxed)
writer1.write_to_file(f_name="mig_muxed_opti", f_path=path_abc_srcdir)
for pi_l in mig_muxed.get_iter_pis():
    name = mig_muxed.get_name_by_id(pi_l)
    print( (pi_l, name) )


root = 100
n=4
print("####################################################")
node_with_multuple_fanout = pnode_muxed.op_get_all_nodes_with_multiple_fanouts()
print(node_with_multuple_fanout)
node_with_multuple_fanout = []

print(pnode_muxed.get_pmig_generated())

print(mig_muxed.get_maj_fanins(root))
leaves, visited = pnode_muxed.op_reconvergence_driven_cut_computation(root_l=root, n=n, stop_list=node_with_multuple_fanout)
print(leaves, visited)
print(pnode_muxed.get_pmig_generated().get_cone(roots=(root, ), stop=leaves))
cut_pmig, cut_map_pi, cut_map_po = pnode_muxed.op_get_n_cut(root_l=root, n=n, stop_list=node_with_multuple_fanout)
print(cut_pmig)
print(cut_map_pi)
print(cut_map_po)
print("######################################################")
es1 = exact_synthesis.ExactSynthesis_4Cut(cut_pmig)
es1._update_po_value()
print(es1.get_po_value())



# pmig_veri1 = pmig_veri.PMIG_Verification(pmig_obj=mig_muxed)
# pmig_veri1.print_pis_id(more_info=True)
# simu_info, simu_result, simu_result_xx = pmig_veri1.run_simu()
# print(simu_info[0])
# print(simu_info[1])
# print(simu_info[2])
# print(len(simu_result))
# print(simu_result)
# print(simu_result_xx)

# mig_new = mig_1.pmig_clean_irrelevant_nodes()
#
# pmig_veri2 = pmig_veri.PMIG_Verification(pmig_obj=mig_new)
# pmig_veri2.print_pis_id(more_info=True)
# simu_result2 = pmig_veri2.run_simu()
# print(len(simu_result2))
# print(simu_result2)
#
# print(simu_result == simu_result2)
# print(simu_result is simu_result2)


