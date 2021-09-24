# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/5/26
# @Author  : c
# @File    : graphs_io.py
#
#
#
import copy
import io
import re
import subprocess
import fileinput
import os

# import xrange
xrange = range # alias!

# from . aig import AIG
from pmig import graphs
AIG = graphs.AIG # alias
PMIG = graphs.PMIG # alias

########################################################################################################################
# PMIG_IO
#
# @Time    : 2021/6/4
# @Author  : c
#
#
#
########################################################################################################################
class pmig_writer:
    def __init__(self, pmig_obj):
        assert isinstance(pmig_obj, PMIG)
        # assert pmig_obj.n_buffers() == 0, "[ERROR] graph_io/pmig_writer: The input PMIG has buffer-type node."

        self._pmig_obj = copy.deepcopy(pmig_obj)
        self._N = self._pmig_obj.n_nodes()
        self._I = self._pmig_obj.n_pis()
        self._L = self._pmig_obj.n_latches()
        self._O = self._pmig_obj.n_pos()
        self._M = self._pmig_obj.n_majs()

        self._comments = None  # 'None' or 'Tuple consists of str'
        self._echomode = 3

        assert self._N == self._I + self._L + self._M + 1 # Const0

    def write_header(self, f):
        f.write("pmig {} {} {} {} {}\n".format(self._N, self._I, self._L, self._M, self._O))

    def write_pis(self, f):
        cnt = 0
        f.write("# PI\n")
        for pi_l in self._pmig_obj.get_iter_pis():
            if self._pmig_obj.has_name(pi_l):
                pi_l_name = self._pmig_obj.get_name_by_id(pi_l)
                f.write("{} {}\n".format(pi_l, pi_l_name))
            else:
                f.write("{}\n".format(pi_l))
            cnt = cnt + 1
        assert cnt == self._I

    def write_latches(self, f):
        cnt = 0
        f.write("# LATCH\n")
        for latch_l in self._pmig_obj.get_iter_latches():
            latch_n = self._pmig_obj.deref(latch_l)
            latch_init = latch_n.get_latch_init()
            latch_next = latch_n.get_latch_next()
            if self._pmig_obj.has_name(latch_l):
                latch_l_name = self._pmig_obj.get_name_by_id(latch_l)
                f.write("{} {} {} {}\n".format(latch_l, latch_init, latch_next, latch_l_name))
            else:
                f.write("{} {} {}\n".format(latch_l, latch_init, latch_next))
            cnt = cnt + 1
        assert cnt == self._L

    def write_pos(self, f):
        cnt = 0
        f.write("# PO\n")
        for po_iter in self._pmig_obj.get_iter_pos():
            po_fanin = po_iter[1]
            po_type = po_iter[2]
            if self._pmig_obj.po_has_name(po_iter[0]):
                po_name = self._pmig_obj.get_name_by_po(po_iter[0])
                f.write("{} {} {}\n".format(po_fanin, po_type, po_name))
            else:
                f.write("{} {}\n".format(po_fanin, po_type))
            cnt = cnt + 1
        assert cnt == self._O

    def write_majs(self, f):
        cnt = 0
        f.write("# MAJ\n")
        for maj_l in self._pmig_obj.get_iter_majs():
            maj_n = self._pmig_obj.deref(maj_l)
            maj_ch0 = maj_n.get_maj_child0()
            maj_ch1 = maj_n.get_maj_child1()
            maj_ch2 = maj_n.get_maj_child2()
            if self._pmig_obj.has_name(maj_l):
                maj_l_name = self._pmig_obj.get_name_by_id(maj_l)
                f.write("{} {} {} {} {}\n".format(maj_l, maj_ch0, maj_ch1, maj_ch2, maj_l_name))
            else:
                f.write("{} {} {} {}\n".format(maj_l, maj_ch0, maj_ch1, maj_ch2))
            cnt = cnt + 1
        assert cnt == self._M

    # def write_names(self, f):
    #     if not self._pmig_obj.is_id_to_name_empty():
    #         f.write("# Node names\n")
    #         f.write("+ nn\n")
    #         for pi_l in self._pmig_obj.get_iter_pis():
    #             if self._pmig_obj.has_name(pi_l):
    #                 f.write("{} {}\n".format(pi_l, self._pmig_obj.get_name_by_id(pi_l)))
    #         for latch_l in self._pmig_obj.get_iter_latches():
    #             if self._pmig_obj.has_name(latch_l):
    #                 f.write("{} {}\n".format(latch_l, self._pmig_obj.get_name_by_id(latch_l)))
    #         for maj_l in self._pmig_obj.get_iter_majs():
    #             if self._pmig_obj.has_name(maj_l):
    #                 f.write("{} {}\n".format(maj_l, self._pmig_obj.get_name_by_id(maj_l)))
    #
    #     if not self._pmig_obj.is_po_to_name_empty():
    #         f.write("# PO names\n")
    #         f.write("+ on\n")
    #         for po_iter in self._pmig_obj.get_iter_pos():
    #             if self._pmig_obj.po_has_name(po_iter[0]):
    #                 f.write("{} {}\n".format(po_iter[0], self._pmig_obj.get_name_by_po(po_iter[0])))

    def write_comments(self, f):
        if self._comments is not None:
            f.write("# Comments:\n")
            for c_line in self._comments:
                f.write('# ' + c_line + '\n')

    def write_to_file(self, f_name, f_path = ".", f_comments_list = None):
        #if not os.path.exists(f_path + '/' + f_name):
        if f_comments_list is not None:
            self._comments = f_comments_list


        with open(file=f_path+'/'+f_name, mode='w') as f:
            self.write_header(f)
            self.write_pis(f)
            self.write_latches(f)
            self.write_majs(f)
            self.write_pos(f)
            # self.write_names(f)
            self.write_comments(f)

class pmig_reader:
    def __init__(self, ptype_of_pmig = PMIG.PTYPE_ALL):
        self._N = 0
        self._I = 0
        self._L = 0
        self._O = 0
        self._M = 0

        self._ptype_of_pmig = ptype_of_pmig
        self._pmig_obj = graphs.PMIG(polymorphic_type=self._ptype_of_pmig)
        self._pmig_tasks = {}
        self._pmig_tasks_po = []
        self._echomode = 3
        self._pmig_task_names = []
        self._pmig_task_ponames = []

    def read_pmig(self, file_path):
        assert isinstance(file_path, str)
        cnt_line = 0
        current_po_id = 0
        self._pmig_obj = graphs.PMIG(polymorphic_type=self._ptype_of_pmig)
        self._pmig_tasks = {}
        self._pmig_tasks_po = []
        self._pmig_task_names = []
        self._pmig_task_ponames = []

        # current_line = 'data'
        for line in fileinput.input(file_path):
            if line[0] == '#':
                continue

            cnt_line = cnt_line + 1

            if cnt_line == 1:
                assert line[0] == 'p'
                assert line[1] == 'm'
                assert line[2] == 'i'
                assert line[3] == 'g'
                assert line [4] == ' '
                line_number = line[5:]
                line_list = []
                line_list.extend([int(i) for i in line_number.split()])
                assert len(line_list) == 5
                self._N = line_list[0]
                self._I = line_list[1]
                self._L = line_list[2]
                self._M = line_list[3]
                self._O = line_list[4]
                assert self._N == self._I + self._L + self._M + 1
                if self._echomode > 1: print("[INFO] graph_io/pmig_reader: Read header - ", self._N, self._I, self._L, self._M, self._O)

            elif 1 < cnt_line < 2 + self._I:
                # self.read_pi(line, cnt_line)
                line_list = []
                line_list = line.rstrip('\n').split(' ')
                # assert len(line_list) == 1
                line_list[0] = int(line_list[0])
                assert int(line_list[0]) % 4 == 0
                id = line_list[0] >> 2
                assert not id in self._pmig_tasks
                if len(line_list) == 1:
                    self._pmig_tasks[id] = ('pi', )
                elif len(line_list) == 2:
                    self._pmig_tasks[id] = ('pi', )
                    self._pmig_task_names.append( (line_list[0], line_list[1]) )
                else:
                    assert False


            elif 1 + self._I < cnt_line < 2 + self._I + self._L:
                # self.read_latch(line, cnt_line)
                line_list = []
                line_list = line.rstrip('\n').split(' ')
                # assert len(line_list) == 3
                line_list[0] = int(line_list[0])
                line_list[1] = int(line_list[1])
                line_list[2] = int(line_list[2])
                assert int(line_list[0]) % 4 == 0
                id = int(line_list[0]) >> 2
                assert not id in self._pmig_tasks
                if len(line_list) == 3:
                    self._pmig_tasks[id] = ('latch', line_list[1], line_list[2])
                elif len(line_list) == 4:
                    self._pmig_tasks[id] = ('latch', line_list[1], line_list[2])
                    self._pmig_task_names.append( (line_list[0], line_list[3]) )
                else:
                    assert False

            elif 1 + self._I + self._L < cnt_line < 2 + self._I + self._L + self._M:
                # self.read_maj(line, cnt_line)
                line_list = []
                line_list = line.rstrip('\n').split(' ')
                # assert len(line_list) == 4
                line_list[0] = int(line_list[0])
                line_list[1] = int(line_list[1])
                line_list[2] = int(line_list[2])
                line_list[3] = int(line_list[3])
                assert line_list[0] % 4 == 0
                id = int(line_list[0]) >> 2
                assert not id in self._pmig_tasks
                if len(line_list) == 4:
                    self._pmig_tasks[id] = ('maj', line_list[1], line_list[2], line_list[3])
                elif len(line_list) == 5:
                    self._pmig_tasks[id] = ('maj', line_list[1], line_list[2], line_list[3])
                    self._pmig_task_names.append( (line_list[0], line_list[4]) )


            elif 1 + self._I + self._L + self._M < cnt_line < 2 + self._I + self._L + self._M + self._O:
                # self.read_po(line, cnt_line)
                line_list = []
                line_list = line.rstrip('\n').split(' ')
                # assert len(line_list) == 2
                line_list[0] = int(line_list[0])
                line_list[1] = int(line_list[1])
                # assert line_list[0] % 4 == 0
                # id = line_list[0] >> 2
                assert not line_list[0] in self._pmig_tasks_po
                if len(line_list) == 2:
                    self._pmig_tasks_po.append( (line_list[0], line_list[1]) )
                elif len(line_list) == 3:
                    self._pmig_tasks_po.append((line_list[0], line_list[1]))
                    self._pmig_task_ponames.append( (current_po_id, line_list[2]) )
                current_po_id = current_po_id + 1

            # elif line[0] == '+':
            #     if line[2] == 'n' and line[3] == 'n':
            #         current_line = 'node name'
            #     elif line[2] == 'o' and line[3] == 'n':
            #         current_line = 'output name'
            #     else:
            #         assert False, "Undefined '+ ...' line."

            else:
                line_strip = line.strip()
                assert len(line_strip) == 0
                # if current_line == 'node name':
                #     # self.read_nodename(line)
                #     self._pmig_task_names.append(line.rstrip('\n'))
                # elif current_line == 'output name':
                #     # self.read_poname(line)
                #     self._pmig_task_ponames.append(line.rstrip('\n'))

        assert len(self._pmig_tasks) == self._N - 1
        for idx in range(1, self._N):
            task = self._pmig_tasks[idx]
            task_type = task[0]
            if task_type == 'pi':
                self._pmig_obj.create_pi()
                if self._echomode > 1:
                    print("[INFO] graph_io/pmig_reader: Create PI: ", task)
                assert self._pmig_obj.deref(idx << 2).is_pi()


            elif task_type == 'latch':
                self._pmig_obj.create_latch(init=task[1], next=task[2])
                if self._echomode > 1:
                    print("[INFO] graph_io/pmig_reader: Create LATCH: ", task)
                assert self._pmig_obj.deref(idx << 2).is_latch()


            elif task_type == 'maj':
                self._pmig_obj.create_maj(task[1], task[2], task[3])
                if self._echomode > 1:
                    print("[INFO] graph_io/pmig_reader: Create MAJ: ", task)
                assert self._pmig_obj.deref(idx << 2).is_maj()

            else:
                assert False


            assert self._pmig_obj.n_nodes() == idx + 1



        assert len(self._pmig_tasks_po) == self._O
        for task in self._pmig_tasks_po:
            self._pmig_obj.create_po(f=task[0], po_type=task[1])
            if self._echomode > 1:
                print("[INFO] graph_io/pmig_reader: Create PO: ", task)

        for line in self._pmig_task_names:
            self.read_nodename(line)

        for line in self._pmig_task_ponames:
            self.read_poname(line)

        return self._pmig_obj

    def read_nodename(self, line):
        nodename_list = line
        assert len(nodename_list) == 2
        self._pmig_obj.set_name(int(nodename_list[0]), nodename_list[1])
        if self._echomode > 1:
            print("[INFO] graph_io/pmig_reader: Set name: ", line)

    def read_poname(self, line):
        poname_list = line
        assert len(poname_list) == 2
        self._pmig_obj.set_po_name(int(poname_list[0]), poname_list[1])
        if self._echomode > 1:
            print("[INFO] graph_io/pmig_reader: Set PO name: ", line)











########################################################################################################################
# AIG_IO
#
# @Time    : 2021/5/26
# @Author  : c
#
# Based on PyAIG (https://github.com/sterin/pyaig). Timestamp: 26 Jul 2020.
# @Author: Baruch Sterin <sterin@berkeley.edu>
# Simple Python AIG readers and writers
#
########################################################################################################################
class _aiger_writer(object):

    def __init__(self, I, L, O, A, B, C, J, F):

        self._bytes = bytearray()

        M = I + L + A
        self._bytes.extend(b"aig %d %d %d %d %d" % (M, I, L, O, A))

        if B + C + J + F > 0:
            self._bytes.extend(b" %d" % B)

        if C + J + F > 0:
            self._bytes.extend(b" %d" % C)

        if J + F > 0:
            self._bytes.extend(b" %d" % J)

        if F > 0:
            self._bytes.extend(b" %d" % F)

        self._bytes.extend(b'\n')

        self._M = M
        self._I = I
        self._L = L
        self._O = O
        self._A = A
        self._B = B
        self._C = C
        self._J = J
        self._F = F

        self._next = (I + 1) << 1

    def get_bytes(self):
        return self._bytes

    def write_inputs(self):
        pass

    def write_latch(self, next, init):
        if init == AIG.INIT_ZERO:
            self._bytes.extend(b"%d\n" % next)
        elif init == AIG.INIT_ONE:
            self._bytes.extend(b"%d 1\n" % next)
        else:
            self._bytes.extend(b"%d %d\n" % (next, self._next))

        self._next += 2

    def write_po(self, po):
        self._bytes.extend(b"%d\n" % po)

    def write_justice_header(self, pos):
        self._bytes.extend(b"%d\n" % len(pos))

    def write_and(self, left, right):
        if left < right:
            left, right = right, left

        self._encode(self._next - left)
        self._encode(left - right)

        self._next += 2

    def write_input_name(self, i, name):
        self._bytes.extend(b"i%d %s\n" % (i, self._encode_str(name)))

    def write_latch_name(self, i, name):
        self._bytes.extend(b"l%d %s\n" % (i, self._encode_str(name)))

    def write_po_name(self, po_type, i, name):
        self._bytes.extend(b"%s%d %s\n" % (po_type, i, self._encode_str(name)))

    def _encode(self, x):

        while (x & ~0x7f) > 0:
            self._bytes.append((x & 0x7f) | 0x80)
            x >>= 7

        self._bytes.append(x)

    def _encode_str(self, s):
        if isinstance(s, bytes):
            return s
        return s.encode('utf-8')


def write_aiger_file(aig, fout):
    map_aiger = {}

    aiger_i = 0

    map_aiger[0] = aiger_i
    aiger_i += 1

    for pi in aig.get_pis():
        map_aiger[pi] = (aiger_i << 1)
        aiger_i += 1

    for l in aig.get_latches():
        map_aiger[l] = (aiger_i << 1)
        aiger_i += 1

    for g in aig.get_nonterminals():
        map_aiger[g] = (aiger_i << 1)
        aiger_i += 1

    def aiger_lit(aig_lit):

        lit_pos = aig.get_positive(aig_lit)
        lit = map_aiger[lit_pos]

        if aig.is_negated(aig_lit):
            return lit + 1
        else:
            return lit

    writer = _aiger_writer(
        aig.n_pis(),
        aig.n_latches(),
        aig.n_pos_by_type(AIG.OUTPUT),
        aig.n_nonterminals(),
        aig.n_pos_by_type(AIG.BAD_STATES),
        aig.n_pos_by_type(AIG.CONSTRAINT),
        aig.n_justice(),
        aig.n_pos_by_type(AIG.FAIRNESS),
    )

    writer.write_inputs()

    for l in aig.get_latches():
        writer.write_latch(aiger_lit(aig.get_next(l)), aig.get_init(l))

    for po in aig.get_po_fanins_by_type(AIG.OUTPUT):
        writer.write_po(aiger_lit(po))

    for po in aig.get_po_fanins_by_type(AIG.BAD_STATES):
        writer.write_po(aiger_lit(po))

    for po in aig.get_po_fanins_by_type(AIG.CONSTRAINT):
        writer.write_po(aiger_lit(po))

    for _, j_pos in aig.get_justice_properties():
        writer.write_justice_header(j_pos)

    for _, j_pos in aig.get_justice_properties():
        for po_id in j_pos:
            writer.write_po(aiger_lit(aig.get_po_fanin(po_id)))

    for po in aig.get_po_fanins_by_type(AIG.FAIRNESS):
        writer.write_po(aiger_lit(po))

    for g in aig.get_nonterminals():
        n = aig.deref(g)
        if n.is_buffer():
            al = ar = aiger_lit(n.get_buf_in())
        else:
            al = aiger_lit(n.get_left())
            ar = aiger_lit(n.get_right())
        writer.write_and(al, ar)

    # Write symbol table

    for i, pi in enumerate(aig.get_pis()):
        if aig.has_name(pi):
            writer.write_input_name(i, aig.get_name_by_id(pi))

    for i, l in enumerate(aig.get_latches()):
        if aig.has_name(l):
            writer.write_latch_name(i, aig.get_name_by_id(l))

    for i, (po_id, _, _) in enumerate(aig.get_pos_by_type(AIG.OUTPUT)):
        if aig.po_has_name(po_id):
            writer.write_po_name(b'o', i, aig.get_name_by_po(po_id))

    for i, (po_id, _, _) in enumerate(aig.get_pos_by_type(AIG.BAD_STATES)):
        if aig.po_has_name(po_id):
            writer.write_po_name(b'b', i, aig.get_name_by_po(po_id))

    for i, (po_id, _, _) in enumerate(aig.get_pos_by_type(AIG.CONSTRAINT)):
        if aig.po_has_name(po_id):
            writer.write_po_name(b'c', i, aig.get_name_by_po(po_id))

    for i, po_ids in aig.get_justice_properties():

        if not po_ids:
            continue

        po_id = po_ids[0]

        if aig.po_has_name(po_id):
            writer.write_po_name(b'j', i, aig.get_name_by_po(po_id))

    for i, (po_id, _, _) in enumerate(aig.get_pos_by_type(AIG.FAIRNESS)):
        if aig.po_has_name(po_id):
            writer.write_po_name(b'f', i, aig.get_name_by_po(po_id))

    fout.write(writer.get_bytes())

    return map_aiger


def write_aiger(aig, f):
    if type(f) == str:
        with open(f, "wb") as fout:
            return write_aiger_file(aig, fout)
    else:
        return write_aiger_file(aig, f)


def flatten_aiger(aig):
    f = io.BytesIO()
    write_aiger_file(aig, f)
    return f.getvalue()


def write_cnf(aig, fout):
    map_cnf = {}

    # const 0

    cnf_i = 1

    map_cnf[0] = cnf_i
    cnf_i += 1

    for pi in aig.get_pis():
        map_cnf[pi] = cnf_i
        cnf_i += 1

    for l in aig.get_latches():
        map_cnf[l] = cnf_i
        cnf_i += 1

    for g in aig.get_and_gates():
        map_cnf[g] = cnf_i
        cnf_i += 1

    fout.write("p %d %d\n" % (cnf_i, aig.n_ands() * 3 + 1 + aig.n_pos()))

    fout.write("-1 0\n")

    def lit(aig_lit):
        lit_pos = aig.get_positive(aig_lit)
        lit_cnf = map_cnf[lit_pos]

        if aig.is_negated(aig_lit):
            return -lit_cnf
        else:
            return lit_cnf

    for po in aig.get_po_fanins():
        fout.write("%d 0\n" % lit(po))

    for g in aig.get_and_gates():
        n = aig.deref(g)

        x = lit(g)
        y = lit(n.get_left())
        z = lit(n.get_right())

        fout.write("%d %d 0\n" % (-x, y))
        fout.write("%d %d 0\n" % (-x, z))
        fout.write("%d %d %d 0\n" % (x, -y, -z))


def write_tecla(aig, fout):
    def get_lit(f):
        if f == aig.get_const0():
            return 'FALSE'
        elif f == aig.get_const1():
            return 'TRUE'

        if aig.is_negated(f):
            neg = '~'
        else:
            neg = ''

        if aig.is_pi(f):
            c = 'I'
        elif aig.is_and(f):
            c = 'N'
        elif aig.is_latch(f):
            c = 'L'

        return '%s%s%d' % (neg, c, aig.get_id(f))

    fout.write('definitions:\n\n')

    for l in aig.get_latches():
        fout.write('  I(%s) := FALSE ;\n' % get_lit(l))

    fout.write('\n')

    for a in aig.get_and_gates():
        n = aig.deref(a)

        fout.write(
            '  %s := %s & %s ;\n' % (
                get_lit(a),
                get_lit(n.get_left()),
                get_lit(n.get_right())
            )
        )

    fout.write('\n')

    for l in aig.get_latches():
        n = aig.deref(l)

        fout.write(
            '  X(%s) := %s ;\n' % (
                get_lit(l),
                get_lit(n.get_next()),
            )
        )

    fout.write('\nproof obligations:\n\n')

    for po in aig.get_pos():
        fout.write('  %s ;\n' % get_lit(po))


def is_sat(aig):
    p = subprocess.Popen("minisat", stdin=subprocess.PIPE, close_fds=True, shell=True)
    fout = p.stdin
    write_cnf(fout)
    fout.close()


def read_aiger_file(fin):
    aig = AIG()

    header = fin.readline().split()
    assert header[0] == b'aig'

    args = [int(t) for t in header[1:]]
    (M, I, L, O, A) = args[:5]

    B = args[5] if len(args) > 5 else 0
    C = args[6] if len(args) > 6 else 0
    J = args[7] if len(args) > 7 else 0
    F = args[8] if len(args) > 8 else 0

    vars = []
    nexts = []

    pos_output = []
    pos_bad_states = []
    pos_constraint = []
    pos_justice = []
    pos_fairness = []

    vars.append(aig.get_const0())

    for i in xrange(I):
        vars.append(aig.create_pi())

    def parse_latch(line):

        tokens = line.strip().split(b' ')

        next = int(tokens[0])
        init = 0

        if len(tokens) == 2:

            if tokens[1] == '0':
                init = AIG.INIT_ZERO
            if tokens[1] == '1':
                init = AIG.INIT_ONE
            else:
                init = AIG.INIT_NONDET

        return (next, init)

    for i in xrange(L):
        vars.append(aig.create_latch())
        nexts.append(parse_latch(fin.readline()))

    for i in xrange(O):
        pos_output.append(int(fin.readline()))

    for i in xrange(B):
        pos_bad_states.append(int(fin.readline()))

    for i in xrange(C):
        pos_constraint.append(int(fin.readline()))

    n_j_pos = []

    for i in xrange(J):
        n_j_pos.append(int(fin.readline()))

    for n in n_j_pos:
        pos = []
        for i in xrange(n):
            pos.append(int(fin.readline()))
        pos_justice.append(pos)

    for i in xrange(F):
        pos_fairness.append(int(fin.readline()))

    def decode():

        i = 0
        res = 0

        while True:

            c = ord(fin.read(1))

            res |= ((c & 0x7F) << (7 * i))

            if (c & 0x80) == 0:
                break

            i += 1

        return res

    def lit(x):
        return aig.negate_if(vars[x >> 1], x & 0x1)

    for i in xrange(I + L + 1, I + L + A + 1):
        d1 = decode()
        d2 = decode()
        g = i << 1
        vars.append(aig.create_and(lit(g - d1), lit(g - d1 - d2)))

    for l, v in enumerate(xrange(I + 1, I + L + 1)):
        aig.set_latch_init(vars[v], nexts[l][1])
        aig.set_latch_next(vars[v], lit(nexts[l][0]))

    output_pos = []

    for po in pos_output:
        output_pos.append(aig.create_po(lit(po), po_type=AIG.OUTPUT))

    bad_states_pos = []

    for po in pos_bad_states:
        bad_states_pos.append(aig.create_po(lit(po), po_type=AIG.BAD_STATES))

    constraint_pos = []

    for po in pos_constraint:
        constraint_pos.append(aig.create_po(lit(po), po_type=AIG.CONSTRAINT))

    for pos in pos_justice:
        po_ids = [aig.create_po(lit(po), po_type=AIG.JUSTICE) for po in pos]
        aig.create_justice(po_ids)

    fairness_pos = []

    for po in pos_fairness:
        fairness_pos.append(aig.create_po(lit(po), po_type=AIG.FAIRNESS))

    names = set()
    po_names = set()

    for line in fin:
        m = re.match(b'i(\\d+) (.*)', line)
        if m:
            if m.group(2) not in names:
                aig.set_name(vars[int(m.group(1)) + 1], m.group(2))
                names.add(m.group(2))
            continue

        m = re.match(b'l(\\d+) (.*)', line)
        if m:
            if m.group(2) not in names:
                aig.set_name(vars[I + int(m.group(1)) + 1], m.group(2))
                names.add(m.group(2))
            continue

        m = re.match(b'o(\\d+) (.*)', line)
        if m:
            if m.group(2) not in po_names:
                aig.set_po_name(output_pos[int(m.group(1))], m.group(2))
                po_names.add(m.group(2))
            continue

        m = re.match(b'b(\\d+) (.*)', line)
        if m:
            if m.group(2) not in po_names:
                aig.set_po_name(bad_states_pos[int(m.group(1))], m.group(2))
                po_names.add(m.group(2))
            continue

        m = re.match(b'c(\\d+) (.*)', line)
        if m:
            if m.group(2) not in po_names:
                aig.set_po_name(constraint_pos[int(m.group(1))], m.group(2))
                po_names.add(m.group(2))
            continue

        m = re.match(b'f(\\d+) (.*)', line)
        if m:
            if m.group(2) not in po_names:
                aig.set_po_name(fairness_pos[int(m.group(1))], m.group(2))
                po_names.add(m.group(2))
            continue

    return aig


def read_aiger(f):
    if type(f) == str:
        with open(f, "rb") as fin:
            return read_aiger_file(fin)
    else:
        return read_aiger_file(f)


def unflatten_aiger(buf):
    return read_aiger_file(io.BytesIO(buf))


def marshal_aiger(aig):
    data = bytearray()

    def putu(x):
        while x >= 0x80:
            data.append(x & 0x7F | 0x80)
            x >>= 7
        data.append(x)

    M = AIG.fmap(negate_if_negated=lambda f, c: f ^ c)

    # Constants

    n_const = 2
    M[AIG.get_const1()] = 2

    # PIs

    n_pis = aig.n_pis()
    putu(n_pis)

    for i, pi in enumerate(aig.get_pis()):
        M[pi] = (n_const + i) << 1

    # Latches

    n_latches = aig.n_latches()
    putu(n_latches)

    for i, ll in enumerate(aig.get_latches()):
        M[ll] = (n_const + n_pis + i) << 1

    # Gates

    n_ands = aig.n_ands()
    putu(n_ands)

    for i, f in enumerate(aig.get_and_gates()):
        putu(M[aig.get_and_right(f)] << 1)
        putu(M[aig.get_and_left(f)])

        M[f] = (n_const + n_pis + n_latches + i) << 1

    # Latches

    V = {AIG.INIT_NONDET: 0, AIG.INIT_ZERO: 2, AIG.INIT_ONE: 3}

    for ll in aig.get_latches():
        putu((M[aig.get_next(ll)] << 2) | V[aig.get_init(ll)])

    # Properties

    output_pos = list(aig.get_pos_by_type(AIG.OUTPUT))
    bad_pos = list(aig.get_pos_by_type(AIG.BAD_STATES))
    constraint_pos = list(aig.get_pos_by_type(AIG.CONSTRAINT))
    fairness_pos = list(aig.get_pos_by_type(AIG.FAIRNESS))
    justice_pos = list(aig.get_pos_by_type(AIG.JUSTICE))
    justice_properties = list(aig.get_justice_properties())

    if len(bad_pos) == 0 and len(justice_properties) == 0 and len(output_pos) > 0:
        bad_pos = output_pos

    putu(len(bad_pos))
    for po_id, po_fanin, po_type in bad_pos:
        putu(M[po_fanin] ^ 1)

    # Fairness

    putu(1)

    total = len(justice_pos) + len(justice_properties) * (len(fairness_pos) + 1)
    putu(total)

    for i, po_ids in justice_properties:

        for po_id in po_ids:
            putu(M[aig.get_po_fanin(po_id)])

        for po_id, po_fanin, po_type in fairness_pos:
            putu(M[po_fanin])

        putu(0)

    # Constraints

    putu(len(constraint_pos))
    for po_id, po_fanin, po_type in constraint_pos:
        putu(M[po_fanin])

    return data


class archive(object):

    def __init__(self, data):

        self.data = data
        self.pos = 0

    def get_next(self):

        c = self.data[self.pos]
        self.pos += 1

        return c

    def getu(self):

        x = 0
        shift = 0
        while True:
            c = self.get_next()
            x |= (c & 0x7F) << shift
            shift += 7
            if c < 0x80:
                return x


class ifmap(object):

    def __init__(self):
        self.m = {}

    def __getitem__(self, i):
        return AIG.negate_if(self.m[i & ~1], i & 1)

    def __setitem__(self, i, f):
        self.m[i & ~1] = AIG.negate_if(f, i & 1)


def unmarshal_aiger(data):
    a = archive(data)

    aig = AIG()
    M = ifmap()

    # Constants

    n_const = 2
    M[2] = AIG.get_const1()

    # PIs

    n_pis = a.getu()

    for i in xrange(n_pis):
        M[(n_const + i) << 1] = aig.create_pi()

    # Latches

    n_latches = a.getu()

    for i in xrange(n_latches):
        M[(n_const + n_pis + i) << 1] = aig.create_latch()

    # Gates

    n_ands = a.getu()

    for i in xrange(n_ands):
        f0 = M[a.getu() >> 1]
        f1 = M[a.getu()]
        M[(n_const + n_pis + n_latches + i) << 1] = aig.create_and(f0, f1)

    # Latches

    V = {0: AIG.INIT_NONDET, 2: AIG.INIT_ZERO, 3: AIG.INIT_ONE}

    for ll in aig.get_latches():
        u = a.getu()
        aig.set_latch_init(ll, V[u & 3])
        aig.set_latch_next(ll, M[u >> 2])

    # Properties

    n_props = a.getu()
    for i in xrange(n_props):
        aig.create_po(M[a.getu() ^ 1], po_type=AIG.BAD_STATES)

    # Liveness

    fair_version = a.getu()
    assert fair_version == 1

    fair_total = a.getu()
    cur_justice = []

    for i in xrange(fair_total):
        u = a.getu()
        if u > 0:
            cur_justice.append(aig.create_po(M[u], po_type=AIG.JUSTICE))
        else:
            aig.create_justice(cur_justice)
            cur_justice = []

    # Constraints

    n_constr = a.getu()
    for i in xrange(n_constr):
        aig.create_po(M[a.getu() ^ 1], po_type=AIG.CONSTRAINT)

    return aig
