# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/5/23
# @Author  : c
# @File    : graphs.py
#
# Definitions of AIG and PMIG

import itertools


########################################################################################################################
# class _AIG_Node
#
# @Time    : 2021/5/24
# @Author  : c
#
# Based on the code on PyAIG (https://github.com/sterin/pyaig). Timestamp: 26 Jul 2020.
# @Author: Baruch Sterin <sterin@berkeley.edu>
#
########################################################################################################################
class _AIG_Node:

    # Node types
    CONST0 = 0
    PI = 1
    LATCH = 2
    AND = 3
    BUFFER = 4

    # Latch Initialization
    INIT_ZERO = 0
    INIT_ONE = 1
    INIT_NONDET = 2

    def __init__(self, node_type, left = 0, right = 0):
        self._type = node_type
        self._left = left
        self._right = right

    # creation

    @staticmethod
    def make_const0():
        return _AIG_Node(_AIG_Node.CONST0)

    @staticmethod
    def make_pi(pi_id):
        return _AIG_Node(_AIG_Node.PI, pi_id, 0)

    @staticmethod
    def make_latch(l_id, init, next=None):
        return _AIG_Node(_AIG_Node.LATCH, l_id, (init, next))

    @staticmethod
    def make_and(left, right):
        return _AIG_Node(_AIG_Node.AND, left, right)

    @staticmethod
    def make_buffer(buf_id, buf_in):
        return _AIG_Node(_AIG_Node.BUFFER, buf_id, buf_in)

    # query type

    def is_const0(self):
        return self._type == _AIG_Node.CONST0

    def is_pi(self):
        return self._type == _AIG_Node.PI

    def is_latch(self):
        return self._type == _AIG_Node.LATCH

    def is_and(self):
        return self._type == _AIG_Node.AND

    def is_buffer(self):
        return self._type == _AIG_Node.BUFFER

    def is_nonterminal(self):
        return self._type in (_AIG_Node.AND, _AIG_Node.BUFFER)

    def get_fanins(self):
        if self._type == _AIG_Node.AND:
            return [self._left, self._right]
        elif self._type == _AIG_Node.BUFFER:
            return [self._right]
        else:
            return []

    def get_seq_fanins(self):
        if self._type == _AIG_Node.AND:
            return [self._left, self._right]
        elif self._type == _AIG_Node.BUFFER:
            return [self._right]
        elif self._type == _AIG_Node.LATCH:
            return [self._right[1]]
        else:
            return []

    # AND gates

    def get_left(self):
        assert self.is_and()
        return self._left

    def get_right(self):
        assert self.is_and()
        return self._right

    # Buffer

    def get_buf_id(self):
        return self._left

    def get_buf_in(self):
        assert self.is_buffer()
        return self._right

    def set_buf_in(self, f):
        assert self.is_buffer()
        self._right = f

    def convert_buf_to_pi(self, pi_id):
        assert self.is_buffer()
        self._type = _AIG_Node.PI
        self._left = pi_id
        self._right = 0

    # PIs

    def get_pi_id(self):
        assert self.is_pi()
        return self._left

    # Latches

    def get_latch_id(self):
        assert self.is_latch()
        return self._left

    def get_latch_init(self):
        assert self.is_latch()
        return self._right[0]

    def get_latch_next(self):
        assert self.is_latch()
        return self._right[1]

    def set_latch_init(self, init):
        assert self.is_latch()
        self._right = (init, self._right[1])

    def set_latch_next(self, f):
        assert self.is_latch()
        self._right = (self._right[0], f)

    def __repr__(self):
        type = "ERROR"
        if self._type == _AIG_Node.AND:
            type = "AND"
        elif self._type == _AIG_Node.BUFFER:
            type = "BUFFER"
        elif self._type == _AIG_Node.CONST0:
            type = "CONST0"
        elif self._type == _AIG_Node.LATCH:
            type = "LATCH"
        elif self._type == _AIG_Node.PI:
            type = "PI"
        return "<pmig.graph._AIG_Node _type=%s, _left=%s, _right=%s>" % (type, str(self._left), str(self._right))


########################################################################################################################
# class AIG
#
# @Time    : 2021/5/25
# @Author  : c
#
# Based on the code on PyAIG (https://github.com/sterin/pyaig). Timestamp: 26 Jul 2020.
# @Author: Baruch Sterin <sterin@berkeley.edu>
#
########################################################################################################################
class AIG:

    # map AIG nodes to AIG nodes, take negation into account

    class fmap:

        def __init__(self, fs=[], negate_if_negated=None, zero=None):
            self.negate_if_negated = negate_if_negated if negate_if_negated else AIG.negate_if_negated
            zero = AIG.get_const0() if zero is None else zero
            self.m = {AIG.get_const0(): zero}
            if fs:
                self.update(fs)

        def __getitem__(self, f):
            return self.negate_if_negated(self.m[AIG.get_positive(f)], f)

        def __setitem__(self, f, g):
            self.m[AIG.get_positive(f)] = self.negate_if_negated(g, f)

        def __contains__(self, f):
            return AIG.get_positive(f) in self.m

        def __delitem__(self, f):
            del self.m[AIG.get_positive(f)]

        def iteritems(self):
            # return iteritems(self.m)
            return self.m.items()

        def update(self, fs):
            self.m.update((AIG.get_positive(f), self.negate_if_negated(g, f)) for f, g in fs)

    class fset:

        def __init__(self, fs=[]):
            self.s = set(AIG.get_positive(f) for f in fs)

        def __contains__(self, f):
            return AIG.get_positive(f) in self.s

        def __len__(self):
            return len(self.s)

        def __iter__(self):
            return self.s.__iter__()

        def add(self, f):
            f = AIG.get_positive(f)
            res = f in self.s
            self.s.add(f)
            return res

        def remove(self, f):
            return self.s.remove(AIG.get_positive(f))

    # PO types

    OUTPUT = 0
    BAD_STATES = 1
    CONSTRAINT = 2
    JUSTICE = 3
    FAIRNESS = 4

    # Latch initialization

    INIT_ZERO = _AIG_Node.INIT_ZERO
    INIT_ONE = _AIG_Node.INIT_ONE
    INIT_NONDET = _AIG_Node.INIT_NONDET

    def __init__(self, name=None, flat_name=(lambda n: n)):
        self._name = name
        self._strash = {}
        self._pis = []
        self._latches = []
        self._buffers = []
        self._pos = []
        self._justice = []
        self._nodes = []
        self._name_to_id = {}
        self._id_to_name = {}
        self._name_to_po = {}
        self._po_to_name = {}
        self._flat_name = flat_name
        self._fanouts = {}

        self._nodes.append(_AIG_Node.make_const0())

    def deref(self, f):
        return self._nodes[f >> 1]

    def name(self):
        return self._name

    # Create basic objects

    @staticmethod
    def get_const(c):
        if c:
            return AIG.get_const1()
        return AIG.get_const0()

    @staticmethod
    def get_const0():
        return 0

    @staticmethod
    def get_const1():
        return 1

    def create_pi(self, name=None):
        pi_id = len(self._pis)
        n = _AIG_Node.make_pi(pi_id) # Generate a _AIG_Node obj
        fn = len(self._nodes) << 1

        self._nodes.append(n)
        self._pis.append(fn)

        if name is not None:
            self.set_name(fn, name)

        return fn

    def create_latch(self, name=None, init=INIT_ZERO, next=None):
        l_id = len(self._latches)
        n = _AIG_Node.make_latch(l_id, init, next)
        fn = len(self._nodes) << 1

        self._nodes.append(n)
        self._latches.append(fn)

        if name is not None:
            self.set_name(fn, name)

        return fn

    def create_and(self, left, right):
        if left < right:
            left, right = right, left

        if right == 0:
            return 0

        if right == 1:
            return left

        if left == right:
            return right

        if left == (right ^ 1):
            return 0

        key = (_AIG_Node.AND, left, right)

        if key in self._strash:
            return self._strash[key]

        f = len(self._nodes) << 1
        self._nodes.append(_AIG_Node.make_and(left, right))

        self._strash[key] = f

        return f

    def create_buffer(self, buf_in=0, name=None):
        b_id = len(self._buffers)
        f = len(self._nodes) << 1

        self._nodes.append(_AIG_Node.make_buffer(b_id, buf_in))
        self._buffers.append(f)

        if name is not None:
            self.set_name(f, name)

        return f

    def convert_buf_to_pi(self, buf):
        assert self.is_buffer(buf)
        assert self.get_buf_in(buf) >= 0

        n = self.deref(buf)
        self._buffers[n.get_buf_id()] = -1
        n.convert_buf_to_pi(len(self._pis))
        self._pis.append(buf)

    def create_po(self, f=0, name=None, po_type=OUTPUT):
        po_id = len(self._pos)
        self._pos.append((f, po_type))

        if name is not None:
            self.set_po_name(po_id, name)

        return po_id

    def create_justice(self, po_ids):
        po_ids = list(po_ids)

        j_id = len(self._justice)

        for po_id in po_ids:
            assert self.get_po_type(po_id) == AIG.JUSTICE

        self._justice.append(po_ids)

        return j_id

    def remove_justice(self):

        for po_ids in self._justice:
            for po_id in po_ids:
                self.set_po_type(po_id, AIG.OUTPUT)

        self._justice = []

    # Names

    def set_name(self, f, name):
        assert not self.is_negated(f)
        assert name not in self._name_to_id
        assert f not in self._id_to_name

        self._name_to_id[name] = f
        self._id_to_name[f] = name

    def get_id_by_name(self, name):
        return self._name_to_id[name]

    def has_name(self, f):
        return f in self._id_to_name

    def name_exists(self, n):
        return n in self._name_to_id

    def get_name_by_id(self, f):
        return self._id_to_name[f]

    def remove_name(self, f):
        assert self.has_name(f)
        name = self.get_name_by_id(f)

        del self._id_to_name[f]
        del self._name_to_id[name]

    def iter_names(self):
        # return iteritems(self._id_to_name)
        #
        # dict.iteritems() returns an iterator of the dictionary’s list.
        # It is a python 2 version feature and got omitted in the Python 3 versions.
        #
        # Replaced by dict.items() – This function returns a copy of the dictionary’s list.
        return self._id_to_name.items()

    def fill_pi_names(self, replace=False, template="I_{}"):

        if replace:
            for pi in self.get_pis():
                if self.has_name(pi):
                    self.remove_name(pi)

        uid = 0

        for pi in self.get_pis():
            if not self.has_name(pi):
                while True:
                    name = template.format(uid)
                    uid += 1
                    if not self.name_exists(name):
                        break
                self.set_name(pi, name)

    # PO names

    def set_po_name(self, po, name):
        assert 0 <= po < len(self._pos)
        assert name not in self._name_to_po
        assert po not in self._po_to_name

        self._name_to_po[name] = po
        self._po_to_name[po] = name

    def get_po_by_name(self, name):
        return self._name_to_po[name]

    def po_has_name(self, po):
        return po in self._po_to_name

    def name_has_po(self, po):
        return po in self._name_to_po

    def remove_po_name(self, po):
        assert self.po_has_name(po)
        name = self.get_name_by_po(po)
        del self._name_to_po[name]
        del self._po_to_name[po]

    def get_name_by_po(self, po):
        return self._po_to_name[po]

    def iter_po_names(self):
        # return ((po_id, self.get_po_fanin(po_id), po_name) for po_id, po_name in iteritems(self._po_to_name))
        return ((po_id, self.get_po_fanin(po_id), po_name) for po_id, po_name in self._po_to_name.items())

    def fill_po_names(self, replace=False, template="O_{}"):

        if replace:
            self._name_to_po.clear()
            self._po_to_name.clear()

        po_names = set(name for _, _, name in self.iter_po_names())

        uid = 0
        for po_id, _, _ in self.get_pos():
            if not self.po_has_name(po_id):
                while True:
                    name = template.format(uid)
                    uid += 1
                    if name not in po_names:
                        break
                self.set_po_name(po_id, name)

    # Query IDs

    @staticmethod
    def get_id(f):
        return f >> 1

    def is_const0(self, f):
        n = self.deref(f)
        return n.is_const0()

    def is_pi(self, f):
        n = self.deref(f)
        return n.is_pi()

    def is_latch(self, f):
        n = self.deref(f)
        return n.is_latch()

    def is_and(self, f):
        n = self.deref(f)
        return n.is_and()

    def is_buffer(self, f):
        n = self.deref(f)
        return n.is_buffer()

    # PIs

    def get_pi_by_id(self, pi_id):
        return self._pis[pi_id]

    # Get/Set next for latches

    def set_latch_init(self, l, init):
        assert not self.is_negated(l)
        assert self.is_latch(l)
        n = self.deref(l)
        n.set_latch_init(init)

    def set_latch_next(self, l, f):
        assert not self.is_negated(l)
        assert self.is_latch(l)
        n = self.deref(l)
        n.set_latch_next(f)

    def get_latch_init(self, l):
        assert not self.is_negated(l)
        assert self.is_latch(l)
        n = self.deref(l)
        return n.get_latch_init()

    def get_latch_next(self, l):
        assert not self.is_negated(l)
        assert self.is_latch(l)
        n = self.deref(l)
        return n.get_latch_next()

    # And gate

    def get_and_fanins(self, f):
        assert self.is_and(f)
        n = self.deref(f)
        return (n.get_left(), n.get_right())

    def get_and_left(self, f):
        assert self.is_and(f)
        return self.deref(f).get_left()

    def get_and_right(self, f):
        assert self.is_and(f)
        return self.deref(f).get_right()

    # Buffer

    def get_buf_in(self, b):
        n = self.deref(b)
        return n.get_buf_in()

    def set_buf_in(self, b, f):
        assert b > f
        n = self.deref(b)
        return n.set_buf_in(f)

    def get_buf_id(self, b):
        n = self.deref(b)
        return n.get_buf_id()

    def skip_buf(self, b):
        while self.is_buffer(b):
            b = AIG.negate_if_negated(self.get_buf_in(b), b)
        return b

    # Fanins

    def get_fanins(self, f):
        n = self.deref(f)
        return n.get_fanins()

    def get_positive_fanins(self, f):
        n = self.deref(f)
        return (self.get_positive(fi) for fi in n.get_fanins())

    def get_positive_seq_fanins(self, f):
        n = self.deref(f)
        return (self.get_positive(fi) for fi in n.get_seq_fanins())

    # PO fanins

    def get_po_type(self, po):
        assert 0 <= po < len(self._pos)
        return self._pos[po][1]

    def get_po_fanin(self, po):
        assert 0 <= po < len(self._pos)
        return self._pos[po][0]

    def set_po_fanin(self, po, f):
        assert 0 <= po < len(self._pos)
        self._pos[po] = (f, self._pos[po][1])

    def set_po_type(self, po, po_type):
        assert 0 <= po < len(self._pos)
        self._pos[po] = (self._pos[po][0], po_type)

    # Justice

    def get_justice_pos(self, j_id):
        assert 0 <= j_id < len(self._justice)
        return (po for po in self._justice[j_id])

    def set_justice_pos(self, j_id, po_ids):
        assert 0 <= j_id < len(self._justice)
        for po_id in po_ids:
            assert self.get_po_type(po_id) == AIG.JUSTICE
        self._justice[j_id] = po_ids

    # Negation

    @staticmethod
    def is_negated(f):
        return (f & 1) != 0 # (f & 1) == 0 or 1,  is the LSB of f.

    @staticmethod
    def get_positive(f):
        return (f & ~1)

    @staticmethod
    def negate(f):
        return f ^ 1

    @staticmethod
    def negate_if(f, c):
        if c:
            return f ^ 1
        else:
            return f

    @staticmethod
    def positive_if(f, c):
        if c:
            return f
        else:
            return f ^ 1

    @staticmethod
    def negate_if_negated(f, c):  # Negate f if c is negated
        return f ^ (c & 1)

    # Higher-level boolean operations

    def create_nand(self, left, right):
        return self.negate(self.create_and(left, right))

    def create_or(self, left, right):
        return self.negate(self.create_and(self.negate(left), self.negate(right)))

    def create_nor(self, left, right):
        return self.negate(self.create_or(left, right))

    def create_xor(self, left, right):
        return self.create_or(
            self.create_and(left, self.negate(right)),
            self.create_and(self.negate(left), right)
        )

    def create_iff(self, left, right):
        return self.negate(self.create_xor(left, right))

    def create_implies(self, left, right):
        return self.create_or(self.negate(left), right)

    def create_ite(self, f_if, f_then, f_else):
        return self.create_or(
            self.create_and(f_if, f_then),
            self.create_and(self.negate(f_if), f_else)
        )

    # Object numbers

    def n_pis(self):
        return len(self._pis)

    def n_latches(self):
        return len(self._latches)

    def n_ands(self):
        return self.n_nonterminals() - self.n_buffers()

    def n_nonterminals(self):
        return len(self._nodes) - 1 - self.n_latches() - self.n_pis()

    def n_pos(self):
        return len(self._pos)

    def n_pos_by_type(self, type):
        res = 0
        for _ in self.get_pos_by_type(type):
            res += 1
        return res

    def n_justice(self):
        return len(self._justice)

    def n_buffers(self):
        return len(self._buffers)

    # Object access as iterators (use list() to get a copy)
    #
    # Replace xrange by range.

    def construction_order(self):
        # return (i << 1 for i in xrange(1, len(self._nodes)))
        return (i << 1 for i in range(1, len(self._nodes)))

    def construction_order_deref(self):
        return ((f, self.deref(f)) for f in self.construction_order())

    def get_pis(self):
        return (i << 1 for i, n in enumerate(self._nodes) if n.is_pi())

    def get_latches(self):
        return (l for l in self._latches)

    def get_buffers(self):
        return (b for b in self._buffers if b >= 0)

    def get_and_gates(self):
        return (i << 1 for i, n in enumerate(self._nodes) if n.is_and())

    def get_pos(self):
        return ((po_id, po_fanin, po_type) for po_id, (po_fanin, po_type) in enumerate(self._pos))

    def get_pos_by_type(self, type):
        return ((po_id, po_fanin, po_type) for po_id, po_fanin, po_type in self.get_pos() if po_type == type)

    def get_po_fanins(self):
        return (po for _, po, _ in self.get_pos())

    def get_po_fanins_by_type(self, type):
        return (po for _, po, po_type in self.get_pos() if po_type == type)

    def get_justice_properties(self):
        return ((i, po_ids) for i, po_ids in enumerate(self._justice))

    def get_nonterminals(self):
        return (i << 1 for i, n in enumerate(self._nodes) if n.is_nonterminal())

    # Python special methods

    def __len__(self):
        return len(self._nodes)

        # return the sequential cone of 'roots', stop at 'stop'

    def get_cone(self, roots, stop=[], fanins=get_positive_fanins):

        visited = set()

        dfs_stack = list(roots)

        while dfs_stack:

            cur = self.get_positive(dfs_stack.pop())

            if cur in visited or cur in stop:
                continue

            visited.add(cur)

            for fi in fanins(self, cur):
                if fi not in visited:
                    dfs_stack.append(fi)

        return sorted(visited)

    # return the sequential cone of roots

    def get_seq_cone(self, roots, stop=[]):
        return self.get_cone(roots, stop, fanins=AIG.get_positive_seq_fanins)

    def topological_sort(self, roots, stop=()):
        """ topologically sort the combinatorial cone of 'roots', stop at 'stop' """

        def fanins(f):
            if f in stop:
                return []
            return [fi for fi in self.get_positive_fanins(f)]

        visited = AIG.fset()
        dfs_stack = []

        for root in roots:

            if visited.add(root):
                continue

            dfs_stack.append((root, fanins(root)))

            while dfs_stack:

                cur, ds = dfs_stack[-1]

                if not ds:

                    dfs_stack.pop()

                    if cur is not None:
                        yield cur

                    continue

                d = ds.pop()

                if visited.add(d):
                    continue

                dfs_stack.append((d, [fi for fi in fanins(d) if fi not in visited]))

    def clean(self, pos=None, justice_pos=None):
        """ return a new AIG, containing only the cone of the POs, removing buffers while attempting to preserve names """

        aig = AIG()
        M = AIG.fmap()

        def visit(f, af):
            if self.has_name(f):
                if AIG.is_negated(af):
                    aig.set_name(AIG.get_positive(af), "~%s" % self.get_name_by_id(f))
                else:
                    aig.set_name(af, self.get_name_by_id(f))
            M[f] = af

        if pos is None:
            pos = range(len(self._pos))

        pos = set(pos)

        if justice_pos is None:
            justice_pos = range(len(self._justice))

        for j in justice_pos:
            pos.update(self._justice[j])

        cone = self.get_seq_cone(self.get_po_fanin(po_id) for po_id in pos)

        for f in self.topological_sort(cone):

            n = self.deref(f)

            if n.is_pi():
                visit(f, aig.create_pi())

            elif n.is_and():
                visit(f, aig.create_and(M[n.get_left()], M[n.get_right()]))

            elif n.is_latch():
                l = aig.create_latch(init=n.get_latch_init())
                visit(f, l)

            elif n.is_buffer():
                assert False
                visit(f, M(n.get_buf_in()))

        for l in self.get_latches():
            if l in cone:
                aig.set_latch_next(M[l], M[self.get_latch_next(l)])

        po_map = {}

        for po_id in pos:
            po_f = self.get_po_fanin(po_id)
            po = aig.create_po(M[po_f], self.get_name_by_po(po_id) if self.po_has_name(po_id) else None,
                               po_type=self.get_po_type(po_id))
            po_map[po_id] = po

        for j in justice_pos:
            aig.create_justice([po_map[j_po] for j_po in self._justice[j]])

        return aig

    def compose(self, src, M, copy_pos=True):
        """ rebuild the AIG 'src' inside 'self', connecting the two AIGs using 'M' """

        for f in src.construction_order():

            if f in M:
                continue

            n = src.deref(f)

            if n.is_pi():
                M[f] = self.create_pi()

            elif n.is_and():
                M[f] = self.create_and(M[n.get_left()], M[n.get_right()])

            elif n.is_latch():
                M[f] = self.create_latch(init=n.get_init())

            elif n.is_buffer():
                M[f] = self.create_buffer()

        for b in src.get_buffers():
            self.set_buf_in(M[b], M[src.get_buf_in(b)])

        for l in src.get_latches():
            self.set_latch_next(M[l], M[src.get_next(l)])

        if copy_pos:
            for po_id, po_fanin, po_type in src.get_pos():
                self.create_po(M[po_fanin], po_type=po_type)

    def cutpoint(self, f):

        assert self.is_buffer(f)
        assert self.has_name(f)

        self.convert_buf_to_pi(f)

    def build_fanouts(self):

        for f in self.construction_order():

            for g in self.get_positive_fanins(f):
                self._fanouts.setdefault(g, set()).add(f)

    def get_fanouts(self, fs):

        res = set()

        for f in fs:
            for fo in self._fanouts[f]:
                res.add(fo)

        return res

    def conjunction(self, fs):

        res = self.get_const1()

        for f in fs:
            res = self.create_and(res, f)

        return res

    def balanced_conjunction(self, fs):

        N = len(fs)

        if N < 2:
            return self.conjunction(fs)

        return self.create_and(self.balanced_conjunction(fs[:N / 2]), self.balanced_conjunction(fs[N / 2:]))

    def disjunction(self, fs):

        res = self.get_const0()

        for f in fs:
            res = self.create_or(res, f)

        return res

    def balanced_disjunction(self, fs):

        N = len(fs)

        if N < 2:
            return self.disjunction(fs)

        return self.create_or(self.balanced_disjunction(fs[:N / 2]), self.balanced_disjunction(fs[N / 2:]))

    def large_xor(self, fs):

        res = self.get_const0()

        for f in fs:
            res = self.create_xor(res, f)

        return res

    def mux(self, select, args):

        res = []

        for col in zip(*args):
            f = self.disjunction(self.create_and(s, c) for s, c in zip(select, col))
            res.append(f)

        return res

    def create_constraint(aig, f, name=None):
        return aig.create_po(aig, f, name=name, po_type=AIG.CONSTRAINT)

    def create_property(aig, f, name=None):
        return aig.create_po(aig, AIG.negate(f), name=name, po_type=AIG.BAD_STATES)

    def create_bad_states(aig, f, name=None):
        return aig.create_po(aig, f, name=name, po_type=AIG.BAD_STATES)

########################################################################################################################
# class _MIG_Node
#
# @Time    : 2021/5/26
# @Author  : c
#
# Nodes in MIG
#
########################################################################################################################
class _MIG_Node:

    # Node types
    CONST0 = 0
    PI = 1
    LATCH = 2
    MAJ = 3
    BUFFER = 4

    # PO type (for polymorphic edges synthesis)
    PO = -1

    # Latch init
    INIT_ZERO = 0
    INIT_ONE = 1
    INIT_NON = 2

    def __init__(self, node_type, child0 = 0, child1 = 0, child2 = 0):
        self._type = node_type
        self._child0 = child0
        self._child1 = child1
        self._child2 = child2

    # creation
    @staticmethod
    def make_const0():
        '''
        Return a _MIG_Node obj whose _type is CONST0

        :return: _MIG_Node
        '''
        return _MIG_Node(_MIG_Node.CONST0)

    @staticmethod
    def make_pi(pi_id):
        '''
        Return a _MIG_Node obj whose _type is PI.
        The _child0 represents the id of PI.
        The _child1 and _child2 are set to 0.

        :param pi_id: INT - PI ID
        :return: _MIG_Node
        '''
        return _MIG_Node(_MIG_Node.PI, pi_id, 0, 0)

    @staticmethod
    def make_latch(latch_id, init, next = None):
        '''
        Return a _MIG_Node obj whose _type is LATCH.
        The _child0, _child1, and child2 represent the id, init state, and next state of this latch, respectively.

        :param latch_id: INT - Latch ID
        :param init: INT - Init state
        :param next: INT - next state
        :return: _MIG_Node
        '''
        return _MIG_Node(_MIG_Node.LATCH, latch_id, init, next)

    @staticmethod
    def make_maj(child0, child1, child2):
        '''
        Return a _MIG_Node obj whose _type is MAJ.

        :param child0: The first child of this MAJ node.
        :param child1: The second child of this MAJ node.
        :param child2: The third child of this MAJ node.
        :return: _MIG_Node
        '''
        return _MIG_Node(_MIG_Node.MAJ, child0, child1, child2)

    @staticmethod
    def make_buffer(buf_id, buf_in):
        '''
        Return a _MIG_Node obj whose _type is BUFFER.
        The _child0 and _child1 represent the id and input of this buffer, respectively.
        The _child2 is set to 0.

        :param buf_id: INT - Buffer ID
        :param buf_in: INT - Buffer input
        :return: _MIG_Node
        '''
        return _MIG_Node(_MIG_Node.BUFFER, buf_id, buf_in, 0)

    # query type
    def is_const0(self):
        '''
        Return Ture if and only if self._type is CONST0.

        :return: Boolean
        '''
        return self._type == _MIG_Node.CONST0

    def is_pi(self):
        '''
        Return Ture if and only if self._type is PI.

        :return: Boolean
        '''
        return self._type == _MIG_Node.PI

    def is_maj(self):
        '''
        Return Ture if and only if self._type is MAJ.

        :return: Boolean
        '''
        return self._type == _MIG_Node.MAJ

    def is_latch(self):
        '''
        Return Ture if and only if self._type is LATCH.

        :return: Boolean
        '''
        return self._type == _MIG_Node.LATCH

    def is_buffer(self):
        '''
        Return Ture if and only if self._type is BUFFER.

        :return: Boolean
        '''
        return self._type == _MIG_Node.BUFFER

    def is_nonterminal(self):
        '''
        Return Ture if and only if this node is a non-terminal node (MAJ or BUFFER).

        :return:
        '''
        return self._type in (_MIG_Node.MAJ, _MIG_Node.BUFFER)

    def get_fanins(self):
        '''
        Return a list containing the fan-ins of node.
        Note: Only MAJ and BUFFER node has fan-in!

        :return: LIST of int
        '''
        if self._type == _MIG_Node.MAJ:
            return [self._child0, self._child1, self._child2]
        elif self._type == _MIG_Node.BUFFER:
            return [self._child1]
        else:
            return []

    def get_seq_fanins(self):
        '''
        Return a list containing the fan-ins of node.
        Note: Only MAJ, BUFFER, and LATCH has fan-in!

        :return: LIST of int
        '''
        if self._type == _MIG_Node.MAJ:
            return [self._child0, self._child1, self._child2]
        elif self._type == _MIG_Node.BUFFER:
            return [self._child1]
        elif self._type == _MIG_Node.LATCH:
            return [self._child2]
        else:
            return []

    # MAJ gates
    def get_maj_child0(self):
        '''
        Return the _child0 of a MAJ-type _MIG_Node obj

        :return: INT
        '''
        assert self.is_maj()
        return self._child0

    def get_maj_child1(self):
        '''
        Return the _child1 of a MAJ-type _MIG_Node obj

        :return: INT
        '''
        assert self.is_maj()
        return self._child1

    def get_maj_child2(self):
        '''
        Return the _child2 of a MAJ-type _MIG_Node obj.

        :return: INT
        '''
        assert self.is_maj()
        return self._child2

    # Buffer
    def get_buf_id(self):
        '''
        Return the _child0 (id) of a BUFFER-type _MIG_Node obj.

        :return: INT
        '''
        assert self.is_buffer()
        return self._child0

    def get_buf_in(self):
        '''
        Return the _child1 (input) of a BUFFER-type _MIG_Node obj.

        :return: INT
        '''
        assert self.is_buffer()
        return self._child1

    def set_buf_in(self, f):
        '''
        Set the _child1 (input) of a BUFFER-type _MIG_Node obj to f.

        :param f: INT - New input.
        :return:
        '''
        assert self.is_buffer()
        self._child1 = f

    def convert_buf_to_pi(self, pi_id):
        '''
        Convert a BUFFER-type _MIG_Node obj to a PI-type _MIG_Node obj with pi_id (id).

        :param pi_id: INT - The id of PI
        :return: _MIG_Node
        '''
        assert self.is_buffer()
        self._type = _MIG_Node.PI
        self._child0 = pi_id
        self._child1 = 0

    # PIs
    def get_pi_id(self):
        '''
        Return the _child0 (id) of a PI-type _MIG_Node obj

        :return: INT
        '''
        assert self.is_pi()
        return self._child0

    # Latch
    def get_latch_id(self):
        '''
        Return the _child0 (id) of a LATCH-type _MIG_Node obj.

        :return: INT
        '''
        assert self.is_latch()
        return self._child0

    def get_latch_init(self):
        '''
        Return the _child1 (init state) of a LATCH-type _MIG_Node obj.

        :return: INT
        '''
        assert self.is_latch()
        return self._child1

    def get_latch_next(self):
        '''
        Return the _child2 (next state) of a LATCH-type _MIG_Node obj.

        :return: INT
        '''
        assert self.is_latch()
        return self._child2

    def set_latch_init(self, init):
        '''
        Set the _child1 (init state) of a LATCH-type _MIG_Node obj to init.

        :param init: New init
        :return:
        '''
        assert self.is_latch()
        self._child1 = init

    def set_latch_next(self, next):
        '''
        Set the _child1 (next state) of a LATCH-type _MIG_Node obj to next.

        :param next: New next
        :return:
        '''
        assert self.is_latch()
        self._child2 = next

    # __repr__
    def __repr__(self):
        if self._type == _MIG_Node.PI:
            type = 'PI'
        elif self._type == _MIG_Node.CONST0:
            type = 'CONST0'
        elif self._type == _MIG_Node.MAJ:
            type = 'MAJ'
        elif self._type == _MIG_Node.BUFFER:
            type = 'BUFFER'
        elif self._type == _MIG_Node.LATCH:
            type = 'LATCH'
        else:
            type = 'ERROR'

        return "pmig.graphs._MIG_Node _type=" + type + ", _child0=" + str(self._child0) + ", _child1=" + str(self._child1) + ", _child2=" + str(self._child2)

########################################################################################################################
# class PMIG
#
# @Time    : 2021/5/27
# @Author  : c
#
# Polymorphic MIG.
#
# Node:
#     Each node is a instance of _MIG_Node. It may be CONST0-type, PI-type, MAJ-type, LATCH-type, or BUFFER-type.
#     Nodes are stored in a list (_nodes), and each node is identified by the order in _nodes.
#
# Literal:
#     Each literal consists of TWO PARTS:
#     (1) The lowest TWO bits are the attributes attached to the output edge of node.
#     (2) The other bits are the position in the list.
#
# Poly-edge:
#     The meaning of the lowest TWO bits (L[1], L[0]) of a literal are as follows:
#     (1) L[1]: L[1] = 1 if the literal represents an output edge with polymorphic attribute. L[1] = 0 if not.
#     (2) L[0]: L[0] = 1 if the literal has negative attribute (in NORMAL mode if L[1] = 1). L[0] = 0 if not.
#
########################################################################################################################
class PMIG:

    # Latch Init
    INIT_ZERO = _MIG_Node.INIT_ZERO
    INIT_ONE = _MIG_Node.INIT_ONE
    INIT_NON = _MIG_Node.INIT_NON

    def __init__(self, name = None):
        self._name = name # Name
        self._strash = {} # Structural hashing table
        self._pis = [] # Literals of PIs (positive and non-polyedged)
        self._pos = [] # (Literal, type)
        self._latches = [] # Literals of latches (positive and non-polyedged)
        self._buffers = [] # Literals of buffers (positive and non-polyedged)
        self._nodes = [] # _MIG_Node objs
        self._name_to_id = {} # Name-to-ID mapping. (The ID here is actually positive non-polyedged literal!)
        self._id_to_name = {} # ID-to-Name mapping. (The ID here is actually positive non-polyedged literal!)
        self._po_to_name = {} # PO-to-Name mapping.
        self._name_to_po = {} # Name-to-PO mapping.
        self._fanouts = {}
        self._polymorphic_edges = {} # Contains all the nodes with polymorphic-edge as child.
                             # The key is the id of node and must be a literal.
                             # It must be positive and non-polymorphic literal if and only if the type is _MIG_Node.PO.
                             # The value is an list: [type, value]. Type can be _MIG_Node.MAJ/LATCH/BUFFER...
                             # Value is an int from 0 to 7 and calculated as follows:
                             # value = 1 * (child0 has p-edge attribute)
                             #         + 2 * (child1 has p-edge attribute)
                             #         + 4 * (child2 has p-edge attribute)
        self._polymorphic_nodes = {} # Contains all the nodes with control signal as child.
                             # The key is the id of node and must be a positive and non-polymorphic literal.
                             # The value is an list: [type, value]. Type can be _MIG_Node.MAJ/LATCH/BUFFER...
                             # The value is an int from 0 to 7 and calculated as follows:
                             # value = 1 * (child0 is control signal PI)
                             #         + 2 * (child1 control signal PI)
                             #         + 4 * (child2 control signal PI)

        self._nodes.append( _MIG_Node.make_const0() ) # The ID of CONST0 must be 0!

    # const fan-ins
    @staticmethod
    def get_literal_const0():
        '''
        Return the literal of const 0.

        :return: INT - Literal
        '''
        return 0

    @staticmethod
    def get_literal_const1():
        '''
        Return the literal of const 1.

        :return: INT - Literal
        '''
        return 1

    @staticmethod
    def get_literal_const_0_1():
        '''
        Return the literal of polymorphic const: 0/1.

        :return: INT - Literal
        '''
        return 2

    @staticmethod
    def get_literal_const_1_0():
        '''
        Return the literal of polymorphic const: 1/0

        :return: INT - Literal
        '''
        return 3

    # Object numbers
    def n_pis(self):
        '''
        Return len(self._pis)

        :return: INT
        '''
        return len(self._pis)

    def n_latches(self):
        '''
        Return len(self._latches)

        :return: INT
        '''
        return len(self._latches)

    def n_buffers(self):
        '''
        Return len(self._buffers)
        :return:
        '''
        return len(self._buffers)

    def n_nonterminals(self):
        '''
        Return the number of non-terminal nodes.

        len(self._nodes) - 1 - self.n_pis() - self.n_latches()

        :return: INT
        '''
        return len(self._nodes) - 1 - self.n_pis() - self.n_latches()

    def n_majs(self):
        '''
        Return the number of NAJ nodes.

        self.n_nonterminals() - self.n_buffers()

        :return: INT
        '''

        return self.n_nonterminals() - self.n_buffers()

    def n_pos(self):
        '''
        Return len(self._pos)

        :return: INT
        '''
        return len(self._pos)

    def n_pos_by_type(self, i_type):
        '''
        Return the number of 'i_type' POs.

        :param i_type: INT - type
        :return: INT
        '''
        res = 0
        for i_po in self.get_iter_pos_by_type(i_type):
            res = res + 1
        return res

    def n_polymorphic_edges(self):
        '''
        Return len(self._polymorphic_edges)

        :return: INT
        '''
        return len(self._polymorphic_edges)

    def n_polymorphic_nodes(self):
        '''
        Return len(self._polymorphic_edges)

        :return: INT
        '''
        return len(self._polymorphic_nodes)

    # Object access as iterators (use list() to get a copy)
    def get_iter_pis(self):
        '''
        Return iterator of PIs (Positive and non-polymorphic literal)

        :return: ITERATOR: INT - Literal
        '''
        return ( i << 2 for i, n in enumerate(self._nodes) if n.is_pi() )

    def get_iter_pos(self):
        '''
        Return iterator of POs: (po_id: Order in self._pos, po_fanin: Fan-in literal, po_type: PO type).

        :return: ITERATOR: TUPLE - (po_id, po_fanin, po_type)
        '''
        return ((po_id, po_fanin, po_type) for po_id, (po_fanin, po_type) in enumerate(self._pos))

    def get_iter_pos_by_type(self, i_type):
        '''
        Return iterator of POs: (po_id: Order in self._pos, po_fanin: Fan-in literal, po_type == i_type: PO type).

        :return: ITERATOR: TUPLE - (po_id, po_fanin, po_type == i_type)
        '''
        return ((po_id, po_fanin, po_type) for po_id, po_fanin, po_type in self.get_iter_pos() if po_type == i_type)

    def get_iter_po_fanins(self):
        '''
        Return iterator of fan-ins (positive and non-polymorphic literals) of PO

        :return: ITERATOR: INT - Literal
        '''
        return ( po_fanin for po_id, po_fanin, po_type in self.get_iter_pos() )

    def get_iter_po_fanins_by_type(self, i_type):
        '''
        Return iterator of fan-ins (positive and non-polmorphic literals) of 'i-type' PO.

        :param i_type: ITERATOR: INT - Literal
        :return:
        '''
        return ( po_fanin for po_id, po_fanin, po_type in self.get_iter_pos_by_type(i_type) )

    def get_iter_latches(self):
        '''
        Return iterator of LATCHs (Positive and non-polymorphic literal)

        :return: ITERATOR: INT - Literal
        '''
        return ( l for l in self._latches )

    def get_iter_buffers(self):
        '''
        Return iterator of BUFFERs (Positive and non-polymorphic literal)

        :return: ITERATOR: INT - Literal
        '''
        return ( b for b in self._buffers if b >= 0 )

    def get_iter_majs(self):
        '''
        Return iterator of MAJs (Positive and non-polymorphic literal)

        :return: ITERATOR: INT - Literal
        '''
        return ( i << 2 for i, n in enumerate(self._nodes) if n.is_maj() )

    def get_iter_nonterminals(self):
        '''
        Return iterator of non-terminal nodes (Positive and non-polymorphic literal).

        :return: ITERATOR: INT - Literal
        '''
        return ( i << 2 for i, n in enumerate(self._nodes) if n.is_nonterminal() )

    # _polymorphic_edges
    def polymorphic_edgesdict_add(self, p_id, p_type, p_value):
        '''
        Add {id: [type, value]} to dict: _polymorphic_edges

        id is a positive and non-polymorphic literal (node) if type is not PO, or a polymorphic literal (output of a node) if type is PO.

        value (MAJ) = 1 * (child0 has p-edge attribute) +
                2 * (child1 has p-edge attribute) +
                4 * (child2 has p-edge attribute)

        value (PO) = po_type

        value (Others) = 1

        :param p_id: INT - Literal (positive and non-polymorphic for types except PO)
        :param p_type: INT - _MIG_Node.MAJ/LATCH/BUFFER/PO. Cannot be PI.
        :param p_value: INT
        :return:
        '''
        assert p_id not in self._polymorphic_edges
        assert p_type in (_MIG_Node.MAJ, _MIG_Node.LATCH, _MIG_Node.BUFFER, _MIG_Node.PO)
        # id must be positive and non-polymorphic if type is _MIG_Node.MAJ/BUFFER/LATCH.
        # And if type is _MIG_Node.PO, then id must be polymorphic!
        assert ( not (self.is_polymorphic_literal(p_id) or self.is_negated_literal(p_id)) ) or (p_type == _MIG_Node.PO)
        assert (self.is_polymorphic_literal(p_id)) or (p_type in (_MIG_Node.MAJ, _MIG_Node.LATCH, _MIG_Node.BUFFER))
        self._polymorphic_edges[p_id] = [p_type, p_value]

    def polymorphic_edgesdict_modify(self, p_id, p_type, p_value):
        '''
        Modify {id: [type, value]} in dict: _polymorphic_edges

        id is a positive and non-polymorphic literal (node) if type is not PO, or a polymorphic literal (output of a node) if type is PO.

        value (MAJ) = 1 * (child0 has p-edge attribute) +
                2 * (child1 has p-edge attribute) +
                4 * (child2 has p-edge attribute)

        value (Others) = 1

        :param p_id: INT - Literal (positive and non-polymorphic for types except PO)
        :param p_type: INT - _MIG_Node.MAJ/LATCH/BUFFER/PO. Cannot be PI.
        :param p_value: INT
        :return:
        '''
        assert p_id in self._polymorphic_edges
        assert p_type in (_MIG_Node.MAJ, _MIG_Node.LATCH, _MIG_Node.BUFFER, _MIG_Node.PO)
        # id must be positive and non-polymorphic if type is _MIG_Node.MAJ/BUFFER/LATCH.
        # And if type is _MIG_Node.PO, then id must be polymorphic!
        assert (not (self.is_polymorphic_literal(p_id) or self.is_negated_literal(p_id))) or (p_type == _MIG_Node.PO)
        assert (self.is_polymorphic_literal(p_id)) or (p_type in (_MIG_Node.MAJ, _MIG_Node.LATCH, _MIG_Node.BUFFER))
        self._polymorphic_edges[p_id] = [p_type, p_value]

    def polymorphic_edgesdict_delete(self, p_id):
        '''
        Delete {id: [type, value]} in dict: _polymorphic_edges

        :param p_id: INT - Literal (positive and non-polymorphic for types except PO)
        :return:
        '''
        assert p_id in self._polymorphic_edges
        poly_info = self._polymorphic_edges.pop(p_id)
        return poly_info

    # __polymorphic_nodes
    def polymorphic_nodesdict_add(self, p_id, p_type, p_value):
        '''
        Add {id: [type, value]} to dict: _polymorphic_nodes

        id is a positive and non-polymorphic literal.

        value (MAJ) = 1 * (child0 has p-edge attribute) +
                2 * (child1 has p-edge attribute) +
                4 * (child2 has p-edge attribute)

        value (Others) = 1

        :param p_id: INT - Literal (positive and non-polymorphic)
        :param p_type: INT - _MIG_Node.MAJ/LATCH/BUFFER. Cannot be PO/PI.
        :param p_value: INT
        :return:
        '''
        assert p_id not in self._polymorphic_nodes
        assert not self.is_polymorphic_literal(p_id)
        assert p_type in (_MIG_Node.MAJ, _MIG_Node.LATCH, _MIG_Node.BUFFER)
        self._polymorphic_nodes[p_id] = [p_type, p_value]

    def polymorphic_nodesdict_modify(self, p_id, p_type, p_value):
        '''
        Modify {id: [type, value]} in dict: _polymorphic_nodes

        id is a positive and non-polymorphic literal.

        value (MAJ) = 1 * (child0 has p-edge attribute) +
                2 * (child1 has p-edge attribute) +
                4 * (child2 has p-edge attribute)

        value (Others) = 1

        :param p_id: INT - Literal (positive and non-polymorphic)
        :param p_type: INT - _MIG_Node.MAJ/LATCH/BUFFER. Cannot be PO/PI.
        :param p_value: INT
        :return:
        '''
        assert p_id in self._polymorphic_nodes
        assert not self.is_polymorphic_literal(p_id)
        assert p_type in (_MIG_Node.MAJ, _MIG_Node.LATCH, _MIG_Node.BUFFER)
        self._polymorphic_nodes[p_id] = [p_type, p_value]

    def polymorphic_nodesdict_delete(self, p_id):
        '''
        Delete {id: [type, value]} in dict: _polymorphic_nodes

        :param p_id: INT - Literal (positive and non-polymorphic)
        :return:
        '''
        assert p_id in self._polymorphic_nodes
        assert not self.is_polymorphic_literal(p_id)
        poly_info = self._polymorphic_nodes.pop(p_id)
        return poly_info


    def deref(self, f):
        '''
        Get the node of a literal.

        :param f: INT - Literal
        :return: _MIG_Node - Node
        '''
        return self._nodes[ f >> 2 ]

    def name(self):
        '''
        Get the name of this PMIG.

        :return: ANY
        '''
        return self._name

    # Attribute of literal
    @staticmethod
    def is_negated_literal(f):
        '''
        Return TRUE if the literal f has negated attribute.

        :param f: INT - Literal
        :return: Bool
        '''
        return (f & 1) != 0

    @staticmethod
    def is_polymorphic_literal(f):
        '''
        Return True if the literal f has polymorphic attribute.

        :param f: INT - Literal
        :return: Bool
        '''
        return (f & 2) != 0

    @staticmethod
    def get_positive_literal(f):
        '''
        Return the literal with positive attribute.

        :param f: INT - Literal
        :return: INT - Literal
        '''
        return (f & ~1)

    @staticmethod
    def get_normal_literal(f):
        '''
        Return the literal with non-polyedge attribute.

        :param f: INT - Literal
        :return: INT - Literal
        '''
        return (f & ~2)

    @staticmethod
    def get_positive_normal_literal(f):
        '''
        Return the literal with positive and non-polymorphic attribute.

        :param f: INT - Literal
        :return: INT - Literal
        '''
        return (f & ~3)

    @staticmethod
    def negate_literal_if(f, c):
        '''
        Invert the LSB of f if c is True.

        :param f: INT - Literal
        :param c: Bool
        :return: INT - Literal
        '''
        if c:
            return f ^ 1 # xor
        else:
            return f

    @staticmethod
    def negate_literal_if_negated(f, c):
        '''
        Invert the LSB of f if c is negated.

        :param f: INT - Literal
        :param c: INT - Literal
        :return: INT - Literal
        '''
        return f ^ (c & 1)

    @staticmethod
    def polymorphic_literal_if(f, c):
        '''
        Invert the polymorphic flag of f if c is True.

        :param f: INT - Literal
        :param c: Bool
        :return: INT - Literal
        '''
        if c:
            return f ^ 2  # xor
        else:
            return f

    @staticmethod
    def polymorphic_literal_if_polyedged(f, c):
        '''
        Invert the polymorphic flag of f if c is polymorphic.

        :param f: INT - Literal
        :param c: INT - Literal
        :return: INT - Literal
        '''
        return f ^ (c & 2)

    # Names
    def set_name(self, f, name):
        '''
        Set name of f. f should be a positive non-polyedged literal!

        :param f: INT - A positive non-polyedged literal
        :param name: STRING
        :return:
        '''
        assert not self.is_negated_literal(f)
        assert not self.is_polymorphic_literal(f)
        assert name not in self._name_to_id
        assert f not in self._id_to_name

        self._name_to_id[name] = f
        self._id_to_name[f] = name

    def get_id_by_name(self, name):
        '''
        Get ID (The ID here is actually positive non-polymorphic literal!) by name.

        :param name: STRING - Name
        :return: INT - A positive non-polyedged literal
        '''
        return self._name_to_id[name]

    def has_name(self, f):
        '''
        Return True if f has a name in _id_to_name.

        :param f: INT - A positive non-polymorphic literal
        :return: Bool
        '''
        return f in self._id_to_name

    def name_exists(self, n):
        '''
        Return True if n has a name in _name_to_id.

        :param n: STRING - Name
        :return: Bool
        '''
        return n in self._name_to_id

    def get_name_by_id(self, f):
        '''
        Get name by ID (The ID here is actually positive non-polymorphic literal!).

        :param f: INT - A positive non-polymorphic literal
        :return: STRING - Name
        '''
        return self._id_to_name[f]

    def remove_name(self, f):
        '''
        Remove f (positive non-polymorphic literal) from _id_to_name and _name_to_id.

        :param f: INT - A positive non-polymorphic literal
        :return:
        '''
        assert self.has_name(f)
        name = self.get_name_by_id(f)

        del self._id_to_name[f]
        del self._name_to_id[name]

    def iter_names(self):
        '''
        Return self._id_to_name.items()

        :return:
        '''
        return self._id_to_name.items()

    def fill_pi_names(self, replace=False, template="I_{}"):
        '''
        Fill PI names

        :param replace:
        :param template: Template
        :return:
        '''

        if replace:
            for pi in self.get_iter_pis():
                if self.has_name(pi):
                    self.remove_name(pi)

        uid = 0

        for pi in self.get_iter_pis():
            if not self.has_name(pi):
                while True:
                    name = template.format(uid)
                    uid += 1
                    if not self.name_exists(name):
                        break
                self.set_name(pi, name)

    # PO names
    def set_po_name(self, po, name):
        assert 0 <= po < len(self._pos)
        assert name not in self._name_to_po
        assert po not in self._po_to_name

        self._name_to_po[name] = po
        self._po_to_name[po] = name

    def get_po_by_name(self, name):
        return self._name_to_po[name]

    def po_has_name(self, po):
        return po in self._po_to_name

    def name_has_po(self, po):
        return po in self._name_to_po

    def remove_po_name(self, po):
        assert self.po_has_name(po)
        name = self.get_name_by_po(po)
        del self._name_to_po[name]
        del self._po_to_name[po]

    def get_name_by_po(self, po):
        return self._po_to_name[po]

    def iter_po_names(self):
        return ((po_id, self.get_po_fanin(po_id), po_name) for po_id, po_name in self._po_to_name.items())

    def fill_po_names(self, replace=False, template="O_{}"):

        if replace:
            self._name_to_po.clear()
            self._po_to_name.clear()

        po_names = set(name for _, _, name in self.iter_po_names())

        uid = 0
        for po_id, _, _ in self.get_iter_pos():
            if not self.po_has_name(po_id):
                while True:
                    name = template.format(uid)
                    uid += 1
                    if name not in po_names:
                        break
                self.set_po_name(po_id, name)

    # Create basic objects
    def create_pi(self, name = None):
        '''
        Create a PI-type node.

        :param name: STRING - Name
        :return: INT - Literal of the node
        '''
        pi_id = len(self._pis)
        n = _MIG_Node.make_pi(pi_id)
        fn = len(self._nodes) << 2

        self._nodes.append(n)
        self._pis.append(fn)

        if name is not None:
            self.set_name(fn, name)

        return fn

    def create_latch(self, name = None, init = INIT_ZERO, next = None):
        '''
        Create a LATCH-type node.

        :param name: STRING - Name
        :param init: INT - Init state
        :param next: INT - Next state
        :return: INT - Literal of the node
        '''
        l_id = len(self._latches)
        n = _MIG_Node.make_latch(l_id, init, next)
        fn = len(self._nodes) << 2

        self._nodes.append(n)
        self._latches.append(fn)

        if name is not None:
            self.set_name(fn, name)

        # Polymorphic
        if self.is_polymorphic_literal(next):
            self.polymorphic_nodesdict_add(fn, _MIG_Node.LATCH, 1)
            self.polymorphic_edgesdict_add(fn, _MIG_Node.LATCH, 1)

        return fn

    def create_maj(self, child0, child1, child2):
        '''
        Create a MAJ-type node.
        It should be noted that:
        before calling this method, additional checks are required to avoid redundant node being created.

        :param child0: INT - Child 0
        :param child1: INT - Child 1
        :param child2: INT - Child 2
        :return: INT - Literal of the node
        '''
        # Literal constraint: child0 < child1 < child2
        if child0 > child1:
            child0, child1 = child1, child0
        if child1 > child2:
            child1, child2 = child2, child1
        if child0 > child1:
            child0, child1 = child1, child0

        # Redundant node
        if child0 == child1:
            return child0
        if child1 == child2:
            return child1
        if child2 == child0:
            return child2
        if child0 == PMIG.negate_literal_if(child1, True):
            return child2
        if child1 == PMIG.negate_literal_if(child2, True):
            return child0
        if child2 == PMIG.negate_literal_if(child0, True):
            return child1

        # Structural hashing
        key = (_MIG_Node.MAJ, child0, child1, child2)
        if key in self._strash:
            return self._strash[key]

        fn = len(self._nodes) << 2
        n = _MIG_Node.make_maj(child0, child1, child2)
        self._nodes.append(n)
        self._strash[key] = fn

        # Polymorphic
        if self.is_polymorphic_literal(child0) or self.is_polymorphic_literal(child1) or self.is_polymorphic_literal(child2):
            pchild_value = (1 * self.is_polymorphic_literal(child0)) + (2 * self.is_polymorphic_literal(child1)) + (4 * self.is_polymorphic_literal(child2))
            self.polymorphic_nodesdict_add(fn, _MIG_Node.MAJ, pchild_value)
            self.polymorphic_edgesdict_add(fn, _MIG_Node.MAJ, pchild_value)

        return fn

    def create_buffer(self, buf_in = 0, name = None):
        '''
        Create a BUFFER-type node.

        :param buf_in: INT - Input of buffer
        :param name: STRING - Name
        :return: INT - Literal of the buffer
        '''
        buf_id = len(self._buffers)
        fn = len(self._nodes) << 2
        n = _MIG_Node.make_buffer(buf_id, buf_in)

        self._nodes.append(n)
        self._buffers.append(fn)

        if name is not None:
            self.set_name(fn, name)

        # Polymorphic
        if self.is_polymorphic_literal(buf_in):
            self.polymorphic_nodesdict_add(fn, _MIG_Node.BUFFER, 1)
            self.polymorphic_edgesdict_add(fn, _MIG_Node.BUFFER, 1)

        return fn

    def convert_buf_to_pi(self, buf_id):
        '''
        Convert a BUFFER-type node to PI-type node.

        :param buf_id: Literal of buffer
        :return:
        '''
        assert self.is_buffer(buf_id)
        assert self.get_buffer_in(buf_id) >= 0

        n = self.deref(buf_id)
        self._buffers[n.get_buf_id()] = -1
        n.convert_buf_to_pi(len(self._pis))
        self._pis.append(buf_id)

        # Polymorphic
        if self.is_polymorphic_literal(buf_id):
            self.polymorphic_nodesdict_delete(buf_id)
            self.polymorphic_edgesdict_delete(buf_id)

    def create_po(self, f = 0, name = None, po_type = 0):
        '''
        Create PO.

        :param f:
        :param name:
        :param po_type:
        :return:
        '''
        po_id = len(self._pos)
        self._pos.append( (f, po_type) )

        if name is not None:
            self.set_po_name(po_id, name)

        # Polymorphic
        if self.is_polymorphic_literal(f):
            self.polymorphic_edgesdict_add(f, _MIG_Node.PO, po_type)

        return po_id

    # The PO types are not defined in current version!
    #
    # def create_justice:
    #
    # def remove_justice:


    # Query IDs
    @staticmethod
    def get_id(f):
        '''

        :param f: INT - Literal
        :return: INT - Literal >> 2
        '''
        return f >> 2

    def is_const0(self, f):
        '''
        Return True if 'f' is a literal of CONST0-type node.

        :param f: INT - Literal
        :return: Bool
        '''
        # assert isinstance(self, PMIG)
        n = self.deref(f)
        return n.is_const0

    def is_pi(self, f):
        '''
        Return True if 'f' is a literal of PI-type node.

        :param f: INT - Literal
        :return: Bool
        '''
        # assert isinstance(self, PMIG)
        n = self.deref(f)
        return n.is_pi

    def is_latch(self, f):
        '''
        Return True if 'f' is a literal of LATCH-type node.

        :param f: INT - Literal
        :return: Bool
        '''
        # assert isinstance(current_pmig, PMIG)
        n = self.deref(f)
        return n.is_latch

    def is_buffer(self, f):
        '''
        Return True if 'f' is a literal of BUFFER-type node.

        :param f: INT - Literal
        :return: Bool
        '''
        # assert isinstance(current_pmig, PMIG)
        n = self.deref(f)
        return n.is_buffer

    def is_maj(self, f):
        # assert isinstance(current_pmig, PMIG)
        '''
        Return True if 'f' is a literal of MAJ-type node.

        :param f: INT - Literal
        :return: Bool
        '''
        n = self.deref(f)
        return n.is_maj

    # PIs
    def get_pi_by_id(self, pi_id):
        '''
        Return 'self._pis[pi_id]'.

        :param pi_id: INT - ID (Literal >> 2)
        :return: INT - Literal
        '''
        return self._pis[pi_id]

    # Latches
    def get_latch_init(self, l):
        '''
        Return the init state of the latch with literal 'l'.

        :param l: INT - Literal of a latch
        :return: INT - The init state of the latch
        '''
        # assert not self.is_negated_literal(l)
        # assert not self.is_polymorphic_literal(l)
        assert self.is_latch(l)
        n = self.deref(l)
        return n.get_latch_init()

    def get_latch_next(self, l):
        '''
        Return the next state of the latch with literal 'l'.

        :param l: INT - Literal of a latch
        :return: INT - The next state of the latch
        '''
        # assert not self.is_negated_literal(l)
        # assert not self.is_polymorphic_literal(l)
        assert self.is_latch(l)
        n = self.deref(l)
        return n.get_latch_next()

    def set_latch_init(self, l, init):
        '''
        Set the init state of the latch with literal 'l'.

        :param l: INT - Literal of a latch
        :param init: INT - Init state
        :return:
        '''
        # assert not self.is_negated_literal(l)
        # assert not self.is_polymorphic_literal(l)
        assert self.is_latch(l)
        n = self.deref(l)
        n.set_latch_init(init)

    def set_latch_next(self, l, next):
        '''
        Set the next state of the latch with literal 'l'.

        :param l: INT - Literal of a latch.
        :param next: INT - Next state
        :return:
        '''
        # assert not self.is_negated_literal(l)
        # assert not self.is_polymorphic_literal(l)
        assert self.is_latch(l)
        n = self.deref(l)
        n.set_latch_next(next)


    # MAJ
    def get_maj_fanins(self, f):
        '''
        Return a tuple with the 3 child of the MAJ node with literal 'f'.

        :param f: INT - Literal of a MAJ node.
        :return: TUPLE (INT, INT, INT) - (child0, child1, child2)
        '''
        assert self.is_maj(f)
        # assert not self.is_negated_literal(f)
        # assert not self.is_polymorphic_literal(f)
        n = self.deref(f)
        return (n.get_maj_child0(), n.get_maj_child1(), n.get_maj_child2())

    def get_maj_child0(self, f):
        '''
        Return 'child0' of the MAJ node with literal 'f'.

        :param f: INT - Literal of a MAJ node.
        :return: INT - Child0
        '''
        assert self.is_maj(f)
        # assert not self.is_negated_literal(f)
        # assert not self.is_polymorphic_literal(f)
        n = self.deref(f)
        return n.get_maj_child0()

    def get_maj_child1(self, f):
        '''
        Return 'child1' of the MAJ node with literal 'f'.

        :param f: INT - Literal of a MAJ node.
        :return: INT - Child1
        '''
        assert self.is_maj(f)
        # assert not self.is_negated_literal(f)
        # assert not self.is_polymorphic_literal(f)
        n = self.deref(f)
        return n.get_maj_child1()

    def get_maj_child2(self, f):
        '''
        Return 'child2' of the MAJ node with literal 'f'.

        :param f: INT - Literal of a MAJ node.
        :return: INT - Child2
        '''
        assert self.is_maj(f)
        # assert not self.is_negated_literal(f)
        # assert not self.is_polymorphic_literal(f)
        n = self.deref(f)
        return n.get_maj_child2()


    # Buffers
    def get_buffer_in(self, b):
        '''
        Return the input of the buffer with literal 'b'.

        :param b: INIT - Literal of a buffer
        :return: INT - Input of the buffer
        '''
        assert self.is_buffer(b)
        n = self.deref(b)
        return n.get_buf_in()

    def set_buf_in(self, b, input):
        '''
        Set the input of the buffer with literal 'b' to 'input'.

        :param b: INIT - Literal of a buffer
        :param input: INT - Input of the buffer
        :return: INT - Input of the buffer
        '''
        assert self.is_buffer(b)
        n = self.deref(b)
        n.set_buf_in(input)

    def get_buffer_id(self, b):
        '''
        Get id of the buffer with literal 'b'.

        :param b: INT - Literal of a buffer
        :return: INT - buffer id
        '''
        assert self.is_buffer(b)
        n = self.deref(b)
        return n.get_buf_id()

    def skip_buffer(self, b):
        '''
        Replace the value of 'b' with the input literal with additional attributes (Attributes of 'b', including negated and polymorphic).
        This operation is carried out iteratively and stops until 'b' is not buffer-type, then return 'b'.

        :param b: INT - Literal
        :return: INT - Literal
        '''
        while self.is_buffer(b):
            b_out = PMIG.negate_literal_if_negated(self.get_buffer_in(b), b)
            b_out = PMIG.polymorphic_literal_if_polyedged(b_out, b)
            b = b_out
        assert not self.is_buffer(b)
        return b

    # Fanins
    def get_fanins(self, f):
        '''
        Get fan-ins (edges) of node with literal 'f'. Note: Only MAJ and BUFFER  has fan-in!

        :param f: INT - Literal
        :return: LIST - Literals of fan-ins
        '''
        n = self.deref(f)
        return n.get_fanins()

    def get_seq_fanins(self, f):
        '''
        Get fan-ins (edges) of node with literal 'f'. Note: Only MAJ, BUFFER, and LATCH has fan-in!

        :param f: INT - Literal
        :return: LIST - Literals of fan-ins
        '''
        n = self.deref(f)
        return n.get_seq_fanins()

    def get_fanins_positive_normal(self, f):
        '''
        Get the fan-ins (nodes) of node with literal 'f'. Note: Only MAJ and BUFFER has fan-in!

        :param f: INT - Literal
        :return: LIST - Literals of fan-ins. The attributes are deleted!
        '''
        n = self.deref(f)
        return (self.get_positive_normal_literal(fi) for fi in n.get_fanins())

    def get_seq_fanins_positive_normal(self, f):
        '''
        Get fan-ins (nodes) of node with literal 'f'. Note: Only MAJ, BUFFER, and LATCH has fan-in!

        :param f: INT - Literal
        :return: LIST - Literals of fan-ins. The attributes are deleted!
        '''
        n = self.deref(f)
        return (self.get_positive_normal_literal(fi) for fi in n.get_seq_fanins())

    # PO fanins
    def get_po_fanin(self, po):
        assert 0 <= po < len(self._pos)
        return self._pos[po][0]

    def get_po_type(self, po):
        assert 0 <= po < len(self._pos)
        return self._pos[po][1]

    def set_po_fanin(self, po, fanin):
        assert 0 <= po < len(self._pos)
        fanin_old = self.get_po_fanin(po)
        self._pos[po] = (fanin, self._pos[po][1])

        # Polymorphic
        if self.is_polymorphic_literal(fanin_old):
            if self.is_polymorphic_literal(fanin):
                self.polymorphic_edgesdict_add(fanin, _MIG_Node.PO, self.get_po_type(fanin))
            self.polymorphic_edgesdict_delete(fanin_old)
        else:
            if self.is_polymorphic_literal(fanin):
                self.polymorphic_edgesdict_add(fanin, _MIG_Node.PO, self.get_po_type(fanin))

    def set_po_type(self, po, po_type):
        assert 0 <= po < len(self._pos)
        type_old = self.get_po_type(po)
        self._pos[po] = (self._pos[po][0], po_type)

        # Polymorphic
        self.polymorphic_edgesdict_modify(self.get_po_fanin(po), _MIG_Node.PO, po_type )


    # Higher-level boolean ops
    def create_and(self, a_in, b_in):
        '''
        Create a 2-input AND gate.

        :param a_in: INT - Input a
        :param b_in: INT - Input b
        :return: INT - Literal
        '''
        return self.create_maj(self.get_literal_const0(), a_in, b_in)

    def create_or(self, a_in, b_in):
        '''
        Create a 2-input OR gate.

        :param a_in: INT - Input a
        :param b_in: INT - Input b
        :return: INT - Literal
        '''
        return self.create_maj(self.get_literal_const1(), a_in, b_in)

    def create_nand(self, a_in, b_in):
        '''
        Create a 2-input NAND gate.

        :param a_in: INT - Input a
        :param b_in: INT - Input b
        :return: INT - Literal
        '''
        return self.negate_literal_if( self.create_and(a_in, b_in), True )

    def create_nor(self, a_in, b_in):
        '''
        Create a 2-input NOR gate.

        :param a_in: INT - Input a
        :param b_in: INT - Input b
        :return: INT - Literal
        '''
        return self.negate_literal_if( self.create_or(a_in, b_in), True )

    def create_imply(self, a_in, b_in):
        '''
        Create a 2-input IMPLY gate.

        :param a_in: INT - Input a
        :param b_in: INT - Input b
        :return: INT - Literal
        '''
        return self.create_or( self.negate_literal_if(a_in, True), b_in )

    # Python special methods
    def __len__(self):
        return len(self._nodes)




