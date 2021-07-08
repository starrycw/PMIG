# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/5/19 下午8:48
# @Author  : c
# @File    : test.py

import sys
sys.path.append("..")
import global_vars as g_vars
g_vars._init()
from pmig import convert_to_graph
from pmig import graphs
from pmig import graphs_io

# Get global variables from global_vars
echo_mode = g_vars.get_value("echo_mode")
path_abc_srcdir = g_vars.get_value("path_srcdir")
print(path_abc_srcdir)
path_aiger_dir = g_vars.get_value("path_aiger_dir")

# Set Variables
# path_abc_srcfile = "rca2.v"
path_abc_srcfile = "ripple_64.blif"


status, warnings = convert_to_graph.convert_to_aiger(path_abc_srcdir, path_abc_srcfile, path_aiger_dir, ("strash", "rewrite", "abc", "python"), echo_mode)
print(status, warnings)

aig_rca2 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
# aig_rca2.create_latch(name="Latch01", next = 5)
# aig_rca2.create_latch(name="Latch06", init=graphs.AIG.INIT_ONE, next = 600)
# aig_rca2.create_po(f=7, name="PO001", po_type=graphs.AIG.JUSTICE)
# aig_rca2.create_buffer(buf_in=3, name="BUF001")
# aig_rca2.create_buffer(buf_in=6)

aig_rca2.fill_pi_names()
aig_rca2.fill_po_names()

ALLOWED_AIG_PO_TYPE = {graphs.AIG.OUTPUT: graphs.PMIG.PO_OUTPUT, "undefined": graphs.PMIG.PO_UNDEFINED, graphs.AIG.JUSTICE: graphs.PMIG.PO_JUSTICE}
# ALLOWED_AIG_PO_TYPE = {graphs.AIG.OUTPUT: graphs.PMIG.PO_OUTPUT, "undefined": graphs.PMIG.PO_UNDEFINED}
aig_rca2 = aig_rca2.clean()
mig_rca2 = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_rca2, allow_modification=False, allow_buffer=True, allow_latch=True, custom_po_conversion=ALLOWED_AIG_PO_TYPE)

# mig_rca2.attribute_polymorphic_nodes_flag_disable()
# mig_rca2.attribute_polymorphic_edges_flag_disable()
mig_rca2.create_maj(3, 5, 8)
mig_rca2.create_maj(11, 5, 8)
mig_rca2.create_po(f=3)
mig_rca2.create_po(f=10)
lll = mig_rca2.create_buffer(23)
ll=mig_rca2.create_maj(654, 32, lll)
lll = mig_rca2.create_buffer(233)
mig_rca2.create_po(f=lll)
lll = mig_rca2.create_buffer(ll)
mig_rca2.create_latch(next=lll)
print(mig_rca2)
mig_rca2_1 = mig_rca2.pmig_clean_all_buffers()
print(mig_rca2_1)
mig_rca2_2 = mig_rca2.pmig_clean_irrelevant_nodes()
print(mig_rca2_2)
