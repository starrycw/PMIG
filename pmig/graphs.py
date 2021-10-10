# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/5/23
# @Author  : c
# @File    : graphs.py
#
# Definitions of AIG and PMIG
import copy
import itertools




########################################################################################################################
# class _MIG_Node
#
# @Time    : 2021/5/26
# @Author  : c
#
# Nodes in MIG
#
#
# 2021/09: 不再支持Buffer
########################################################################################################################
class _MIG_Node:

    # Node types
    CONST0 = 0
    PI = 1
    LATCH = 2
    MAJ = 3
    # BUFFER = 4

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

    def __eq__(self, other):
        if not isinstance(other, _MIG_Node):
            return False
        if self._type != other._type:
            return False
        if self._child0 != other._child0:
            return False
        if self._child1 != other._child1:
            return False
        if self._child2 != other._child2:
            return False
        return True



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

    # @staticmethod
    # def make_buffer(buf_id, buf_in):
    #     '''
    #     Return a _MIG_Node obj whose _type is BUFFER.
    #     The _child0 and _child1 represent the id and input of this buffer, respectively.
    #     The _child2 is set to 0.
    #
    #     :param buf_id: INT - Buffer ID
    #     :param buf_in: INT - Buffer input
    #     :return: _MIG_Node
    #     '''
    #     return _MIG_Node(_MIG_Node.BUFFER, buf_id, buf_in, 0)

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

    # def is_buffer(self):
    #     '''
    #     Return Ture if and only if self._type is BUFFER.
    #
    #     :return: Boolean
    #     '''
    #     return self._type == _MIG_Node.BUFFER

    # def is_nonterminal(self):
    #     '''
    #     Return Ture if and only if this node is a non-terminal node (MAJ or BUFFER).
    #
    #     :return:
    #     '''
    #     return self._type in (_MIG_Node.MAJ, _MIG_Node.BUFFER)

    def get_fanins(self):
        '''
        Return a list containing the fan-ins of node.
        Note: Only MAJ node has fan-in!

        :return: LIST of int
        '''
        if self._type == _MIG_Node.MAJ:
            return [self._child0, self._child1, self._child2]
        # elif self._type == _MIG_Node.BUFFER:
        #     return [self._child1]
        else:
            return []

    def get_seq_fanins(self):
        '''
        Return a list containing the fan-ins of node.
        Note: Only MAJ and LATCH has fan-in!

        :return: LIST of int
        '''
        if self._type == _MIG_Node.MAJ:
            return [self._child0, self._child1, self._child2]
        # elif self._type == _MIG_Node.BUFFER:
        #     return [self._child1]
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

    # # Buffer
    # def get_buf_id(self):
    #     '''
    #     Return the _child0 (id) of a BUFFER-type _MIG_Node obj.
    #
    #     :return: INT
    #     '''
    #     assert self.is_buffer()
    #     return self._child0
    #
    # def get_buf_in(self):
    #     '''
    #     Return the _child1 (input) of a BUFFER-type _MIG_Node obj.
    #
    #     :return: INT
    #     '''
    #     assert self.is_buffer()
    #     return self._child1
    #
    # def set_buf_in(self, f):
    #     '''
    #     Set the _child1 (input) of a BUFFER-type _MIG_Node obj to f.
    #
    #     :param f: INT - New input.
    #     :return:
    #     '''
    #     assert self.is_buffer()
    #     self._child1 = f
    #
    # def convert_buf_to_pi(self, pi_id):
    #     '''
    #     Convert a BUFFER-type _MIG_Node obj to a PI-type _MIG_Node obj with pi_id (id).
    #
    #     :param pi_id: INT - The id of PI
    #     :return: _MIG_Node
    #     '''
    #     assert self.is_buffer()
    #     self._type = _MIG_Node.PI
    #     self._child0 = pi_id
    #     self._child1 = 0

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
        # elif self._type == _MIG_Node.BUFFER:
        #     type = 'BUFFER'
        elif self._type == _MIG_Node.LATCH:
            type = 'LATCH'
        else:
            type = 'UNDEFINED TYPE'

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
# 注意：这里所谓的“多态属性”是指“保持模式1的逻辑值不变，将模式2的逻辑值取反”。如果一个node的逻辑值为a/b，那么附加一个多态属性后，逻辑值为a/b'。
#
#
# 2021/09 大更新:
#
#       不再兼容buffer node。现在禁止将包含buffer node的AIG转换为MIG。
#
#       删除了部分从AIG继承的属性（比如PO_JUSTICE），在默认参数下，未定义的PO type将被转换为未定义类型。
#
#       更改了对多态属性的限制。现在通过self._polymorphic_type来限制node（这里仅包括MAJ和Latch和PO）的创建：
#           PTYPE_ALL - 允许新建以多态literal作为扇入的node;
#           PTYPE_NO - 禁止新建以多态literal作为扇入的node;
#           PTYPE_PIS_ONLY - 若新建的node以多态literal作为扇入，那么该多态literal只允许是多态PI（注意：这里PI仅指0,即只能为const 1/0或0/1）。
#           is_legal_fanin_literal方法能够判断一个literal能否作为扇入。
#
#       改名：包括很多方法的名字，以及一些变量的名字。注意，以前版本中的“多态node”和“多态edge”的概念被废弃。
#           多态literal扇入包括多态PI扇入（仅指const 0/1和1/0,不包括其它PI），也包括其它的多态literal扇入。
#           is_node_with_polymorphic_edge方法判断node是否存在多态literal扇入。
#           is_node_with_polymorphic_edge方法判断node是否存在多态PI扇入。
#
########################################################################################################################
class PMIG:

####### 宏定义
    # Latch Init
    INIT_ZERO = _MIG_Node.INIT_ZERO
    INIT_ONE = _MIG_Node.INIT_ONE
    INIT_NON = _MIG_Node.INIT_NON

    # PO types
    PO_OUTPUT = 0
    PO_UNDEFINED = 1
    PO_OBSOLETE = -1

    # polymorphic_type (no：不允许多态；all：允许多态；pis_only：仅允许const 0/1和const 1/0。)
    # 注意此PI并非指真正的PI nodes，而是指const 0（即多态PI仅包括const 0/1和1/0） ！
    PTYPE_ALL = 0
    PTYPE_NO = 1
    PTYPE_PIS_ONLY = 2
    PTYPE_List = (PTYPE_ALL, PTYPE_NO, PTYPE_PIS_ONLY)

####### __init__
    def __init__(self, name = None, polymorphic_type = PTYPE_ALL):
        self._name = name # Name
        self._strash = {} # Structural hashing table
        self._pis = [] # Literals of PIs (positive and non-polyedged)
        self._pos = [] # (Literal, type)
        self._latches = [] # Literals of latches (positive and non-polyedged)
        self._nodes = [] # _MIG_Node objs
        self._name_to_id = {} # Name-to-ID mapping. (注意：这里的id实际上并非id!而是无属性的literal！)
        self._id_to_name = {} # ID-to-Name mapping. (注意：这里的id实际上并非id!而是无属性的literal！)
        self._po_to_name = {} # PO-to-Name mapping.
        self._name_to_po = {} # Name-to-PO mapping.
        self._fanouts = {}

        self._nodes.append( _MIG_Node.make_const0() ) # The ID of CONST0 must be 0!

        assert polymorphic_type in PMIG.PTYPE_List
        self._polymorphic_type = polymorphic_type

####### __repr__
    def __repr__(self):
        return "#PMIG obj: \n Name: {} \n {} PIs, {} POs, {} MAJs, {} latches \n Polymorphic type: {} \n {} nodes have polymorphic edges \n " \
               "{} nodes have polymorphic PIs (const 0/1 or const 1/0) \n {} POs has polymorphic fanin.".format\
            ( self._name, self.n_pis(), self.n_pos(), self.n_majs(), self.n_latches(), \
             self.attr_ptype_get(), self.n_nodes_with_polymorphic_edge(), self.n_nodes_with_polymorphic_pi(), self.n_pos_with_polymorphic_edge() )
    # self._polymorphic_flag

####### __len__
    def __len__(self):
        return len(self._nodes)


####### attribute相关
    def _alarm_attr_changed(self, info):
        print("[WARNING] Protected attribute changed! ", info)


    def attr_nodeslist_get(self):
        '''
        返回 self._nodes

        :return: LIST
        '''
        nodeslist = copy.deepcopy(self._nodes)
        return nodeslist


    def attr_ptype_get(self):
        '''
        返回 多态类型，详见宏定义部分

        :return: INT
        '''
        return self._polymorphic_type


    def attr_ptype_set(self, new_type):
        '''
        设置多态类型。

        :param new_type: 详见宏定义部分
        :return:
        '''
        assert new_type in PMIG.PTYPE_List
        self._polymorphic_type = new_type
        self._alarm_attr_changed(info="self._polymorphic_type <-- {}".format(new_type))


    def attr_strash_query_if_exist(self, key):
        '''
        查询self._strash中是否存在某个key

        :param key: 无属性literal
        :return: BOOL
        '''
        return key in self._strash


    def attr_strash_get_literal(self, key):
        '''
        返回self._strash中指定键key的literal值

        :param key:
        :return:
        '''
        return self._strash.get(key)


    def attr_strash_add(self, key, value):
        '''
        向self._strash添加新的记录

        :param key:
        :param value:
        :return:
        '''
        assert not self.attr_strash_query_if_exist(key)
        assert self.is_noattribute_literal(value)
        assert isinstance(key, tuple)
        assert len(key) == 4
        self._strash[key] = value

    # self._pis
    def attr_pis_get(self, n):
        '''
        返回self._pis[n]

        :param n:
        :return:
        '''
        return self._pis[n]

    def attr_pis_append(self, value):
        assert self.is_noattribute_literal(value)
        return self._pis.append(value)

    # self._pos
    def attr_pos_get(self, n):
        return self._pos[n]

    def attr_pos_append(self, value):
        assert isinstance(value, tuple)
        assert isinstance(value[0], int)
        assert isinstance(value[1], int)
        assert len(value) == 2
        return self._pos.append(value)

    def attr_pos_set(self, n, value):
        assert 0 <= n < self.n_pos()
        assert isinstance(n, int)
        assert isinstance(value, tuple)
        assert isinstance(value[0], int)
        assert isinstance(value[1], int)
        assert len(value) == 2
        self._pos[n] = value

    # self._latches
    def attr_latches_get(self, n):
        return self._latches[n]

    def attr_latches_append(self, value):
        assert self.is_noattribute_literal(value)
        self._latches.append(value)


    # self._nodes
    def attr_nodes_get_copy(self, n):
        '''
        Return return self._nodes[n]

        :param n:
        :return:
        '''
        assert 0 <= n < self.n_nodes()
        n_copy = copy.deepcopy(self._nodes[n])
        return n_copy

    def attr_nodes_set(self, n, value):
        assert 0 <= n < self.n_nodes()
        assert isinstance(n, int)
        assert isinstance(value, _MIG_Node)
        self._nodes[n] = value

    def attr_nodes_append(self, value):
        assert isinstance(value, _MIG_Node)
        return self._nodes.append(value)




####### Const 0, 1, 0/1, 1/0
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



####### Object numbers
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

    def n_majs(self):
        '''
        Return the number of MAJ nodes.

        len(self._nodes) - 1 - self.n_pis() - self.n_latches()

        :return: INT
        '''
        return self.n_nodes() - 1 - self.n_pis() - self.n_latches()

    def n_nodes(self):
        '''
        Return len(self._nodes).

        :return: INT
        '''
        return len(self._nodes)

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



####### Object access as iterators (use list() to get a copy)
    def get_iter_pis(self):
        '''
        Return iterator of PIs (Positive and non-polymorphic literal)

        :return: ITERATOR: INT - Literal
        '''
        return ( i << 2 for i, n in enumerate(copy.deepcopy(self._nodes)) if n.is_pi() )

    def get_iter_pos(self):
        '''
        Return iterator of POs: (po_id: Order in self._pos, po_fanin: Fan-in literal, po_type: PO type).

        :return: ITERATOR: TUPLE - (po_id, po_fanin, po_type)
        '''
        return ((po_id, po_fanin, po_type) for po_id, (po_fanin, po_type) in enumerate(copy.deepcopy(self._pos)))

    def get_iter_pos_by_type(self, i_type):
        '''
        Return iterator of POs: (po_id: Order in self._pos, po_fanin: Fan-in literal, po_type == i_type: PO type).

        :param i_type:
        :return: ITERATOR: TUPLE - (po_id, po_fanin, po_type == i_type)
        '''
        return ((po_id, po_fanin, po_type) for po_id, po_fanin, po_type in self.get_iter_pos() if po_type == i_type)

    def get_iter_pos_except_specified_type(self, i_type):
        '''
        Return iterator of POs: (po_id: Order in self._pos, po_fanin: Fan-in literal, po_type != i_type: PO type).

        :param i_type:
        :return: ITERATOR: TUPLE - (po_id, po_fanin, po_type == i_type)
        '''
        return ((po_id, po_fanin, po_type) for po_id, po_fanin, po_type in self.get_iter_pos() if po_type != i_type)

    def get_iter_pos_by_fanin(self, i_fanin):
        '''
        Return iterator of POs: (po_id: Order in self._pos, po_fanin == i_fanin: Fan-in literal, po_type: PO type).

        :param i_fanin:
        :return: ITERATOR: TUPLE - (po_id, po_fanin == i_fanin, po_type)
        '''
        return ((po_id, po_fanin, po_type) for po_id, po_fanin, po_type in self.get_iter_pos() if po_fanin == i_fanin)

    def get_iter_po_fanins(self):
        '''
        Return iterator of fan-ins (literals) of PO

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

    def get_iter_majs(self):
        '''
        Return iterator of MAJs (Positive and non-polymorphic literal)

        :return: ITERATOR: INT - Literal
        '''
        return ( i << 2 for i, n in enumerate(copy.deepcopy(self._nodes)) if n.is_maj() )

    def get_iter_nodes_all(self):
        '''
        Return iterator of all nodes (Positive and non-polymorphic literal).

        :return: ITERATOR: INT - Literal
        '''
        return ( i << 2 for i, n in enumerate(copy.deepcopy(self._nodes)))




####### Polymorphic相关
    def is_node_with_polymorphic_pi(self, mig_n):
        '''
        If a node (_MIG_Node) has polymorphic fan-in PI.

        :param mig_n: _MIG_Node
        :return: Bool
        '''
        assert isinstance(mig_n, _MIG_Node)
        if not ( mig_n._type in (_MIG_Node.MAJ, _MIG_Node.LATCH) ):
            return False

        if mig_n._type == _MIG_Node.MAJ:
            if mig_n.get_maj_child0() in (self.get_literal_const_0_1(), self.get_literal_const_1_0()):
                return True
            if mig_n.get_maj_child1() in (self.get_literal_const_0_1(), self.get_literal_const_1_0()):
                return True
            if mig_n.get_maj_child2() in (self.get_literal_const_0_1(), self.get_literal_const_1_0()):
                return True
            return False

        elif mig_n._type == _MIG_Node.LATCH:
            if mig_n.get_latch_next() in (self.get_literal_const_0_1(), self.get_literal_const_1_0()):
                return True
            return False

        else:
            assert False

    def is_node_with_polymorphic_edge(self, mig_n):
        '''
        If a node has polymorphic fan-in edge (包含多态PI).

        :param mig_n: _MIG_Node
        :return: Bool
        '''
        assert isinstance(mig_n, _MIG_Node)
        # if not ( mig_n._type in (_MIG_Node.MAJ, _MIG_Node.LATCH) ):
        #     return False
        if mig_n._type == _MIG_Node.MAJ:
            if self.is_polymorphic_literal( mig_n.get_maj_child0() ):
                return True
            if self.is_polymorphic_literal( mig_n.get_maj_child1() ):
                return True
            if self.is_polymorphic_literal( mig_n.get_maj_child2() ):
                return True
            return False

        elif mig_n._type == _MIG_Node.LATCH:
            if self.is_polymorphic_literal( mig_n.get_latch_next() ):
                return True
            return False

        else:
            assert mig_n._type in ( _MIG_Node.CONST0, _MIG_Node.PI )


    def get_iter_nodes_with_polymorphic_pi(self):
        '''
        Return literals of nodes with polymorphic fan-in PI.

        :return:
        '''
        return (i << 2 for i, n in enumerate(copy.deepcopy(self._nodes)) if self.is_node_with_polymorphic_pi(n))

    def get_iter_nodes_with_polymorphic_edge(self):
        '''
        Return literals of nodes with polymorphic fan-in edge.

        :return:
        '''
        return (i << 2 for i, n in enumerate(copy.deepcopy(self._nodes)) if self.is_node_with_polymorphic_edge(n))

    def get_iter_pos_with_polymorphic_fanin(self):
        '''
        Return POs: (po_id, po_fanin, po_type) with po_fanin is polymorphic literal.

        :return:
        '''
        return ((po_id, po_fanin, po_type) for po_id, (po_fanin, po_type) in enumerate(copy.deepcopy(self._pos)) if self.is_polymorphic_literal(po_fanin))

    def n_nodes_with_polymorphic_pi(self):
        cnt = 0
        for i in self.get_iter_nodes_with_polymorphic_pi():
            cnt = cnt + 1
        return cnt

    def n_nodes_with_polymorphic_edge(self):
        cnt = 0
        for i in self.get_iter_nodes_with_polymorphic_edge():
            cnt = cnt + 1
        return cnt

    def n_pos_with_polymorphic_edge(self):
        '''
        注意，PO本身不会施加额外属性，其扇入即为PO

        :return:
        '''
        cnt = 0
        for (po_id, po_fanin, po_type) in self.get_iter_pos_with_polymorphic_fanin():
            cnt = cnt + 1
        return cnt

    def n_pos_with_polymorphic_pi(self):
        cnt = 0
        for (po_id, po_fanin, po_type) in self.get_iter_pos_with_polymorphic_fanin():
            if po_fanin in (self.get_literal_const_0_1(), self.get_literal_const_1_0()):
                cnt = cnt + 1
        return cnt


    def is_legal_fanin_literal(self, l):
        '''
        Check if the node with fan-in 'l' can be created.

        :param l: INT - literal
        :return: Bool
        '''

        if self.is_polymorphic_literal(l):
            if self.attr_ptype_get() == PMIG.PTYPE_NO:
                return False
            elif self.attr_ptype_get() == PMIG.PTYPE_ALL:
                return True
            elif self.attr_ptype_get() == PMIG.PTYPE_PIS_ONLY:
                if l in (self.get_literal_const_0_1(), self.get_literal_const_1_0()):
                    return True
                else:
                    return False
            else:
                assert False
        else:
            return True







####### Attribute of literal
    @staticmethod
    def is_negated_literal(f):
        '''
        Return TRUE if the literal f has negated attribute.

        :param f: INT - Literal
        :return: Bool
        '''
        assert isinstance(f, int)
        return (f & 1) != 0

    @staticmethod
    def is_polymorphic_literal(f):
        '''
        Return True if the literal f has polymorphic attribute.

        :param f: INT - Literal
        :return: Bool
        '''
        assert isinstance(f, int)
        return (f & 2) != 0

    @staticmethod
    def is_noattribute_literal(f):
        '''
        检查f是否为无属性的（非反相非多态）

        :param f:
        :return:
        '''
        if PMIG.is_polymorphic_literal(f):
            return False
        if PMIG.is_negated_literal(f):
            return False
        else:
            return True

    @staticmethod
    def get_positive_literal(f):
        '''
        Return the literal with positive attribute.

        :param f: INT - Literal
        :return: INT - Literal
        '''
        assert isinstance(f, int)
        return (f & ~1)

    @staticmethod
    def get_normal_literal(f):
        '''
        Return the literal with non-polyedge attribute.

        :param f: INT - Literal
        :return: INT - Literal
        '''
        assert isinstance(f, int)
        return (f & ~2)

    @staticmethod
    def get_noattribute_literal(f):
        '''
        Return the literal with positive and non-polymorphic attribute.

        :param f: INT - Literal
        :return: INT - Literal
        '''
        assert isinstance(f, int)
        return (f & ~3)

    @staticmethod
    def negate_literal_if(f, c):
        '''
        Invert the LSB of f if c is True.

        :param f: INT - Literal
        :param c: Bool
        :return: INT - Literal
        '''
        assert isinstance(f, int)
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
        assert isinstance(f, int)
        assert isinstance(c, int)
        return f ^ (c & 1)

    @staticmethod
    def polymorphic_literal_if(f, c):
        '''
        Invert the polymorphic flag of f if c is True.

        :param f: INT - Literal
        :param c: Bool
        :return: INT - Literal
        '''
        assert isinstance(f, int)
        if c:
            return f ^ 2  # xor
        else:
            return f

    @staticmethod
    def polymorphic_literal_if_polymorphic(f, c):
        '''
        Invert the polymorphic flag of f if c is polymorphic.

        :param f: INT - Literal
        :param c: INT - Literal
        :return: INT - Literal
        '''
        assert isinstance(f, int)
        assert isinstance(c, int)
        return f ^ (c & 2)


    @staticmethod
    def negate_maj_fanins_literal_if(child0, child1, child2, c):
        '''
        Return a tuple containing the literal of child0~child2, and the three literals are negated if c is True.

        :param child0: INT - Literal
        :param child1: INT - Literal
        :param child2: INT - Literal
        :param c: Bool
        :return: TUPLE: (INT, INT, INT)
        '''
        return (PMIG.negate_literal_if(child0, c), PMIG.negate_literal_if(child1, c), PMIG.negate_literal_if(child2, c))

    @staticmethod
    def polymorphic_maj_fanins_literal_if(child0, child1, child2, c):
        '''
        Return a tuple containing the literal of child0~child2, and the three literals are polymorphic-ed if c is True.

        :param child0: INT - Literal
        :param child1: INT - Literal
        :param child2: INT - Literal
        :param c: Bool
        :return:TUPLE: (INT, INT, INT)
        '''
        return (PMIG.polymorphic_literal_if(child0, c), PMIG.polymorphic_literal_if(child1, c), PMIG.polymorphic_literal_if(child2, c) )

    @staticmethod
    def negate_and_polymorphic_maj_fanins_literal_if(child0, child1, child2, c):
        '''
        Return a tuple containing the literal of child0~child2, and the three literals are negated and polymorphic-ed if c is True.

        :param child0: INT - Literal
        :param child1: INT - Literal
        :param child2: INT - Literal
        :param c: Bool
        :return: TUPLE: (INT, INT, INT)
        '''
        child0_ne, child1_ne, child2_ne = PMIG.negate_maj_fanins_literal_if(child0, child1, child2, c)
        child0_ne_po, child1_ne_po, child2_ne_po = PMIG.polymorphic_maj_fanins_literal_if(child0_ne, child1_ne, child2_ne, c)
        return (child0_ne_po, child1_ne_po, child2_ne_po)

    @staticmethod
    def add_attr_if_has_attr(f, c):
        '''
        Invert the negated/polymorphic flag of f if c is negated/polymorphic.

        :param f: INT - Literal
        :param c: INT - Literal
        :return: INT - Literal
        '''
        f_ne = PMIG.negate_literal_if_negated(f, c)
        f_ne_po = PMIG.polymorphic_literal_if_polymorphic(f_ne, c)
        return f_ne_po




####### Name相关
    def attr_get_pmig_name(self):
        '''
        Get the name of this PMIG.

        :return: ANY
        '''
        return self._name


    def set_name(self, f, name):
        '''
        Set name of f. f should be a positive non-polymorphic literal!

        :param f: INT - A positive non-polyedged literal
        :param name: STRING
        :return:
        '''
        assert self.is_noattribute_literal(f)
        assert not self.has_name(f)
        assert not self.name_exists(name)
        assert not (' ' in name), "[ERROR] Spaces are not allowed in node names! "

        self._name_to_id[name] = f
        self._id_to_name[f] = name


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


    def get_id_by_name(self, name):
        '''
        Get ID (The ID here is positive non-polymorphic literal!) by name.

        :param name: STRING - Name
        :return: INT - A positive non-polyedged literal
        '''
        return self._name_to_id[name]

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
        assert 0 <= po < self.n_pos()
        assert name not in self._name_to_po
        assert po not in self._po_to_name
        assert not (' ' in name), "[ERROR] Spaces are not allowed in PO names! "

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

    def get_name_by_po_if_has(self, po):
        if self.po_has_name(po):
            return self.get_name_by_po(po)
        else:
            return None

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



####### Create basic objects
    def create_pi(self, name = None):
        '''
        Create a PI-type node.

        :param name: STRING - Name
        :return: INT - Literal of the node
        '''

        pi_id = self.n_pis()
        n = _MIG_Node.make_pi(pi_id)
        fn = self.n_nodes() << 2

        self.attr_nodes_append(n)
        self.attr_pis_append(fn)

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
        # Fanin Checks
        assert self.is_legal_fanin_literal(next)

        l_id = self.n_latches()
        n = _MIG_Node.make_latch(l_id, init, next)
        fn = self.n_nodes() << 2

        self.attr_nodes_append(n)
        self.attr_latches_append(fn)

        if name is not None:
            self.set_name(fn, name)

        return fn

    def create_maj(self, child0, child1, child2):
        '''
        Return the literal of Y = MAJ(child0, child1, child2).
        If MAJ(child0, child1, child2) can be implemented by an existing node with additional 'negated' and 'polymorphic' attributes, then return the corresponding literal.
        If not, create a new MAJ node.

        :param child0: INT - Literal
        :param child1: INT - Literal
        :param child2: INT - Literal
        :return: INT - Literal
        '''
        # return self.create_maj_with_additional_checks(child0=child0, child1=child1, child2=child2)
        assert self.is_legal_fanin_literal(child0)
        assert self.is_legal_fanin_literal(child1)
        assert self.is_legal_fanin_literal(child2)

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
        # if key in self._strash:
        # return self._strash[key]
        if self.attr_strash_query_if_exist(key):
            return self.attr_strash_get_literal(key)

        # Additional structural hashing checks
        child0_ne, child1_ne, child2_ne = self.negate_maj_fanins_literal_if(child0, child1, child2, True)
        key_negated = (_MIG_Node.MAJ, child0_ne, child1_ne, child2_ne)
        if self.attr_strash_query_if_exist(key_negated):
            return self.negate_literal_if(self.attr_strash_get_literal(key_negated), True)

        child0_po, child1_po, child2_po = self.polymorphic_maj_fanins_literal_if(child0, child1, child2, True)

        if child0_po > child1_po:
            child0_po, child1_po = child1_po, child0_po
        if child1_po > child2_po:
            child1_po, child2_po = child2_po, child1_po
        if child0_po > child1_po:
            child0_po, child1_po = child1_po, child0_po

        key_polyed = (_MIG_Node.MAJ, child0_po, child1_po, child2_po)

        if self.attr_strash_query_if_exist(key_polyed):
            return self.polymorphic_literal_if(self.attr_strash_get_literal(key_polyed), True)

        child0_ne_po, child1_ne_po, child2_ne_po = self.negate_and_polymorphic_maj_fanins_literal_if(child0, child1, child2, True)

        if child0_ne_po > child1_ne_po:
            child0_ne_po, child1_ne_po = child1_ne_po, child0_ne_po
        if child1_ne_po > child2_ne_po:
            child1_ne_po, child2_ne_po = child2_ne_po, child1_ne_po
        if child0_ne_po > child1_ne_po:
            child0_ne_po, child1_ne_po = child1_ne_po, child0_ne_po

        key_negated_polyed = (_MIG_Node.MAJ, child0_ne_po, child1_ne_po, child2_ne_po)

        if self.attr_strash_query_if_exist(key_negated_polyed):
            return self.polymorphic_literal_if(
                self.negate_literal_if(self.attr_strash_get_literal(key_negated_polyed), True),
                True)


        fn = self.n_nodes() << 2
        n = _MIG_Node.make_maj(child0, child1, child2)
        self.attr_nodes_append(n)
        self.attr_strash_add(key, fn)

        return fn


    def create_po(self, f = 0, name = None, po_type = PO_OUTPUT):
        '''
        Create PO.

        :param f:
        :param name:
        :param po_type:
        :return:
        '''

        assert self.is_legal_fanin_literal(f)

        po_id = self.n_pos()
        # self._pos.append( (f, po_type) )
        self.attr_pos_append( (f, po_type) )

        if name is not None:
            self.set_po_name(po_id, name)

        # # Polymorphic
        # if self.is_polymorphic_literal(f):
        #     self.polymorphic_edgesdict_add(f, _MIG_Node.PO, po_type)

        return po_id


####### deref
    def deref_copy(self, f):
        '''
        Get the node of a literal.

        :param f: INT - Literal
        :return: _MIG_Node - Node
        '''
        # return self._nodes[ f >> 2 ]
        return self.attr_nodes_get_copy( f >> 2 )

    def deref(self, f):
        '''
        Get the node of a literal.

        :param f: INT - Literal
        :return: _MIG_Node - Node
        '''
        # return self._nodes[ f >> 2 ]
        n = f >> 2
        assert 0 <= n < self.n_nodes()
        return self._nodes[n]

####### Query IDs
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
        n = self.deref_copy(f)
        return n.is_const0()

    def is_pi(self, f):
        '''
        Return True if 'f' is a literal of PI-type node.

        :param f: INT - Literal
        :return: Bool
        '''
        # assert isinstance(self, PMIG)
        n = self.deref_copy(f)
        return n.is_pi()

    def is_latch(self, f):
        '''
        Return True if 'f' is a literal of LATCH-type node.

        :param f: INT - Literal
        :return: Bool
        '''
        # assert isinstance(current_pmig, PMIG)
        n = self.deref_copy(f)
        return n.is_latch()

    def is_maj(self, f):
        # assert isinstance(current_pmig, PMIG)
        '''
        Return True if 'f' is a literal of MAJ-type node.

        :param f: INT - Literal
        :return: Bool
        '''
        n = self.deref_copy(f)
        return n.is_maj()


####### PIs
    def get_pi_by_id(self, pi_id):
        '''
        Return 'self._pis[pi_id]'.

        :param pi_id: INT - ID (Literal >> 2)
        :return: INT - Literal
        '''
        # return self._pis[pi_id]
        return self.attr_pis_get(pi_id)

####### Latches
    def get_latch_init(self, l):
        '''
        Return the init state of the latch with literal 'l'.

        :param l: INT - Literal of a latch
        :return: INT - The init state of the latch
        '''
        # assert not self.is_negated_literal(l)
        # assert not self.is_polymorphic_literal(l)
        assert self.is_latch(l)
        n = self.deref_copy(l)
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
        n = self.deref_copy(l)
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
        # Polymorphic Checks
        assert self.is_legal_fanin_literal(next)
        assert self.is_latch(l)
        n = self.deref(l)
        n.set_latch_next(next)


####### MAJ
    def get_maj_fanins(self, f):
        '''
        Return a tuple with the 3 child of the MAJ node with literal 'f'.

        :param f: INT - Literal of a MAJ node.
        :return: TUPLE (INT, INT, INT) - (child0, child1, child2)
        '''
        assert self.is_maj(f)
        # assert not self.is_negated_literal(f)
        # assert not self.is_polymorphic_literal(f)
        n = self.deref_copy(f)
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
        n = self.deref_copy(f)
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
        n = self.deref_copy(f)
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
        n = self.deref_copy(f)
        return n.get_maj_child2()


####### Fanins
    def get_fanins(self, f):
        '''
        Get fan-ins (edges) of node with literal 'f'. Note: Only MAJ and BUFFER  has fan-in!

        :param f: INT - Literal
        :return: LIST - Literals of fan-ins
        '''
        n = self.deref_copy(f)
        return n.get_fanins()

    def get_seq_fanins(self, f):
        '''
        Get fan-ins (edges) of node with literal 'f'. Note: Only MAJ, BUFFER, and LATCH has fan-in!

        :param f: INT - Literal
        :return: LIST - Literals of fan-ins
        '''
        n = self.deref_copy(f)
        return n.get_seq_fanins()

    def get_fanins_without_attribute(self, f):
        '''
        Get the fan-ins (nodes) of node with literal 'f'. Note: Only MAJ and BUFFER has fan-in!

        :param f: INT - Literal
        :return: LIST - Literals of fan-ins. The attributes are deleted!
        '''
        n = self.deref_copy(f)
        return (self.get_noattribute_literal(fi) for fi in n.get_fanins())

    def get_seq_fanins_without_attribute(self, f):
        '''
        Get fan-ins (nodes) of node with literal 'f'. Note: Only MAJ, BUFFER, and LATCH has fan-in!

        :param f: INT - Literal
        :return: LIST - Literals of fan-ins. The attributes are deleted!
        '''
        n = self.deref_copy(f)
        return (self.get_noattribute_literal(fi) for fi in n.get_seq_fanins())

####### PO fanins
    def get_po_fanin(self, po):
        assert 0 <= po < self.n_pos()
        # return self._pos[po][0]
        return self.attr_pos_get(po)[0]

    def get_po_type(self, po):
        assert 0 <= po < self.n_pos()
        # return self._pos[po][1]
        return self.attr_pos_get(po)[1]

    def set_po_fanin(self, po, fanin):
        # Polymorphic Checks
        assert self.is_legal_fanin_literal(fanin)

        assert 0 <= po < self.n_pos()
        fanin_old = self.get_po_fanin(po)
        # self._pos[po] = (fanin, self._pos[po][1])
        self.attr_pos_set(po, (fanin, self.get_po_type(po)))


    def set_po_type(self, po, po_type):
        assert 0 <= po < self.n_pos()
        type_old = self.get_po_type(po)
        # self._pos[po] = (self._pos[po][0], po_type)
        self.attr_pos_set(po, (self.get_po_fanin(po), po_type))


    def set_po_obsolete(self, po):
        assert 0 <= po < self.n_pos()
        self.set_po_type(po=po, po_type=self.PO_OBSOLETE)


####### Higher-level boolean ops
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



####### Convert AIG to PMIG
    @staticmethod
    def convert_aig_to_pmig(aig_obj, mig_name = None, allow_latch = True, custom_po_conversion = None, ptype_of_created_pmig = PTYPE_NO, echo_mode = 3):
        '''
        Convert a AIG obj to PMIG obj.

        - Param: allow_latch:

        -- Flase (Default) - No

        -- True - Yes

        - Param: custom_po_conversion:

        -- DICT - Dict ALLOWED_AIG_PO_TYPE specify how the PO type is mapped from AIG to PMIG. It must contain {"undefined": PMIG.PO_UNDEFINED} in order to map undefined PO types.
                  Example: {graphs.AIG.OUTPUT: graphs.PMIG.PO_OUTPUT, "undefined": graphs.PMIG.PO_UNDEFINED, graphs.AIG.JUSTICE: graphs.PMIG.PO_JUSTICE}
is_legal_fanin_literal
        -- None(Default) - Dict ALLOWED_AIG_PO_TYPE is set to default

        :param aig_obj: AIG obj
        :param mig_name: STRING - MIG name
        :param allow_latch: Bool
        :param custom_po_conversion: None(Default) or DICT
        :param ptype_of_created_pmig: INT - PTYPE_xxx，默认为PTYPE_NO
        :param echo_mode: INT
        :return: PMIG obj
        '''

        if echo_mode > 1: print("[INFO] pmig/graph/PMIG.convert_aig_to_mig: Start the conversion from [ AIG:",  aig_obj._name,\
                          "] to [ PMIG:", mig_name, "] ......")
        # Variables
        MAPPING_AIG_PO_TYPE = {AIG.OUTPUT: PMIG.PO_OUTPUT, "undefined": PMIG.PO_UNDEFINED}
        ADDITIONAL_CHECKS = True
        if custom_po_conversion:
            assert isinstance(custom_po_conversion, dict)
            assert "undefined" in custom_po_conversion
            MAPPING_AIG_PO_TYPE = custom_po_conversion

        # Literal conversion tools
        def fanin_literal_aig_to_pmig(aig_fanin_literal):
            return ( AIG.negate_if_negated(aig_fanin_literal, aig_fanin_literal) << 1 ) + ( aig_fanin_literal & 1 )

        # Some checks
        assert isinstance(aig_obj, AIG)
        assert aig_obj._nodes[0].is_const0()

        # Create an PMIG obj
        pmig_obj = PMIG(name=mig_name, polymorphic_type=ptype_of_created_pmig)

        # Convert _AIG_Node to _MIG_Node
        for node_i, node_n in enumerate(aig_obj._nodes):
            assert isinstance(node_n, _AIG_Node)
            assert not ( node_n.is_const0() and node_i > 0)
            assert ( not node_n.is_buffer() ), "[ERROR] pmig/graph/PMIG.convert_aig_to_mig: No buffer!"
            # CONST0
            if node_n.is_const0():
                assert node_i == 0

            # PI
            elif node_n.is_pi():
                pi_id = node_n.get_pi_id()
                pi_name = None
                pi_literal = node_i << 2
                if aig_obj.has_name( pi_literal >> 1 ):
                    pi_name = aig_obj.get_name_by_id( pi_literal >> 1)

                return_literal = pmig_obj.create_pi(name=pi_name)
                if echo_mode > 1:
                    print("[INFO] pmig/graph/PMIG.convert_aig_to_mig: Convert PI", pi_id, "of AIG (", aig_obj._name,\
                          ") to PI of PMIG (", mig_name, "). Literal:", aig_obj._pis[pi_id], "-->", return_literal, ". Name:", pi_name)

                # Checks
                if ADDITIONAL_CHECKS:
                    # assert pmig_obj._pis[-1] == pi_literal
                    assert pmig_obj.attr_pis_get(-1) == pi_literal
                    assert return_literal == pi_literal
                    assert pmig_obj.n_pis() == pi_id + 1
                    assert aig_obj._pis[pi_id] == return_literal >> 1

            # LATCH
            elif node_n.is_latch():
                assert allow_latch, "[ERROR] pmig/graph/PMIG.convert_aig_to_mig: Latch-type node is not allowed!"

                latch_init_new = PMIG.INIT_ZERO
                if node_n.get_latch_init() == AIG.INIT_ONE:
                    latch_init_new = PMIG.INIT_ONE
                elif node_n.get_latch_init() == AIG.INIT_NONDET:
                    latch_init_new = PMIG.INIT_NON
                else:
                    assert node_n.get_latch_init() == AIG.INIT_ZERO

                latch_next_aig = node_n.get_latch_next()
                latch_next_new = fanin_literal_aig_to_pmig(latch_next_aig)
                latch_id = node_n.get_latch_id()
                latch_name = None
                latch_literal = node_i << 2
                if aig_obj.has_name( latch_literal >> 1 ):
                    latch_name = aig_obj.get_name_by_id(latch_literal >> 1)

                return_literal = pmig_obj.create_latch(name=latch_name, init=latch_init_new, next=latch_next_new)

                if echo_mode > 1:
                    print("[INFO] pmig/graph/PMIG.convert_aig_to_mig: Convert LATCH", latch_id, "of AIG (", aig_obj._name,\
                          ") to LATCH of PMIG (", mig_name, "). Literal:", aig_obj._latches[latch_id], "-->", return_literal, \
                          ". Next state literal:", latch_next_aig, "-->", latch_next_new, ". Name:", latch_name)

                # Checks
                if ADDITIONAL_CHECKS:
                    # assert pmig_obj._latches[-1] == latch_literal
                    assert pmig_obj.attr_latches_get(-1) == latch_literal
                    assert return_literal == latch_literal
                    assert pmig_obj.n_latches() == latch_id + 1
                    assert aig_obj._latches[latch_id] == return_literal >> 1
                    assert fanin_literal_aig_to_pmig(node_n.get_latch_next()) == latch_next_new

            # AND to MAJ
            elif node_n.is_and():
                and_left = node_n.get_left()
                and_right = node_n.get_right()
                and_literal = node_i << 2
                maj_child0 = fanin_literal_aig_to_pmig(and_left)
                maj_child1 = fanin_literal_aig_to_pmig(and_right)

                return_literal = pmig_obj.create_maj(maj_child0, maj_child1, pmig_obj.get_literal_const0())

                and_name = None
                if aig_obj.has_name(and_literal >> 1):
                    and_name = aig_obj.get_name_by_id(and_literal >> 1)
                    # aig_obj.set_name(return_literal, and_name)
                    pmig_obj.set_name(f=return_literal, name=and_name)

                if echo_mode > 1:
                    print("[INFO] pmig/graph/PMIG.convert_aig_to_mig: Convert AND of AIG (", aig_obj._name,\
                          ") to MAJ of PMIG (", mig_name, "). Literal:", node_i << 1, "-->", return_literal, \
                          ". Fan-ins:", (and_left, and_right), "-->", pmig_obj.get_maj_fanins(return_literal), ". Name:", and_name)

                # Checks
                if ADDITIONAL_CHECKS:
                    assert return_literal == node_i << 2
                    # assert pmig_obj._nodes[node_i].is_maj()
                    assert pmig_obj.attr_nodes_get_copy(node_i).is_maj()
                    assert fanin_literal_aig_to_pmig(and_left) == pmig_obj.get_maj_child2(return_literal)
                    assert fanin_literal_aig_to_pmig(and_right) == pmig_obj.get_maj_child1(return_literal)
                    assert pmig_obj.get_maj_child0(return_literal) == 0

            # Buffer
            elif node_n.is_buffer():
                assert False, "[ERROR] pmig/graph/PMIG.convert_aig_to_mig: Buffer-type node is not allowed!"

            # Unknown
            else:
                assert False, "[ERROR] pmig/graph/PMIG.convert_aig_to_mig: Unknown node type!"

        # Convert PO
        for po_id, po_fanin, po_type_aig in aig_obj.get_pos():
            # PO type
            if po_type_aig not in MAPPING_AIG_PO_TYPE:
                po_type_new = MAPPING_AIG_PO_TYPE["undefined"]
            else:
                po_type_new = MAPPING_AIG_PO_TYPE[po_type_aig]

            # PO fan-in
            po_fanin_new = fanin_literal_aig_to_pmig(po_fanin)

            po_name = None
            if aig_obj.po_has_name(po_id):
                po_name = aig_obj.get_name_by_po(po_id)
            return_id = pmig_obj.create_po(f=po_fanin_new, name=po_name, po_type = po_type_new)

            if echo_mode > 1:
                print("[INFO] pmig/graph/PMIG.convert_aig_to_mig: Convert PO", po_id, "of AIG (",aig_obj._name, \
                      ") to PO of PMIG (", mig_name, "). Fan-in literal:", po_fanin, "-->", po_fanin_new, \
                      ". Type:", po_type_aig, "-->", po_type_new, ". Name:", po_name)

            # Checks
            if ADDITIONAL_CHECKS:
                assert return_id == po_id
                # assert pmig_obj._pos[-1] == (po_fanin_new, po_type_new)
                assert pmig_obj.attr_pos_get(-1) == (po_fanin_new, po_type_new)
                assert pmig_obj.n_pos() == po_id + 1
                # assert pmig_obj._pos[po_id][0] == fanin_literal_aig_to_pmig(po_fanin)
                assert pmig_obj.get_po_fanin(po_id) == fanin_literal_aig_to_pmig(po_fanin)


        if echo_mode > 1: print("[INFO] pmig/graph/PMIG.convert_aig_to_mig: Conversion from [ AIG:",  aig_obj._name,\
                          "] to [ PMIG:", mig_name, "] is completed!")
        return pmig_obj

    def get_cone(self, roots, stop = [], fanins = get_fanins_without_attribute):
        '''
        Return the cone of 'roots', stop at 'stop'

        :param roots: ITREABLE OBJ.
        :param stop: LIST
        :param fanins: METHOD - get_fanins_without_attribute(Default, return fanins of MAJ and BUF)
        :return: SET
        '''
        visited = set()
        dfs_stack = list(roots)

        while dfs_stack:

            cur = self.get_noattribute_literal(dfs_stack.pop())
            if (cur in visited) or (cur in stop):
                continue

            visited.add(cur)

            for fi in fanins(self, cur):
                if fi not in visited:
                    dfs_stack.append(fi)

        return sorted(visited)

    def get_seq_cone(self, roots, stop=[]):
        '''
        Return the seq cone of 'roots', stop at 'stop'

        :param roots: ITREABLE OBJ.
        :param stop: LIST
        :return: SET
        '''
        return self.get_cone(roots=roots, stop=stop, fanins=PMIG.get_seq_fanins_without_attribute)

    class fset:
        def __init__(self, fs=[]):
            self.s = set(PMIG.get_noattribute_literal(f) for f in fs)

        def __contains__(self, item):
            return PMIG.get_noattribute_literal(item) in self.s

        def __len__(self):
            return len(self.s)

        def __iter__(self):
            return self.s.__iter__()

        def add(self, f):
            f = PMIG.get_noattribute_literal(f)
            res = f in self.s
            self.s.add(f)
            return res

        def remove(self, f):
            return self.s.remove(PMIG.get_noattribute_literal(f))

    def topological_sort(self, roots, stop = ()):
        '''
        Topologically sort the combinatorial cone of 'roots', stop at 'stop'

        :param roots:
        :param stop:
        :return:
        '''
        def fanins(f):
            if f in stop:
                return []
            return [fi for fi in self.get_fanins_without_attribute(f)]

        visited = PMIG.fset()
        dfs_stack = []

        for root in roots:

            if visited.add(root):
                continue

            dfs_stack.append( (root, fanins(root)) )

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

                dfs_stack.append( (d, [fi for fi in fanins(d) if fi not in visited]) )

    class node_map:
        def __init__(self):
            self._nodemap_original_to_new = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
            self._nodemap_new_to_original = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
            self._node_id = 1

        def add_node_mapping(self, literal_original, literal_new):
            l_original = PMIG.get_noattribute_literal(literal_original)
            l_new = PMIG.get_noattribute_literal(literal_new)
            assert l_new == self._node_id << 2
            assert l_original not in self._nodemap_original_to_new
            assert l_new not in self._nodemap_new_to_original
            self._nodemap_original_to_new[l_original] = l_new
            self._nodemap_new_to_original[l_new] = l_original
            self._node_id = self._node_id + 1

        def get_new_literal(self, literal_original):
            l_original = PMIG.get_noattribute_literal(literal_original)
            assert l_original in self._nodemap_original_to_new
            l_new = self._nodemap_original_to_new[l_original]
            return PMIG.add_attr_if_has_attr(l_new, literal_original)

    def pmig_clean_irrelevant_nodes(self, pos=None):
        '''
        Return a new PMIG obj, only containing the nodes relevant to specified outputs (pos).

        :param pos: None (Default) or LIST - Specified outputs.
        :return:
        '''
        nmap = PMIG.node_map()
        if pos is None:
            # print(self.n_pos())
            pos = range(0, self.n_pos())
        pos_set = set(pos)
        pmig_new = PMIG(polymorphic_type=self.attr_ptype_get())

        # relevant_literals = self.get_seq_cone(self.get_po_fanin(po_id) for po_id in pos_set)
        fanins_of_selected_pos = [self.get_po_fanin(po=po_id) for po_id in pos_set]
        relevant_literals = self.get_seq_cone(roots=fanins_of_selected_pos)

        # Create lists of PI and other nodes
        pis_list = []
        nodes_list = []
        for literal_i in self.topological_sort(relevant_literals):
            assert isinstance(literal_i, int)
            # assert not self.is_negated_literal(literal_i)
            # assert not self.is_polymorphic_literal(literal_i)
            assert self.is_noattribute_literal(literal_i)

            if self.is_const0(literal_i):
                assert literal_i == 0
                continue

            elif self.is_pi(literal_i):
                pis_list.append(literal_i)
            else:
                assert self.is_maj(literal_i) or self.is_latch(literal_i)
                nodes_list.append(literal_i)

        # Create nodes
        for literal_i in (pis_list + nodes_list):

            if self.is_pi(literal_i):
                if self.has_name(literal_i):
                    new_l = pmig_new.create_pi(name=self.get_name_by_id(literal_i))
                else:
                    new_l = pmig_new.create_pi()
                nmap.add_node_mapping(literal_i, new_l)

            elif self.is_latch(literal_i):
                latch_init = self.get_latch_init(literal_i)
                latch_next = self.get_latch_next(literal_i)
                new_latch_init = nmap.get_new_literal(latch_init)
                new_latch_next = nmap.get_new_literal(latch_next)
                if self.has_name(literal_i):
                    new_l = pmig_new.create_latch(name=self.get_name_by_id(literal_i), init=new_latch_init, next=new_latch_next)
                else:
                    new_l = pmig_new.create_latch(init=new_latch_init, next=new_latch_next)
                nmap.add_node_mapping(literal_i, new_l)

            elif self.is_maj(literal_i):
                maj_ch0 = self.get_maj_child0(literal_i)
                maj_ch1 = self.get_maj_child1(literal_i)
                maj_ch2 = self.get_maj_child2(literal_i)
                new_maj_ch0 = nmap.get_new_literal(maj_ch0)
                new_maj_ch1 = nmap.get_new_literal(maj_ch1)
                new_maj_ch2 = nmap.get_new_literal(maj_ch2)
                # print(new_maj_ch0, new_maj_ch1, new_maj_ch2)
                new_l = pmig_new.create_maj(child0=new_maj_ch0, child1=new_maj_ch1, child2=new_maj_ch2)
                if self.has_name(literal_i):
                    pmig_new.set_name(new_l, self.get_name_by_id(literal_i))
                nmap.add_node_mapping(literal_i, new_l)

            else:
                assert False

        # Create POs
        for po_i in pos_set:
            po_fanin = self.get_po_fanin(po_i)
            po_type = self.get_po_type(po_i)
            new_po_fanin = nmap.get_new_literal(po_fanin)

            if self.po_has_name(po_i):
                pmig_new.create_po(f=new_po_fanin, name=self.get_name_by_po(po_i), po_type=po_type)
            else:
                pmig_new.create_po(f=new_po_fanin, po_type=po_type)
        # print(nmap._nodemap_original_to_new.items())
        return pmig_new

    def pmig_clean_pos_by_type(self, po_type_tuple = (PO_OBSOLETE, )):
        '''
        Remove the POs of specified types.

        :param po_type_tuple: TUPLE - Containing the PO types. eg. (PMIG.PO_OBSOLETE, PMIG.PO_UNDEFINED). Default: (PMIG.PO_OBSOLETE, )
        :return: PMIG obj
        '''
        reserved_po_list = []
        for po_id, po_fanin, po_type in self.get_iter_pos():
            if not po_type in po_type_tuple:
                # print(">>>>>", po_id, po_type, po_fanin)
                reserved_po_list.append(po_id)
        # print(reserved_po_list)
        return self.pmig_clean_irrelevant_nodes(pos=reserved_po_list)







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
















