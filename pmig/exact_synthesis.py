# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/10/03
# @Author  : c
# @File    : exact_synthesis.py

import z3
from pmig import graphs
# AIG = graphs.AIG # alias
PMIG = graphs.PMIG # alias

from prettytable import PrettyTable
import copy
import numpy