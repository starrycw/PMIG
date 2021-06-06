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

# mig_rca2.attribute_polymorphic_nodes_flag_disable()
# mig_rca2.attribute_polymorphic_edges_flag_disable()

mig_rca2.create_maj(3, 5, 8)
mig_rca2.create_maj(11, 5, 8)
mig_rca2.create_maj(3, 7, 8)
mig_rca2.create_po(f=3)
mig_rca2.create_po(f=10)

for buf_l in mig_rca2.get_iter_buffers():
    mig_rca2.convert_buf_to_pi(buf_l)

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

print("\n###AIG: {} PIs, {} POs, {} NODEs, {} BUFs, {} LATs".format( aig_rca2.n_pis(), aig_rca2.n_pos(), len(aig_rca2._nodes), aig_rca2.n_buffers(), aig_rca2.n_latches() ) )

print("\n###MIG: {} PIs, {} POs, {} NODEs, {} BUFs, {} LATs, {} MAJs".format( mig_rca2.n_pis(), mig_rca2.n_pos(), len(mig_rca2._nodes), mig_rca2.n_buffers(), mig_rca2.n_latches(), mig_rca2.n_majs() ) )

# mig_rca2.attribute_polymorphic_nodes_flag_disable()
# mig_rca2.attribute_polymorphic_edges_flag_disable()
print(mig_rca2.check_if_polymorphic_legal())
print(list(mig_rca2.get_iter_nodes_with_polymorphic_pi()))
print(mig_rca2.n_nodes_with_polymorphic_pi())
print(list(mig_rca2.get_iter_nodes_with_polymorphic_edge()))
print(mig_rca2.n_nodes_with_polymorphic_edge())
print(list(mig_rca2.get_iter_pos_with_polymorphic_fanin()))
print(mig_rca2.n_pos_with_polymorphic_edge())

filepath = path_abc_srcdir + '/' + 'test.pmig'
print(filepath)
writer01 = graphs_io.pmig_writer(mig_rca2)
writer01.write_to_file('test.pmig', path_abc_srcdir)

reader01 = graphs_io.pmig_reader()
mig_01 = reader01.read_pmig(filepath)

print("\n###MIG-PIs")
for mig_pi in mig_01.get_iter_pis():
    print(mig_pi)

print("\n###MIG-PIs")
for mig_pi in mig_rca2.get_iter_pis():
    print(mig_pi)

print("\n###MIG-MAJs")
for mig_maj in mig_01.get_iter_majs():
    print(mig_maj, mig_01.get_fanins(mig_maj))

print("\n###MIG-MAJs")
for mig_maj in mig_rca2.get_iter_majs():
    print(mig_maj, mig_rca2.get_fanins(mig_maj))

print("\n###MIG-BUFFERs")
for mig_buf in mig_01.get_iter_buffers():
    print(mig_buf)

print("\n###MIG-BUFFERs")
for mig_buf in mig_rca2.get_iter_buffers():
    print(mig_buf)

print("\n###MIG-LATCHs")
for mig_lat in mig_01.get_iter_latches():
    print(mig_lat)

print("\n###MIG-LATCHs")
for mig_lat in mig_rca2.get_iter_latches():
    print(mig_lat)

print("\n###MIG-POs")
for mig_po in mig_01.get_iter_pos():
    print(mig_po)

print("\n###MIG-POs")
for mig_po in mig_rca2.get_iter_pos():
    print(mig_po)

print("\n###MIG-NAMEs")
for idname in mig_01._id_to_name.items():
    print(idname)

print("\n###MIG-NAMEs")
for idname in mig_rca2._id_to_name.items():
    print(idname)

print("\n###MIG-PONAMEs")
for idname in mig_01._po_to_name.items():
    print(idname)

print("\n###MIG-PONAMEs")
for idname in mig_rca2._po_to_name.items():
    print(idname)

print("\n###MIG: {} PIs, {} POs, {} NODEs, {} BUFs, {} LATs, {} MAJs".format( mig_01.n_pis(), mig_01.n_pos(), len(mig_01._nodes), mig_01.n_buffers(), mig_01.n_latches(), mig_01.n_majs() ) )


print("\n###MIG: {} PIs, {} POs, {} NODEs, {} BUFs, {} LATs, {} MAJs".format( mig_rca2.n_pis(), mig_rca2.n_pos(), len(mig_rca2._nodes), mig_rca2.n_buffers(), mig_rca2.n_latches(), mig_rca2.n_majs() ) )


