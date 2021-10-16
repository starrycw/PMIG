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
from pmig import graphs_polymorphic

# Get global variables from global_vars
echo_mode = g_vars.get_value("echo_mode")
path_abc_srcdir = g_vars.get_value("path_srcdir") + "/91"
print(path_abc_srcdir)
path_aiger_dir = g_vars.get_value("path_aiger_dir")

# Set Variables
# path_abc_srcfile = "rca2.v"
# path_abc_srcfile = "ripple_64.blif"

path_abc_srcfile = "cht.blif"

status, warnings = convert_to_graph.convert_to_aiger(path_abc_srcdir, path_abc_srcfile, path_aiger_dir, ("strash", ), echo_mode)
print(status, warnings)

aig_1 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
aig_1.fill_pi_names()
aig_1.fill_po_names()

mig_1 = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_1)
print(mig_1)




path_abc_srcfile = "apex7.blif"

status, warnings = convert_to_graph.convert_to_aiger(path_abc_srcdir, path_abc_srcfile, path_aiger_dir, ("strash", ), echo_mode)
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



opti_obj = pmig_ops.PMIG_optimization()
opti_obj.initialization(mig_obj=mig_pnode, n_random_veri=20)
opti_obj.opti_clean_pos_by_type()
opti_obj.opti_clean_irrelevant_nodes()
opti_obj.opti_exact_synthesis_size_frompo_allow_0contribution(n_leaves=5)
opti_obj.opti_clean_irrelevant_nodes()
