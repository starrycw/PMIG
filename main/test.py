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
path_abc_srcdir = g_vars.get_value("path_abc_srcdir")
print(path_abc_srcdir)
path_aiger_dir = g_vars.get_value("path_aiger_dir")

# Set Variables
path_abc_srcfile = "rca2.v"
#path_abc_srcfile = "ripple_64.blif"

status, warnings = convert_to_graph.convert_to_aiger(path_abc_srcdir, path_abc_srcfile, path_aiger_dir, ("strash", "rewrite", "abc", "python"), echo_mode)
print(status, warnings)

aig_rca2 = graphs_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
aig_rca2.create_latch(name="Latch01", next = 5)
aig_rca2.create_latch(name="Latch06", init=graphs.AIG.INIT_ONE, next = 6)
aig_rca2.create_po(f=7, name="PO001", po_type=graphs.AIG.JUSTICE)
aig_rca2.create_buffer(buf_in=3, name="BUF001")
aig_rca2.create_buffer(buf_in=6)

aig_rca2.fill_pi_names()
aig_rca2.fill_po_names()


mig_rca2 = graphs.PMIG.convert_aig_to_pmig(aig_obj=aig_rca2, allow_modification=True, allow_buffer=True, allow_latch=True)

print("\n###AIG-PIs")
for aig_pi in aig_rca2.get_pis():
    print(aig_pi)

print("\n###MIG-PIs")
for mig_pi in mig_rca2.get_iter_pis():
    print(mig_pi)

print("\n###AIG-ANDs")
for aig_and in aig_rca2.get_and_gates():
    print(aig_and, aig_rca2.get_and_left(aig_and), aig_rca2.get_and_right(aig_and))

print("\n###MIG-MAJs")
for mig_maj in mig_rca2.get_iter_majs():
    print(mig_maj, mig_rca2.get_fanins(mig_maj))

print("\n###AIG-BUFFERs")
for aig_buf in aig_rca2.get_buffers():
    print(aig_buf)

print("\n###MIG-BUFFERs")
for mig_buf in mig_rca2.get_iter_buffers():
    print(mig_buf)

print("\n###AIG-LATCHs")
for aig_lat in aig_rca2.get_latches():
    print(aig_lat)

print("\n###MIG-LATCHs")
for mig_lat in mig_rca2.get_iter_latches():
    print(mig_lat)

print("\n###AIG-POs")
for aig_po in aig_rca2.get_pos():
    print(aig_po)

print("\n###MIG-POs")
for mig_po in mig_rca2.get_iter_pos():
    print(mig_po)

print("\n###AIG: {} PIs, {} POs, {} NODEs, {} BUFs, {} LATs".format( len(aig_rca2._pis), len(aig_rca2._pos), \
                                                               len(aig_rca2._nodes), len(aig_rca2._buffers), \
                                                               len(aig_rca2._latches) ))

print("\n###MIG: {} PIs, {} POs, {} NODEs, {} BUFs, {} LATs".format( len(mig_rca2._pis), len(mig_rca2._pos), \
                                                               len(mig_rca2._nodes), len(mig_rca2._buffers), \
                                                               len(mig_rca2._latches) ))


