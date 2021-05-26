# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/5/19 下午8:48
# @Author  : c
# @File    : test.py

import global_vars as g_vars
g_vars._init()
from pmig import convert_to_graph
from pmig import graphs
from pmig import aig_io

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

aig_rca2 = aig_io.read_aiger(path_abc_srcdir + '/' + path_abc_srcfile + '.aig')
print("\n###PIs")
for aig_pi in aig_rca2.get_pis():
    print(aig_pi)

print("\n###ANDs")
for aig_and in aig_rca2.get_and_gates():
    print(aig_and, aig_rca2.get_and_left(aig_and), aig_rca2.get_and_right(aig_and))

print("\n###BUFFERs")
for aig_buf in aig_rca2.get_buffers():
    print(aig_buf)

print("\n###LATCHs")
for aig_lat in aig_rca2.get_latches():
    print(aig_lat)

print("\n###POs")
for aig_po in aig_rca2.get_pos():
    print(aig_po)

print("\n###{} PIs, {} POs, {} NODEs, {} BUFs, {} LATs".format( len(aig_rca2._pis), len(aig_rca2._pos), \
                                                               len(aig_rca2._nodes), len(aig_rca2._buffers), \
                                                               len(aig_rca2._latches) ))

mig01 = graphs._MIG_Node.make_const0()
mig02 = graphs._MIG_Node.make_pi(1)
mig03 = graphs._MIG_Node.make_maj(4, 6, 9)
mig04 = graphs._MIG_Node.make_latch(1, 0)
mig05 = graphs._MIG_Node.make_buffer(1, 9)
print(mig01)
print(mig02)
print(mig03)
print(mig04)
print(mig05)


