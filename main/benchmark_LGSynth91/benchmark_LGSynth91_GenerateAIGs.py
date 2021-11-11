# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/11
# @Author  : c
# @File    : benchmark_LGSynth91_GenerateAIGs.py
#
# 用于生成LGSynth91 benchmark所需的AIG文件。

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

################################################

################################################
input_file_list = (
    ('cht.blif', 'apex7.blif'), # C1
    ('lal.blif', 'c8.blif'), # C2
    ('misex2.pla', 'c8.blif'), # C3
    ('pcler8.blif', 'c8.blif'), # C4
    ('my_adder.blif', 'count.blif'), # C5
    ('misex2.pla', 'lal.blif'), # C6
    ('ttt2.blif', 'lal.blif'), # C7
    ('ttt2.blif', 'misex2.pla'), # C8
    ('lal.blif', 'pcler8.blif'), # C9
    ('C499.blif', 'C1355.blif'), # C10
    ('count.blif', 'unreg.blif'), # C11
    ('my_adder.blif', 'unreg.blif'), # C12
    ('pdc.pla', 'vda.blif'), # C13
    ('apex1.pla', 'k2.blif'), # C14
    ('misex3.pla', 'misex3c.pla'), # C15
)

################################################
# Get global variables from global_vars
echo_mode = g_vars.get_value("echo_mode")
# path_abc_srcdir = g_vars.get_value("path_srcdir") + "/LGSynth91/C{}".format(task_id)
# print(path_abc_srcdir)
path_aiger_dir = g_vars.get_value("path_aiger_dir")

################################################
# PreGen
for pg_task_id in range(0, 15):
    path_abc_srcdir = g_vars.get_value("path_srcdir") + "/LGSynth91/C{}".format(pg_task_id+1)
    pg_task = input_file_list[pg_task_id]
    print("\n C{}: {}".format(pg_task_id+1, pg_task))

    for sub_id in (0, 1):
        print("Sub-graph {}: ".format(sub_id))
        path_abc_srcfile = pg_task[sub_id]
        status, warnings = convert_to_graph.convert_to_aiger(path_abc_srcdir, path_abc_srcfile, path_aiger_dir, ('strash', 'rewrite', 'rewrite', 'rewrite', 'rewrite', 'rewrite', 'rewrite'), echo_mode=1)
        if status != 0:
            assert False
        print(warnings)

