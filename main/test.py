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

# mig_rca2.create_maj(3, 5, 8)
# mig_rca2.create_maj(11, 5, 8)
mig_rca2.create_po(f=3)
mig_rca2.create_po(f=10)
# mig_rca2.create_maj(654, 32, 1)
# mig_rca2.create_maj(2310, 320, 10)
# mig_rca2.create_maj(2313, 325, 19)
# mig_rca2.create_po(f=2316)


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


mig_rca2.set_name(600, 'maj60')
writer01 = graphs_io.pmig_writer(mig_rca2)
writer01.write_to_file('test.pmig', path_abc_srcdir, f_comments_list=["Comment example", "Line 2", "Line 3", "2021"])

reader01 = graphs_io.pmig_reader()
mig_01 = reader01.read_pmig(path_abc_srcdir + '/' + 'test.pmig')

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


writer02 = graphs_io.pmig_writer(mig_01)
writer02.write_to_file('test01.pmig', path_abc_srcdir, f_comments_list=["Comment example", "Line 2", "Line 3", "2021"])

reader02 = graphs_io.pmig_reader()
mig_02 = reader02.read_pmig(path_abc_srcdir + '/' + 'test01.pmig')

writer03 = graphs_io.pmig_writer(mig_02)
writer03.write_to_file('test02.pmig', path_abc_srcdir, f_comments_list=["Comment example", "Line 2", "Line 3", "2021"])

reader03 = graphs_io.pmig_reader()
mig_03 = reader03.read_pmig(path_abc_srcdir + '/' + 'test02.pmig')

mig_new_01 = mig_03.pmig_clean_irrelevant_nodes()
writer_new01 = graphs_io.pmig_writer(mig_new_01)
writer_new01.write_to_file('test_new01.pmig', path_abc_srcdir, f_comments_list=["Comment example", "Line 2", "Line 3", "2021"])

reader_new02 = graphs_io.pmig_reader()
mig_new_02 = reader_new02.read_pmig(path_abc_srcdir + '/' + 'test_new01.pmig')
writer_new02 = graphs_io.pmig_writer(mig_new_02)
writer_new02.write_to_file('test_new02.pmig', path_abc_srcdir, f_comments_list=["Comment example", "Line 2", "Line 3", "2021"])

cone1 = mig_03.get_seq_cone(roots=range(1000, 1500))
cone2 = mig_03.topological_sort(cone1)
print(list(cone1))
print(list(cone2))

reader_s01 = graphs_io.pmig_reader()
mig_s01 = reader_s01.read_pmig(path_abc_srcdir + '/' + 's01.pmig')
mig_s01_c0 = mig_s01.pmig_clean_irrelevant_nodes()
mig_s01_c1 = mig_s01.pmig_clean_irrelevant_nodes((0, ))
mig_s01_c2 = mig_s01.pmig_clean_irrelevant_nodes((0, 1))
mig_s01_c3 = mig_s01.pmig_clean_irrelevant_nodes((2, ))
mig_s01_c4 = mig_s01.pmig_clean_irrelevant_nodes((2, 1))

writer_c0 = graphs_io.pmig_writer(mig_s01_c0)
writer_c0.write_to_file('s01_c0.pmig', path_abc_srcdir)

writer_c1 = graphs_io.pmig_writer(mig_s01_c1)
writer_c1.write_to_file('s01_c1.pmig', path_abc_srcdir)

writer_c2 = graphs_io.pmig_writer(mig_s01_c2)
writer_c2.write_to_file('s01_c2.pmig', path_abc_srcdir)

writer_c3 = graphs_io.pmig_writer(mig_s01_c3)
writer_c3.write_to_file('s01_c3.pmig', path_abc_srcdir)

writer_c4 = graphs_io.pmig_writer(mig_s01_c4)
writer_c4.write_to_file('s01_c4.pmig', path_abc_srcdir)
