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

# Get global variables from global_vars
echo_mode = g_vars.get_value("echo_mode")
path_abc_srcdir = g_vars.get_value("path_srcdir")
print(path_abc_srcdir)
path_aiger_dir = g_vars.get_value("path_aiger_dir")

# Set Variables
# path_abc_srcfile = "rca2.v"
path_abc_srcfile = "ripple_8.blif"


status, warnings = convert_to_graph.convert_to_aiger(path_abc_srcdir, path_abc_srcfile, path_aiger_dir, ("strash", "rewrite"), echo_mode)
print(status, warnings)

aig_1 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
aig_1.fill_pi_names()
aig_1.fill_po_names()


mig_1 = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_1)
print(mig_1)

writer_1 = graphs_io.pmig_writer(mig_1)
writer_1.write_to_file('mig_1.pmig', path_abc_srcdir, f_comments_list=["Comment example", "abc", "def", "123"])
writer_1.write_to_file('mig_01.pmig', path_abc_srcdir, f_comments_list=["Comment example", "abc", "def", "123"])

reader_1 = graphs_io.pmig_reader()
mig_1_1 = reader_1.read_pmig(path_abc_srcdir + '/' + 'mig_1.pmig')

reader_2 = graphs_io.pmig_reader()
mig_2 = reader_2.read_pmig(path_abc_srcdir + '/' + 'mig_2.pmig')

print(mig_1 == mig_1_1)

mig_1_1.create_po(8)
mig_1_1.create_po(4)

for i in mig_2.get_iter_pos_with_polymorphic_fanin():
    print('xxx', i)

pmux_mig1 = graphs_polymorphic.PMIG_PNode(mig_1, mig_2)
pmux_mig1.print_pos_of_mig()
pmux_mig1.print_pis_of_mig()
mux_fanin_table1 = pmux_mig1.mux_fanin_list_get()
pmux_mig1.set_mux_auto()
pmux_mig1.set_merged_pis_auto()
mux_fanin_table2 = pmux_mig1.mux_fanin_list_get()


print(mux_fanin_table1)
print(mux_fanin_table2)
print(pmux_mig1.mux_fanin_list_get())
print(pmux_mig1.mux_fanin_list_add(( (1, 2), (7, 6)) ))
print("Merged_pis: ", pmux_mig1.merged_pis_list_get())
# print(pmux_mig1.mux_fanin_list_get())
# print(pmux_mig1.mux_fanin_list_remove( ((1, 1), (8, 4), (2, 2)) ))
# print(pmux_mig1.mux_fanin_list_get())

pmux1 = pmux_mig1._pmux
print(pmux1)

print("#####################")
print(pmux_mig1._pmig_generated)
pmux_mig1.pmig_generation(obsolete_muxed_pos=True)
print(pmux_mig1._pmig_generated)
pmig_generated = pmux_mig1.get_pmig_generated()
writer_mux1 = graphs_io.pmig_writer(pmig_generated)
writer_mux1.write_to_file('mig_mux1.pmig', path_abc_srcdir, f_comments_list=["Comment example", "abc", "def", "123"])

