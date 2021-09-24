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
#path_abc_srcfile = "ripple_64.blif"

status, warnings = convert_to_graph.convert_to_aiger(path_abc_srcdir, path_abc_srcfile, path_aiger_dir, ("strash", "rewrite"), echo_mode)
print(status, warnings)

aig_1 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
aig_1.fill_pi_names()
aig_1.fill_po_names()

mig_1 = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_1)
print(mig_1)


# Set Variables
path_abc_srcfile = "rca2_inv.v"
#path_abc_srcfile = "ripple_64.blif"

status, warnings = convert_to_graph.convert_to_aiger(path_abc_srcdir, path_abc_srcfile, path_aiger_dir, ("strash", "rewrite"), echo_mode)
print(status, warnings)

aig_2 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
aig_2.fill_pi_names()
aig_2.fill_po_names()

mig_2 = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_2)
print(mig_2)

writer01 = graphs_io.pmig_writer(pmig_obj=mig_1)
writer01.write_to_file(f_name='mig_1.pmig', f_path=path_abc_srcdir + '/', f_comments_list=['test','mig_1'])

writer02 = graphs_io.pmig_writer(pmig_obj=mig_2)
writer02.write_to_file(f_name='mig_2.pmig', f_path=path_abc_srcdir + '/', f_comments_list=['test','mig_2'])

pmig_gen_pedge = graphs_polymorphic.PMIG_Gen_Comb_2to1_PEdge()
pmig_gen_pedge.initialization(mig1=mig_1, mig2=mig_2)
pmig_gen_pedge.set_merged_pis([(8,8)])
pmig_gen_pedge.set_muxed_pos_auto()
pmig_gen_pedge.pmig_generation(obsolete_muxed_pos=True)
mig_pedge = pmig_gen_pedge._pmig_generated
print(mig_pedge)
writer03 = graphs_io.pmig_writer(pmig_obj=mig_pedge)
writer03.write_to_file(f_name='mig_pedge.pmig', f_path=path_abc_srcdir + '/', f_comments_list=['test','mig_pedge'])


pmig_gen_pnode = graphs_polymorphic.PMIG_Gen_Comb_2to1_PNode()
pmig_gen_pnode.initialization(mig1=mig_1, mig2=mig_2)
pmig_gen_pnode.set_merged_pis([(8,8)])
pmig_gen_pnode.set_muxed_pos_auto()
pmig_gen_pnode.pmig_generation(obsolete_muxed_pos=True)
mig_pnode = pmig_gen_pnode._pmig_generated
print(mig_pnode)
writer04 = graphs_io.pmig_writer(pmig_obj=mig_pnode)
writer04.write_to_file(f_name='mig_pnode.pmig', f_path=path_abc_srcdir + '/', f_comments_list=['test','mig_pnode'])




