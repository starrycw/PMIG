# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/9/25
# @Author  : c
# @File    : graphs_ops.py


####### import
import random

from pmig import graphs
from pmig import exact_synthesis
from pmig import pmig_logic
PMIG = graphs.PMIG # alias

from prettytable import PrettyTable
import copy

########################################################################################################################
# class PMIG_operator
#
# @Time    : 2021/10
# @Author  : c
#
# 包含对PMIG进行基本操作的方法。这些方法应当是静态方法。
#
#
########################################################################################################################
class PMIG_operator:
#######
    def __init__(self):
        self._pmig_obj = None # 作为操作对象的PMIG，它不应当被修改
        self._ptype = None # PMIG的多态类型

#######
    def initialization(self, mig_obj):
        assert isinstance(mig_obj, PMIG)
        self._pmig_obj = copy.deepcopy(mig_obj)
        self._ptype = self._pmig_obj.attr_ptype_get()

#######
    @staticmethod
    def _function_verification_random(mig_obj_1, mig_obj_2, n_random_veri):
        '''
        随机的生成PI向量，用于比较mig_obj_1 和 mig_obj_2的功能。

        随机次数n_random_veri

        :param mig_obj_1
        :param mig_obj_2
        :param n_random_veri:
        :return:
        '''

        assert isinstance(n_random_veri, int)
        assert isinstance(mig_obj_1, PMIG)
        assert isinstance(mig_obj_2, PMIG)
        assert n_random_veri >= 0

        simu_obj_current = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=mig_obj_1)
        simu_obj_last = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=mig_obj_2)
        # simu_obj_init = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=self.get_init_pmig())
        pi_len = simu_obj_current.get_pis_len()
        # assert pi_len == simu_obj_init.get_pis_len()
        assert pi_len == simu_obj_last.get_pis_len()

        for ii_random in range(0, n_random_veri):
            vec_max = pow(2, pi_len)
            vec_value = random.randint(0, vec_max)
            vec_bin = bin(vec_value)[2:]
            vec_tuple = tuple(str.zfill(vec_bin, pi_len))
            # print(len(vec_tuple), pi_len, latch_len)
            assert len(vec_tuple) == pi_len
            vec_pi_tuple = vec_tuple[:pi_len]
            pi_vec = []
            for i in vec_pi_tuple:
                if int(i) == 0:
                    pi_vec.append(pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_00)
                elif int(i) == 1:
                    pi_vec.append(pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_11)
                else:
                    assert False

            result_pos_value_simple_1, result_pos_value_1, pos_selected_1, pi_vec_1 = simu_obj_current.simu_pos_value(pi_vec=pi_vec, allow_node_with_fixed_value=False)
            result_pos_value_simple_2, result_pos_value_2, pos_selected_2, pi_vec_2 = simu_obj_last.simu_pos_value(pi_vec=pi_vec, allow_node_with_fixed_value=False)
            # result_pos_value_simple_3, result_pos_value_3, pos_selected_3, pi_vec_3 = simu_obj_init.simu_pos_value(pi_vec=pi_vec, allow_node_with_fixed_value=False)

            # print(result_pos_value_simple_1)
            # print(result_pos_value_simple_2)
            # print(result_pos_value_simple_3)

            if result_pos_value_simple_1 != result_pos_value_simple_2:
                print("Random Verification failed!")
                print(result_pos_value_simple_1)
                print(result_pos_value_simple_2)
                return False
            # if result_pos_value_simple_1 != result_pos_value_simple_3:
            #     return False

        # print("Random Verification x{} passed!".format(n_random_veri))
        return True


#######
    @staticmethod
    def op_reconvergence_driven_cut_computation_with_stop_list(pmig_obj_r, root_l, n, stop_list=[]):
        '''
        输入一个root_l（literal)，以及整数n，返回一个以root_l对应的node为root的n割集PMIG对象。
        使用reconvergence-driven cut computation算法。
        注意：stop_list应当包含一些node的literal（无属性），默认为空。
        该列表中的literal所对应的node在本方法中被视为类似于PI，即无扇入。
        该列表的意义是：避免列表中的node被作为一个cut的leaves与root之间的中间node。
        例如，某个node具有多个扇出，因此不希望它作为一个cut的中间node被优化掉，此时就可以借助stop_list。

        :param pmig_obj_r:
        :param root_l:
        :param n:
        :return:
        '''

        assert isinstance(pmig_obj_r, PMIG)

        # 迭代执行，尝试将nodeset_leaves中node的扇入来替换该node作为leaves。每次被替换的node都是非stop的并且具有最低cost的，并且替换必须不能使leaves数目超过限制。
        def construct_cut_rec(nodeset_leaves, nodeset_visited, size_limit, stop_list):
            def is_stop_node(l):
                if pmig_obj_r.is_pi(l):
                    return True
                if pmig_obj_r.is_const0(l):
                    return True
                if l in stop_list:
                    return True
                return False

            assert isinstance(nodeset_leaves, list)
            assert isinstance(nodeset_visited, list)
            assert PMIG.get_literal_const0() in nodeset_leaves

            if if_all_nodes_are_stop_nodes(leaves=nodeset_leaves, stop_list=stop_list):
                return nodeset_leaves, nodeset_visited

            min_cost = 10
            node_with_min_cost = None
            for n_i in (l_nodes for l_nodes in nodeset_leaves if not is_stop_node(l=l_nodes)):
                cost_i = leaf_cost(node_m=n_i, visited=nodeset_visited)
                if cost_i < min_cost:
                    min_cost = cost_i
                    node_with_min_cost = n_i
            assert (min_cost < 10) and (node_with_min_cost is not None)
            if (len(nodeset_leaves) + min_cost) > (size_limit + 1):  # size_limit+1是由于考虑到存在一个CONST0
                return nodeset_leaves, nodeset_visited

            for fanin_i in pmig_obj_r.get_maj_fanins(node_with_min_cost):
                if (PMIG.get_noattribute_literal(f=fanin_i)) not in nodeset_leaves:
                    nodeset_leaves.append(PMIG.get_noattribute_literal(f=fanin_i))
            assert node_with_min_cost in nodeset_leaves
            nodeset_leaves.remove(node_with_min_cost)
            assert node_with_min_cost not in nodeset_leaves

            for fanin_i in pmig_obj_r.get_maj_fanins(node_with_min_cost):
                if (PMIG.get_noattribute_literal(f=fanin_i)) not in nodeset_visited:
                    nodeset_visited.append(PMIG.get_noattribute_literal(f=fanin_i))

            return construct_cut_rec(nodeset_leaves=nodeset_leaves, nodeset_visited=nodeset_visited,
                                     size_limit=size_limit, stop_list=stop_list)

        # 用于检查leaves列表中的nodes是否全部都不可被扇入替代了。这作为迭代的终止条件之一。
        def if_all_nodes_are_stop_nodes(leaves, stop_list):
            def is_stop_node(l):
                if pmig_obj_r.is_pi(l):
                    return True
                if pmig_obj_r.is_const0(l):
                    return True
                if l in stop_list:
                    return True
                return False

            for l in leaves:
                if not is_stop_node(l):
                    return False
            return True

        # cost函数
        def leaf_cost(node_m, visited):
            cost = -1
            # print(node_m)
            for ch_l in pmig_obj_r.get_maj_fanins(node_m):
                if PMIG.get_noattribute_literal(ch_l) not in visited:
                    cost = cost + 1
            return cost

        # main
        nodeset_leaves = [root_l, PMIG.get_literal_const0()]
        nodeset_visited = [root_l, PMIG.get_literal_const0()]
        stop_list = tuple(stop_list)
        return construct_cut_rec(nodeset_leaves=nodeset_leaves, nodeset_visited=nodeset_visited, size_limit=n,
                                 stop_list=stop_list)


#######
    @staticmethod
    def op_number_of_fanouts(pmig_obj_r, target_l):
        '''
        输入一个node的literal， 返回这个node的扇出数目, 以及扇出到的node的literals列表。

        :param target_l:
        :return:
        '''
        assert isinstance(pmig_obj_r, PMIG)
        n_fanout = 0
        fanout_list = []
        target_id = target_l >> 2
        for node_l in pmig_obj_r.get_iter_nodes_all():
            if pmig_obj_r.is_maj(f=node_l):
                for ch_l in pmig_obj_r.get_maj_fanins(f=node_l):
                    ch_id = ch_l >> 2
                    if ch_id == target_id:
                        if node_l not in fanout_list:
                            n_fanout = n_fanout + 1
                            fanout_list.append(node_l)
            elif pmig_obj_r.is_latch(f=node_l):
                assert False
            else:
                assert (pmig_obj_r.is_pi(f=node_l) or pmig_obj_r.is_const0(f=node_l))
        return n_fanout, fanout_list

#######
    @staticmethod
    def op_get_all_nodes_with_multiple_fanouts(pmig_obj_r, limit_number=1):
        '''
        返回一个元组，包含扇出数目大于limit_number(默认为1)的MAJ node的literal及扇出到的literals。即元组的元素为 (符合条件的node的literal, [扇出目标的literal...])

        注意：这里的扇出数目指的是扇出目标nodes的数目，即若node B的两个扇入均为node A，那么node B也只会为为node A的扇出数目统计加1而不是加2。

        与op_get_all_nodes_with_multiple_fanouts_fast方法功能相同，但是本方法会更慢一些。

        :param limit_number:
        :return:
        '''
        assert isinstance(pmig_obj_r, PMIG)
        node_list = []
        for node_l in pmig_obj_r.get_iter_nodes_all():
            n, ls = PMIG_operator.op_number_of_fanouts(pmig_obj_r=pmig_obj_r, target_l=node_l)
            if (n > limit_number) and (pmig_obj_r.is_maj(f=node_l)):
                node_list.append((node_l, ls))
        node_tuple = tuple(copy.deepcopy(node_list))
        return node_tuple

#######
    @staticmethod
    def op_get_all_nodes_with_multiple_fanouts_fast(pmig_obj_r, limit_number=1):
        '''
        返回一个元组，包含扇出数目大于limit_number(默认为1)的MAJ node的literal及扇出到的literals。即元组的元素为 (符合条件的node的literal, [扇出目标的literal...])

        注意：这里的扇出数目指的是扇出目标nodes的数目，即若node B的两个扇入均为node A，那么node B也只会为为node A的扇出数目统计加1而不是加2。

        与op_get_all_nodes_with_multiple_fanouts方法功能相同，但是本方法会更快一些。

        :param limit_number:
        :return:
        '''
        assert isinstance(pmig_obj_r, PMIG)
        list_n_fanout_target = []  # 包含了每个node的扇出目标nodes的数目。索引对应node id，因此也包含了const0和pi，虽然没有用处
        list_fanout_targets = []  # 对应上面的列表，这个列表包含的元素为列表，列表中是扇出目标nodes的literal(noattr)，不重复

        for node_l in pmig_obj_r.get_iter_nodes_all():
            node_id = node_l >> 2
            assert len(list_n_fanout_target) == node_id
            list_n_fanout_target.append(0)
            list_fanout_targets.append([])
            if pmig_obj_r.is_maj(f=node_l):
                for ch_l in pmig_obj_r.get_maj_fanins(f=node_l):
                    ch_id = ch_l >> 2
                    if node_l not in list_fanout_targets[ch_id]:
                        list_fanout_targets[ch_id].append(node_l)
                        list_n_fanout_target[ch_id] = list_n_fanout_target[ch_id] + 1
            else:
                assert pmig_obj_r.is_const0(f=node_l) or pmig_obj_r.is_pi(f=node_l)

        assert pmig_obj_r.n_nodes() == len(list_n_fanout_target)
        assert pmig_obj_r.n_nodes() == len(list_fanout_targets)
        result_list = []
        for idx in range(0, pmig_obj_r.n_nodes()):
            if (list_n_fanout_target[idx] > limit_number) and (pmig_obj_r.is_maj(f=idx << 2)):
                idx_l = idx << 2
                idx_targets = list_fanout_targets[idx]
                assert len(idx_targets) == list_n_fanout_target[idx]
                result_list.append((idx_l, idx_targets))
        result_tuple = tuple(copy.deepcopy(result_list))
        return result_tuple


#######
    @staticmethod
    def op_reconvergence_driven_cut_computation_with_multifanout_checks(pmig_obj_r, root_l, n, multi_fanout_nodes_list):
        '''
        op_reconvergence_driven_cut_computation_with_stop_list的增强版！

        输入一个root_l（literal)，以及整数n，返回一个以root_l对应的node为root的n割集PMIG对象，并且割集的内部nodes不会扇出到不被割集包含的node。
        使用reconvergence-driven cut computation算法。
        注意：stop_list应当包含一些node的literal（无属性），默认为空。
        该列表中的literal所对应的node在本方法中被视为类似于PI，即无扇入。
        该列表的意义是：避免列表中的node被作为一个cut的leaves与root之间的中间node。
        例如，某个node具有多个扇出，因此不希望它作为一个cut的中间node被优化掉，此时就可以借助stop_list。

        :param pmig_obj_r:
        :param root_l:
        :param n:
        :param multi_fanout_nodes_list: 应当为op_get_all_nodes_with_multiple_fanouts_fast或op_get_all_nodes_with_multiple_fanouts的返回元组
        :return:
        '''
        # 此函数用于检查割集是否符合要求（即内部node的扇出均被node包含），若不符合要求，则给出需要扩充到stop list中的literal
        def check_inner_nodes(nodeset_leaves, nodeset_visited, nlist):
            if_satisfied = True # 当前割集是否已满足要求
            return_literals = [] # 需要扩充到stop list的nodes
            worst_literal = None # 具有最多数量的不被割集包含的扇出目标的node
            worst_n = 0
            # 获得leaves中最大的literal
            leaves_max = 0
            for leaves_i in nodeset_leaves:
                if leaves_i > leaves_max:
                    leaves_max = leaves_i
            # 若一个node的扇出不在visited中，并且literal大于最大的leaves literal， 那么应当加入stop_list
            # 同时，会记录worst node（即不在visited中的fanout的数目最多的node），作为备选。
            for mfn in nlist:
                n = 0
                mfn_l = mfn[0]
                mfn_llist = mfn[1]
                if ((mfn_l in nodeset_visited) and (mfn_l not in nodeset_leaves)):
                    for mfn_llist_i in mfn_llist:
                        if (mfn_llist_i not in nodeset_visited) or (mfn_llist_i in nodeset_leaves):
                            if_satisfied = False
                            n = n + 1
                            if ((mfn_llist_i > leaves_max) and (mfn_l not in return_literals)):
                                return_literals.append(mfn_l)
                if n > worst_n:
                    worst_literal = mfn_l
                    worst_n = n

            if (not if_satisfied) and (len(return_literals) == 0):
                return_literals.append(worst_literal)

            return if_satisfied, return_literals

        # main

        # 将不可包含的点加入stop_list，这些点至少有一个扇出到的node具有比root大的literal
        stop_list_current = []

        # 如果一个node存在一个扇出的node，其literal大于root node的literal，那么该node不能作为cut的内部node
        for mfn in multi_fanout_nodes_list:
            i = 0
            mfn_l = mfn[0]
            mfn_llist = mfn[1]
            for ll in mfn_llist:
                if ll > root_l:
                    i = i + 1
            if i > 0:
                stop_list_current.append(mfn_l)

        # 作为PO扇入的node不可被优化
        for ii_po_l in pmig_obj_r.get_iter_po_fanins():
            ii_po_l_noattr = PMIG.get_noattribute_literal(f=ii_po_l)
            if ii_po_l_noattr not in stop_list_current:
                stop_list_current.append(ii_po_l_noattr)


        if_satisfied = False
        while (not if_satisfied):
            nodeset_leaves, nodeset_visited = PMIG_operator.op_reconvergence_driven_cut_computation_with_stop_list(pmig_obj_r=pmig_obj_r,
                                                                                                          root_l=root_l,
                                                                                                          n=n,
                                                                                                          stop_list=stop_list_current)
            if_satisfied, additional_stop_nodes = check_inner_nodes(nodeset_leaves=nodeset_leaves,
                                                                    nodeset_visited=nodeset_visited,
                                                                    nlist=multi_fanout_nodes_list)
            for l_i in additional_stop_nodes:
                stop_list_current.append(l_i)

        return nodeset_leaves, nodeset_visited

#######
    class Cut_Mapping:
        '''
        这个类是为了存储n-cut与原图之间的nodes映射关系
        '''

        def __init__(self):
            self._nodes_mapping = {}  # 原图中的nodes literal（无属性）：cut图中的nodes literal（无属性）

        def add_nodes_mapping(self, l_old, l_new):
            # assert not PMIG.is_negated_literal(l_old)
            # assert not PMIG.is_polymorphic_literal(l_old)
            # assert not PMIG.is_negated_literal(l_new)
            # assert not PMIG.is_polymorphic_literal(l_new)
            assert PMIG.is_noattribute_literal(l_old)
            assert PMIG.is_noattribute_literal(l_new)
            assert l_old not in self._nodes_mapping
            self._nodes_mapping[l_old] = l_new

        def get_new_literal(self, l_old):
            # l_old_noattr = PMIG.get_positive_normal_literal(f=l_old)
            l_old_noattr = PMIG.get_noattribute_literal(f=l_old)
            assert l_old_noattr in self._nodes_mapping
            l_new_noattr = self._nodes_mapping[l_old_noattr]
            l_new = PMIG.add_attr_if_has_attr(f=l_new_noattr, c=l_old)
            return l_new
#######
    @staticmethod
    def op_get_n_cut_pmig_with_multifanout_checks(pmig_obj_r, root_l, n):
        '''
        获得以root_l(literal)为root的n-cut，并将获得的cut构建一个PMIG用于优化。该方法使用op_reconvergence_driven_cut_computation_with_multifanout_checks搜索割集。

        return copy.deepcopy(pmig_cut), cut_map_pi, cut_map_po, nodeset_leaves, nodeset_visited

        cut_map_pi 为字典，存储着生成的图的PI与cut leaves之间的对应关系，key为生成的PMIG的PI literal， value为cut的leaves literal

        cut_map_po 为元组：(cut_map.get_new_literal(root_l), root_l)

        nodeset_leaves, nodeset_visited 为割集的信息

        :param pmig_obj_r:
        :param root_l: INT - root node的literal
        :param n: INT - leaves数目上限
        :return:
        '''

        assert isinstance(pmig_obj_r, PMIG)
        multifanout_list = PMIG_operator.op_get_all_nodes_with_multiple_fanouts_fast(pmig_obj_r=pmig_obj_r)
        # print("*-*-*-*-*-*", multifanout_list)
        # Get n-cut
        nodeset_leaves, nodeset_visited = PMIG_operator.op_reconvergence_driven_cut_computation_with_multifanout_checks(pmig_obj_r=pmig_obj_r, root_l=root_l, n=n, multi_fanout_nodes_list=multifanout_list)
        nodeset_cone = pmig_obj_r.get_cone(roots=(root_l,), stop=nodeset_leaves)
        # print("#####", nodeset_visited)
        # print("#####", nodeset_leaves)
        # checks
        for i in nodeset_visited:
            assert (i in nodeset_leaves) or (i in nodeset_cone)
        for i in nodeset_cone:
            assert i in nodeset_visited
        for i in nodeset_leaves:
            assert i in nodeset_visited
        assert len(nodeset_leaves) + len(nodeset_cone) == len(nodeset_visited)

        # Create PMIG
        pmig_cut = PMIG(polymorphic_type=pmig_obj_r.attr_ptype_get())
        cut_map = PMIG_operator.Cut_Mapping()
        # PI
        for i in nodeset_leaves:
            if i == pmig_cut.get_literal_const0():
                cut_map.add_nodes_mapping(l_old=i, l_new=i)
            else:
                new_l = pmig_cut.create_pi()
                cut_map.add_nodes_mapping(l_old=i, l_new=new_l)
        # MAJ
        for i in nodeset_cone:
            assert pmig_obj_r.is_maj(f=i)
            ch0, ch1, ch2 = pmig_obj_r.get_maj_fanins(f=i)
            ch0_new = cut_map.get_new_literal(l_old=ch0)
            ch1_new = cut_map.get_new_literal(l_old=ch1)
            ch2_new = cut_map.get_new_literal(l_old=ch2)
            new_l = pmig_cut.create_maj(child0=ch0_new, child1=ch1_new, child2=ch2_new)
            cut_map.add_nodes_mapping(l_old=i, l_new=new_l)

        # PO
        pmig_cut.create_po(f=cut_map.get_new_literal(root_l))

        # Collect info
        cut_map_po = (cut_map.get_new_literal(root_l), root_l)
        cut_map_pi = {}
        for i in nodeset_leaves:
            key = cut_map.get_new_literal(l_old=i)
            cut_map_pi[key] = i

        # return
        return copy.deepcopy(pmig_cut), cut_map_pi, cut_map_po, nodeset_leaves, nodeset_visited



#######
    @staticmethod
    def op_get_n_cut_pmig_with_stop_list(pmig_obj_r, root_l, n, stop_list = []):
        '''
        获得以root_l(literal)为root的n-cut，并将获得的cut构建一个PMIG用于优化。该方法使用op_reconvergence_driven_cut_computation_with_stop_list搜索割集。

        return copy.deepcopy(pmig_cut), cut_map_pi, cut_map_po, nodeset_leaves, nodeset_visited

        cut_map_pi 为字典，存储着生成的图的PI与cut leaves之间的对应关系，key为生成的PMIG的PI literal， value为cut的leaves literal

        cut_map_po 为元组：(cut_map.get_new_literal(root_l), root_l)

        nodeset_leaves, nodeset_visited 为割集的信息

        :param pmig_obj_r:
        :param root_l: INT - root node的literal
        :param n: INT - leaves数目上限
        :return:
        '''

        assert isinstance(pmig_obj_r, PMIG)
        # multifanout_list = PMIG_operator.op_get_all_nodes_with_multiple_fanouts_fast(pmig_obj_r=pmig_obj_r)
        # print("*-*-*-*-*-*", multifanout_list)
        # Get n-cut
        nodeset_leaves, nodeset_visited = PMIG_operator.op_reconvergence_driven_cut_computation_with_stop_list(pmig_obj_r=pmig_obj_r, root_l=root_l, n=n, stop_list=stop_list)
        nodeset_cone = pmig_obj_r.get_cone(roots=(root_l,), stop=nodeset_leaves)
        # print("#####", nodeset_visited)
        # print("#####", nodeset_leaves)
        # checks
        for i in nodeset_visited:
            assert (i in nodeset_leaves) or (i in nodeset_cone)
        for i in nodeset_cone:
            assert i in nodeset_visited
        for i in nodeset_leaves:
            assert i in nodeset_visited
        assert len(nodeset_leaves) + len(nodeset_cone) == len(nodeset_visited)

        # Create PMIG
        pmig_cut = PMIG(polymorphic_type=pmig_obj_r.attr_ptype_get())
        cut_map = PMIG_operator.Cut_Mapping()
        # PI
        for i in nodeset_leaves:
            if i == pmig_cut.get_literal_const0():
                cut_map.add_nodes_mapping(l_old=i, l_new=i)
            else:
                new_l = pmig_cut.create_pi()
                cut_map.add_nodes_mapping(l_old=i, l_new=new_l)
        # MAJ
        for i in nodeset_cone:
            assert pmig_obj_r.is_maj(f=i)
            ch0, ch1, ch2 = pmig_obj_r.get_maj_fanins(f=i)
            ch0_new = cut_map.get_new_literal(l_old=ch0)
            ch1_new = cut_map.get_new_literal(l_old=ch1)
            ch2_new = cut_map.get_new_literal(l_old=ch2)
            new_l = pmig_cut.create_maj(child0=ch0_new, child1=ch1_new, child2=ch2_new)
            cut_map.add_nodes_mapping(l_old=i, l_new=new_l)

        # PO
        pmig_cut.create_po(f=cut_map.get_new_literal(root_l))

        # Collect info
        cut_map_po = (cut_map.get_new_literal(root_l), root_l)
        cut_map_pi = {}
        for i in nodeset_leaves:
            key = cut_map.get_new_literal(l_old=i)
            cut_map_pi[key] = i

        # return
        return copy.deepcopy(pmig_cut), cut_map_pi, cut_map_po, nodeset_leaves, nodeset_visited



    # @staticmethod
    # def op_cut_exact_synthesis_size(pmig_obj_r, root_l, n_leaves):
    #     '''
    #     在pmig_obj_r中，以literal为root_l的node为root，获得一个n_leaves割集，然后对该割集进行exact synthesis
    #
    #     return sat_flag, copy.deepcopy(new_pmig), copy.deepcopy(optimized_mig_obj), n_maj_compare, new_literal_of_root, info_tuple_cut, info_tuple_model
    #
    #     sat_flag: bool - 是否可优化
    #
    #     new_pmig: PMIG - 优化后的割集PMIG
    #
    #     optimized_mig_obj: PMIG - 对割集进行优化后的图
    #
    #     n_maj_compare: tuple - (优化前割集的MAJ数目, 优化后割集的MAJ数目)
    #
    #     new_literal_of_root: int - 割集root在新图中的literal（含属性）
    #
    #     info_tuple_cut:
    #
    #     info_tuple_model:
    #
    #     :param pmig_obj_r:
    #     :param root_l:
    #     :param n_leaves:
    #     :return:
    #     '''
    #     ####################################class
    #     class Map_for_ApplyOptiCut:
    #         '''
    #         用于将PMIG的cut替换为优化后的cut
    #         '''
    #         def __init__(self, deleted_literal, map_cut_pi):
    #             self._dict_literal_old_to_new = {PMIG.get_literal_const0():PMIG.get_literal_const0()}
    #             self._dict_literal_cut_to_old = copy.deepcopy(map_cut_pi)
    #             self._dict_literal_cut_to_new = {}
    #             self._deleted_literal = copy.deepcopy(deleted_literal)
    #
    #
    #
    #         def map_literal_old_to_new(self, l_old, l_new):
    #             assert PMIG.is_noattribute_literal(f=l_old)
    #             assert l_old not in self._dict_literal_old_to_new
    #             assert l_old not in self._deleted_literal
    #             self._dict_literal_old_to_new[l_old] = l_new
    #
    #         def get_new_literal_of_old(self, l_old):
    #             l_old_noattr = PMIG.get_noattribute_literal(f=l_old)
    #             assert l_old_noattr in self._dict_literal_old_to_new
    #             assert l_old_noattr not in self._deleted_literal
    #             l_new_noattr = self._dict_literal_old_to_new[l_old_noattr]
    #             l_new = PMIG.add_attr_if_has_attr(f=l_new_noattr, c=l_old)
    #             return l_new
    #
    #         def map_literal_cut_to_new(self, l_cut, l_new):
    #             assert PMIG.is_noattribute_literal(f=l_cut)
    #             assert l_cut not in self._dict_literal_cut_to_new
    #             self._dict_literal_cut_to_new[l_cut] = l_new
    #
    #         def get_new_literal_of_cut(self, l_cut):
    #             l_cut_noattr = PMIG.get_noattribute_literal(f=l_cut)
    #             if l_cut_noattr in self._dict_literal_cut_to_old:
    #                 l_old_noattr = self._dict_literal_cut_to_old[l_cut_noattr]
    #                 l_old = PMIG.add_attr_if_has_attr(f=l_old_noattr, c=l_cut)
    #                 return self.get_new_literal_of_old(l_old=l_old)
    #             else:
    #                 assert l_cut_noattr in self._dict_literal_cut_to_new
    #                 l_new_noattr = self._dict_literal_cut_to_new[l_cut_noattr]
    #                 l_new = PMIG.add_attr_if_has_attr(f=l_new_noattr, c=l_cut)
    #                 return l_new
    #
    #
    #     ####################################main
    #     assert isinstance(pmig_obj_r, PMIG)
    #
    #     # 获得cut
    #     cut_pmig_obj, cut_map_pi, cut_map_po, nodeset_leaves, nodeset_visited = PMIG_operator.op_get_n_cut_pmig_with_multifanout_checks(pmig_obj_r=copy.deepcopy(pmig_obj_r), root_l=root_l, n=n_leaves)
    #     assert isinstance(cut_pmig_obj, PMIG)
    #     # 若cut大小为0,则直接返回
    #     if cut_pmig_obj.n_majs() == 0:
    #         return False, None, None, None, None, None, None
    #
    #     # print("**********")
    #     # print(nodeset_leaves)
    #     # print(nodeset_visited)
    #     # 获得cut功能
    #     pmigsimu_obj = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=cut_pmig_obj)
    #     func1, func2, pflag = pmigsimu_obj.simu_for_exact_synthesis()
    #     # exact synthesis
    #     exsyn_obj = exact_synthesis.PMIG_Cut_ExactSynthesis(func1=func1, func2=func2, allow_polymorphic=pflag)
    #     sat_flag, model_nodes_list, model_po, new_pmig = exsyn_obj.search_minimum_mig(upper_limit_n=cut_pmig_obj.n_majs() - 1, echo_mode=False)
    #
    #     # 应用优化后的cut
    #     if sat_flag:
    #         # print
    #         # print("发现可优化的割集：root = {}, 原割集大小 = {}, 优化后的割集大小 = {}".format(root_l, cut_pmig_obj.n_majs(), new_pmig.n_majs()))
    #         n_maj_compare = (cut_pmig_obj.n_majs(), new_pmig.n_majs())
    #         # 功能验证
    #         new_pmigsimu_obj = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=copy.deepcopy(new_pmig))
    #         new_func1, new_func2, new_pflag = new_pmigsimu_obj.simu_for_exact_synthesis()
    #         # print(new_func1)
    #         # print(func1)
    #         assert new_func1 == func1
    #         assert new_func2 == func2
    #
    #         # 应用
    #         optimized_mig_obj = PMIG(name=pmig_obj_r.attr_get_pmig_name(), polymorphic_type=pmig_obj_r.attr_ptype_get())
    #         # 原图中可被直接删除的nodes，即割集中除去root和leaves以外的其它所有nodes。
    #         list_nodes_to_be_deleted = []
    #         for ii_l in nodeset_visited:
    #             if (ii_l not in nodeset_leaves) and (ii_l != root_l):
    #                 list_nodes_to_be_deleted.append(ii_l)
    #         # print(list_nodes_to_be_deleted,"***")
    #         # literal映射字典
    #         map_dict = Map_for_ApplyOptiCut(deleted_literal=list_nodes_to_be_deleted, map_cut_pi=cut_map_pi)
    #
    #         # cut po在原图中的literal，即root_l
    #         po_literal_old = cut_map_po[1]
    #
    #         # 开始映射
    #         for ii_l in pmig_obj_r.get_iter_nodes_all():
    #             if pmig_obj_r.has_name(f=ii_l):
    #                 newnode_name = pmig_obj_r.get_name_by_id(f=ii_l)
    #             else:
    #                 newnode_name = None
    #
    #             if pmig_obj_r.is_const0(f=ii_l):
    #                 assert ii_l == PMIG.get_literal_const0()
    #
    #             elif pmig_obj_r.is_pi(f=ii_l):
    #                 newnode_l = optimized_mig_obj.create_pi(name=newnode_name)
    #                 map_dict.map_literal_old_to_new(l_old=ii_l, l_new=newnode_l)
    #
    #             elif ii_l == po_literal_old:
    #                 for ii_cut_l in new_pmig.get_iter_nodes_all():
    #                     if new_pmig.is_maj(f=ii_cut_l):
    #                         ch0_l_cut = new_pmig.get_maj_child0(f=ii_cut_l)
    #                         ch1_l_cut = new_pmig.get_maj_child1(f=ii_cut_l)
    #                         ch2_l_cut = new_pmig.get_maj_child2(f=ii_cut_l)
    #
    #                         ch0_l_new = map_dict.get_new_literal_of_cut(l_cut=ch0_l_cut)
    #                         ch1_l_new = map_dict.get_new_literal_of_cut(l_cut=ch1_l_cut)
    #                         ch2_l_new = map_dict.get_new_literal_of_cut(l_cut=ch2_l_cut)
    #
    #                         newnode_l = optimized_mig_obj.create_maj(child0=ch0_l_new, child1=ch1_l_new, child2=ch2_l_new)
    #                         map_dict.map_literal_cut_to_new(l_cut=ii_cut_l, l_new=newnode_l)
    #                     else:
    #                         assert (new_pmig.is_const0(f=ii_cut_l)) or (new_pmig.is_pi(f=ii_cut_l))
    #
    #                 # assert ii_cut_l == cut_map_po[0]
    #                 assert ii_cut_l == PMIG.get_noattribute_literal( new_pmig.get_po_fanin(po=0) )
    #
    #                 newnode_l_withattr = newnode_l
    #                 if model_po[1]:
    #                     newnode_l_withattr = newnode_l_withattr + 1
    #                 if model_po[2]:
    #                     newnode_l_withattr = newnode_l_withattr + 2
    #
    #                 map_dict.map_literal_old_to_new(l_old=ii_l, l_new=newnode_l_withattr)
    #                 new_literal_of_root = newnode_l_withattr
    #
    #
    #
    #             elif pmig_obj_r.is_maj(f=ii_l):
    #                 if (ii_l not in list_nodes_to_be_deleted) and (ii_l != po_literal_old):
    #                     ch0_l_old = pmig_obj_r.get_maj_child0(f=ii_l)
    #                     ch1_l_old = pmig_obj_r.get_maj_child1(f=ii_l)
    #                     ch2_l_old = pmig_obj_r.get_maj_child2(f=ii_l)
    #
    #                     ch0_l_new = map_dict.get_new_literal_of_old(l_old=ch0_l_old)
    #                     # print(ch1_l_old)
    #                     ch1_l_new = map_dict.get_new_literal_of_old(l_old=ch1_l_old)
    #                     ch2_l_new = map_dict.get_new_literal_of_old(l_old=ch2_l_old)
    #
    #                     newnode_l = optimized_mig_obj.create_maj(child0=ch0_l_new, child1=ch1_l_new, child2=ch2_l_new)
    #                     map_dict.map_literal_old_to_new(l_old=ii_l, l_new=newnode_l)
    #                     if newnode_name != None:
    #                         optimized_mig_obj.set_name(f=newnode_l, name=newnode_name)
    #             else:
    #                 assert False
    #
    #         for ii_po_id, ii_po_fanin, ii_po_type in pmig_obj_r.get_iter_pos():
    #             # print(ii_po_fanin)
    #             # print(map_dict._dict_literal_old_to_new)
    #             new_po_fanin = map_dict.get_new_literal_of_old(l_old=ii_po_fanin)
    #             new_po_name = pmig_obj_r.get_name_by_po(po=ii_po_id)
    #             optimized_mig_obj.create_po(f=new_po_fanin, name = new_po_name, po_type=ii_po_type)
    #
    #
    #     else:
    #         new_pmig = None
    #         optimized_mig_obj = None
    #         n_maj_compare = 0
    #         new_literal_of_root = None
    #         info_tuple_cut = None
    #         info_tuple_model = None
    #
    #     info_tuple_model = ( copy.deepcopy(model_nodes_list), copy.deepcopy(model_po) )
    #     info_tuple_cut = ( copy.deepcopy(cut_map_pi), copy.deepcopy(cut_map_po), copy.deepcopy(nodeset_leaves), copy.deepcopy(nodeset_visited) )
    #     return sat_flag, copy.deepcopy(new_pmig), copy.deepcopy(optimized_mig_obj), n_maj_compare, new_literal_of_root, info_tuple_cut, info_tuple_model

    @staticmethod
    def op_cut_exact_synthesis_size(pmig_obj_r, root_l, n_leaves, cut_computation_method, if_allow_0contribution):
        '''
        修改于2021.11.10。修改：1. 允许指定割集搜索方式; 2. 由“判断割集PMIG是否有优化 -> 替换到原图”更改为“替换到原图 -> 判断替换后整个PMIG是否有优化”

        cut_computation: rec_driven(recovergence driven cut computation), rec_driven_mfc(recovergence driven cut computation with multi-fanout-checks)

        在pmig_obj_r中，以literal为root_l的node为root，获得一个n_leaves割集，然后对该割集进行exact synthesis

        return sat_flag, copy.deepcopy(new_pmig), copy.deepcopy(optimized_mig_obj), n_maj_compare, new_literal_of_root, info_tuple_cut, info_tuple_model

        sat_flag: bool - 是否可优化

        optimized_mig_obj: PMIG - 对割集进行优化后的图

        n_maj_compare: tuple - (优化前的MAJ数目, 优化后的MAJ数目)


        :param pmig_obj_r:
        :param root_l:
        :param n_leaves:
        :return:
        '''

        assert cut_computation_method in ('rec_driven', 'rec_driven_mfc')
        assert if_allow_0contribution in (True, False)
        optimized_mig_obj_clean = None
        n_maj_compare = 0

        ####################################class
        class Map_for_ApplyOptiCut:
            '''
            用于将PMIG的cut替换为优化后的cut
            '''

            def __init__(self, deleted_literal, map_cut_pi):
                self._dict_literal_old_to_new = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
                self._dict_literal_cut_to_old = copy.deepcopy(map_cut_pi)
                self._dict_literal_cut_to_new = {}
                self._deleted_literal = copy.deepcopy(deleted_literal)

            def map_literal_old_to_new(self, l_old, l_new):
                assert PMIG.is_noattribute_literal(f=l_old)
                assert l_old not in self._dict_literal_old_to_new
                assert l_old not in self._deleted_literal
                self._dict_literal_old_to_new[l_old] = l_new

            def get_new_literal_of_old(self, l_old):
                l_old_noattr = PMIG.get_noattribute_literal(f=l_old)
                assert l_old_noattr in self._dict_literal_old_to_new
                assert l_old_noattr not in self._deleted_literal
                l_new_noattr = self._dict_literal_old_to_new[l_old_noattr]
                l_new = PMIG.add_attr_if_has_attr(f=l_new_noattr, c=l_old)
                return l_new

            def map_literal_cut_to_new(self, l_cut, l_new):
                assert PMIG.is_noattribute_literal(f=l_cut)
                assert l_cut not in self._dict_literal_cut_to_new
                self._dict_literal_cut_to_new[l_cut] = l_new

            def get_new_literal_of_cut(self, l_cut):
                l_cut_noattr = PMIG.get_noattribute_literal(f=l_cut)
                if l_cut_noattr in self._dict_literal_cut_to_old:
                    l_old_noattr = self._dict_literal_cut_to_old[l_cut_noattr]
                    l_old = PMIG.add_attr_if_has_attr(f=l_old_noattr, c=l_cut)
                    return self.get_new_literal_of_old(l_old=l_old)
                else:
                    assert l_cut_noattr in self._dict_literal_cut_to_new
                    l_new_noattr = self._dict_literal_cut_to_new[l_cut_noattr]
                    l_new = PMIG.add_attr_if_has_attr(f=l_new_noattr, c=l_cut)
                    return l_new

        ####################################main
        assert isinstance(pmig_obj_r, PMIG)

        # 获得cut
        if cut_computation_method == 'rec_driven_mfc':
            cut_pmig_obj, cut_map_pi, cut_map_po, nodeset_leaves, nodeset_visited = PMIG_operator.op_get_n_cut_pmig_with_multifanout_checks(pmig_obj_r=copy.deepcopy(pmig_obj_r), root_l=root_l, n=n_leaves)
        elif cut_computation_method == 'rec_driven':
            cut_pmig_obj, cut_map_pi, cut_map_po, nodeset_leaves, nodeset_visited = PMIG_operator.op_get_n_cut_pmig_with_stop_list(pmig_obj_r=copy.deepcopy(pmig_obj_r), root_l=root_l, n=n_leaves)
        else:
            assert False
        assert isinstance(cut_pmig_obj, PMIG)
        # 若cut大小为0,则直接返回
        if cut_pmig_obj.n_majs() == 0:
            return False, None, None, None, None, None, None

        # print("**********")
        # print(nodeset_leaves)
        # print(nodeset_visited)
        # 获得cut功能
        pmigsimu_obj = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=cut_pmig_obj)
        func1, func2, pflag = pmigsimu_obj.simu_for_exact_synthesis()
        # exact synthesis
        exsyn_obj = exact_synthesis.PMIG_Cut_ExactSynthesis(func1=func1, func2=func2, allow_polymorphic=pflag)

        if if_allow_0contribution:
            sat_flag, model_nodes_list, model_po, new_pmig = exsyn_obj.search_minimum_mig(upper_limit_n=cut_pmig_obj.n_majs(), echo_mode=False)
        else:
            sat_flag, model_nodes_list, model_po, new_pmig = exsyn_obj.search_minimum_mig(upper_limit_n=cut_pmig_obj.n_majs() - 1, echo_mode=False)


        # 应用优化后的cut
        if sat_flag:
        # if True:
            # print
            # print("发现可优化的割集：root = {}, 原割集大小 = {}, 优化后的割集大小 = {}".format(root_l, cut_pmig_obj.n_majs(), new_pmig.n_majs()))
            # n_maj_compare = (cut_pmig_obj.n_majs(), new_pmig.n_majs())
            # 功能验证
            new_pmigsimu_obj = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=copy.deepcopy(new_pmig))
            new_func1, new_func2, new_pflag = new_pmigsimu_obj.simu_for_exact_synthesis()
            # print(new_func1)
            # print(func1)
            assert new_func1 == func1
            assert new_func2 == func2

            # 应用
            optimized_mig_obj = PMIG(name=pmig_obj_r.attr_get_pmig_name(), polymorphic_type=pmig_obj_r.attr_ptype_get())
            # 原图中可被直接删除的nodes，即割集中除去root和leaves以外的其它所有nodes。
            # list_nodes_to_be_deleted = []
            # for ii_l in nodeset_visited:
            #     if (ii_l not in nodeset_leaves) and (ii_l != root_l):
            #         list_nodes_to_be_deleted.append(ii_l)
            # print(list_nodes_to_be_deleted,"***")
            # literal映射字典
            map_dict = Map_for_ApplyOptiCut(deleted_literal=[], map_cut_pi=cut_map_pi)

            # cut po在原图中的literal，即root_l
            po_literal_old = cut_map_po[1]

            # 开始映射
            for ii_l in pmig_obj_r.get_iter_nodes_all():
                if pmig_obj_r.has_name(f=ii_l):
                    newnode_name = pmig_obj_r.get_name_by_id(f=ii_l)
                else:
                    newnode_name = None

                if pmig_obj_r.is_const0(f=ii_l):
                    assert ii_l == PMIG.get_literal_const0()

                elif pmig_obj_r.is_pi(f=ii_l):
                    newnode_l = optimized_mig_obj.create_pi(name=newnode_name)
                    map_dict.map_literal_old_to_new(l_old=ii_l, l_new=newnode_l)

                elif ii_l == po_literal_old:
                    for ii_cut_l in new_pmig.get_iter_nodes_all():
                        if new_pmig.is_maj(f=ii_cut_l):
                            ch0_l_cut = new_pmig.get_maj_child0(f=ii_cut_l)
                            ch1_l_cut = new_pmig.get_maj_child1(f=ii_cut_l)
                            ch2_l_cut = new_pmig.get_maj_child2(f=ii_cut_l)

                            ch0_l_new = map_dict.get_new_literal_of_cut(l_cut=ch0_l_cut)
                            ch1_l_new = map_dict.get_new_literal_of_cut(l_cut=ch1_l_cut)
                            ch2_l_new = map_dict.get_new_literal_of_cut(l_cut=ch2_l_cut)

                            newnode_l = optimized_mig_obj.create_maj(child0=ch0_l_new, child1=ch1_l_new, child2=ch2_l_new)
                            map_dict.map_literal_cut_to_new(l_cut=ii_cut_l, l_new=newnode_l)
                        else:
                            assert (new_pmig.is_const0(f=ii_cut_l)) or (new_pmig.is_pi(f=ii_cut_l))

                    # assert ii_cut_l == cut_map_po[0]
                    # if ii_cut_l != PMIG.get_noattribute_literal(new_pmig.get_po_fanin(po=0)):
                    #     print(new_pmig)
                    #     print(ii_cut_l)
                    #     print(new_pmig.get_po_fanin(po=0))
                    assert ( ii_cut_l == PMIG.get_noattribute_literal(new_pmig.get_po_fanin(po=0)) ) or (new_pmig.n_majs() == 0)

                    if new_pmig.n_majs() == 0:
                        newnode_l_withattr = cut_map_pi[model_po[0] << 2]
                        print("发现可消除的割集，root_l={}".format(root_l))
                    else:
                        newnode_l_withattr = newnode_l
                    if model_po[1]:
                        newnode_l_withattr = PMIG.negate_literal_if(f=newnode_l_withattr, c=True)
                        # newnode_l_withattr = newnode_l_withattr + 1
                    if model_po[2]:
                        newnode_l_withattr = PMIG.polymorphic_literal_if(f=newnode_l_withattr, c=True)
                        # newnode_l_withattr = newnode_l_withattr + 2

                    map_dict.map_literal_old_to_new(l_old=ii_l, l_new=newnode_l_withattr)
                    new_literal_of_root = newnode_l_withattr



                elif pmig_obj_r.is_maj(f=ii_l):
                    # if (ii_l not in list_nodes_to_be_deleted) and (ii_l != po_literal_old):
                    if ii_l != po_literal_old:
                        ch0_l_old = pmig_obj_r.get_maj_child0(f=ii_l)
                        ch1_l_old = pmig_obj_r.get_maj_child1(f=ii_l)
                        ch2_l_old = pmig_obj_r.get_maj_child2(f=ii_l)

                        ch0_l_new = map_dict.get_new_literal_of_old(l_old=ch0_l_old)
                        # print(ch1_l_old)
                        ch1_l_new = map_dict.get_new_literal_of_old(l_old=ch1_l_old)
                        ch2_l_new = map_dict.get_new_literal_of_old(l_old=ch2_l_old)

                        newnode_l = optimized_mig_obj.create_maj(child0=ch0_l_new, child1=ch1_l_new, child2=ch2_l_new)
                        map_dict.map_literal_old_to_new(l_old=ii_l, l_new=newnode_l)
                        if newnode_name != None:
                            optimized_mig_obj.set_name(f=newnode_l, name=newnode_name)
                else:
                    assert False

            for ii_po_id, ii_po_fanin, ii_po_type in pmig_obj_r.get_iter_pos():
                # print(ii_po_fanin)
                # print(map_dict._dict_literal_old_to_new)
                new_po_fanin = map_dict.get_new_literal_of_old(l_old=ii_po_fanin)
                new_po_name = pmig_obj_r.get_name_by_po(po=ii_po_id)
                optimized_mig_obj.create_po(f=new_po_fanin, name=new_po_name, po_type=ii_po_type)

            # assert PMIG_operator._function_verification_random(mig_obj_1=copy.deepcopy(pmig_obj_r), mig_obj_2=copy.deepcopy(optimized_mig_obj), n_random_veri=10)
            optimized_mig_obj_clean = optimized_mig_obj.pmig_clean_irrelevant_nodes()
            n_maj_compare = (pmig_obj_r.n_majs(), optimized_mig_obj_clean.n_majs())

            # 注意：下面这条断言用于debug，不需要时可删除，以加快速度。
            assert PMIG_operator._function_verification_random(mig_obj_1=copy.deepcopy(pmig_obj_r), mig_obj_2=copy.deepcopy(optimized_mig_obj_clean),n_random_veri=10)
            # print('pass')

        # info_tuple_model = (copy.deepcopy(model_nodes_list), copy.deepcopy(model_po))
        # info_tuple_cut = (copy.deepcopy(cut_map_pi), copy.deepcopy(cut_map_po), copy.deepcopy(nodeset_leaves),copy.deepcopy(nodeset_visited))


            if ( ( optimized_mig_obj_clean.n_majs() > pmig_obj_r.n_majs() ) and if_allow_0contribution ) or ( ( optimized_mig_obj_clean.n_majs() >= pmig_obj_r.n_majs() ) and (not if_allow_0contribution) ):
                sat_flag = False
                optimized_mig_obj_clean = None
                n_maj_compare = 0


        return sat_flag, copy.deepcopy(optimized_mig_obj_clean), n_maj_compare





    # @staticmethod
    # def op_cut_exact_synthesis_size_allow_0contribution(pmig_obj_r, root_l, n_leaves):
    #     '''
    #     与op_cut_exact_synthesis_size不同的是，该方法将允许0优化的替换。
    #
    #     在pmig_obj_r中，以literal为root_l的node为root，获得一个n_leaves割集，然后对该割集进行exact synthesis
    #
    #     return sat_flag, copy.deepcopy(new_pmig), copy.deepcopy(optimized_mig_obj), n_maj_compare, new_literal_of_root, info_tuple_cut, info_tuple_model
    #
    #     sat_flag: bool - 是否可优化
    #
    #     new_pmig: PMIG - 优化后的割集PMIG
    #
    #     optimized_mig_obj: PMIG - 对割集进行优化后的图
    #
    #     n_maj_compare: tuple - (优化前割集的MAJ数目, 优化后割集的MAJ数目)
    #
    #     new_literal_of_root: int - 割集root在新图中的literal（含属性）
    #
    #     info_tuple_cut:
    #
    #     info_tuple_model:
    #
    #     :param pmig_obj_r:
    #     :param root_l:
    #     :param n_leaves:
    #     :return:
    #     '''
    #
    #     ####################################class
    #     class Map_for_ApplyOptiCut:
    #         '''
    #         用于将PMIG的cut替换为优化后的cut
    #         '''
    #
    #         def __init__(self, deleted_literal, map_cut_pi):
    #             self._dict_literal_old_to_new = {PMIG.get_literal_const0(): PMIG.get_literal_const0()}
    #             self._dict_literal_cut_to_old = copy.deepcopy(map_cut_pi)
    #             self._dict_literal_cut_to_new = {}
    #             self._deleted_literal = copy.deepcopy(deleted_literal)
    #
    #         def map_literal_old_to_new(self, l_old, l_new):
    #             assert PMIG.is_noattribute_literal(f=l_old)
    #             assert l_old not in self._dict_literal_old_to_new
    #             assert l_old not in self._deleted_literal
    #             self._dict_literal_old_to_new[l_old] = l_new
    #
    #         def get_new_literal_of_old(self, l_old):
    #             l_old_noattr = PMIG.get_noattribute_literal(f=l_old)
    #             assert l_old_noattr in self._dict_literal_old_to_new
    #             assert l_old_noattr not in self._deleted_literal
    #             l_new_noattr = self._dict_literal_old_to_new[l_old_noattr]
    #             l_new = PMIG.add_attr_if_has_attr(f=l_new_noattr, c=l_old)
    #             return l_new
    #
    #         def map_literal_cut_to_new(self, l_cut, l_new):
    #             assert PMIG.is_noattribute_literal(f=l_cut)
    #             assert l_cut not in self._dict_literal_cut_to_new
    #             self._dict_literal_cut_to_new[l_cut] = l_new
    #
    #         def get_new_literal_of_cut(self, l_cut):
    #             l_cut_noattr = PMIG.get_noattribute_literal(f=l_cut)
    #             if l_cut_noattr in self._dict_literal_cut_to_old:
    #                 l_old_noattr = self._dict_literal_cut_to_old[l_cut_noattr]
    #                 l_old = PMIG.add_attr_if_has_attr(f=l_old_noattr, c=l_cut)
    #                 return self.get_new_literal_of_old(l_old=l_old)
    #             else:
    #                 assert l_cut_noattr in self._dict_literal_cut_to_new
    #                 l_new_noattr = self._dict_literal_cut_to_new[l_cut_noattr]
    #                 l_new = PMIG.add_attr_if_has_attr(f=l_new_noattr, c=l_cut)
    #                 return l_new
    #
    #     ####################################main
    #     assert isinstance(pmig_obj_r, PMIG)
    #
    #     # 获得cut
    #     cut_pmig_obj, cut_map_pi, cut_map_po, nodeset_leaves, nodeset_visited = PMIG_operator.op_get_n_cut_pmig_with_multifanout_checks(
    #         pmig_obj_r=copy.deepcopy(pmig_obj_r), root_l=root_l, n=n_leaves)
    #     assert isinstance(cut_pmig_obj, PMIG)
    #     # 若cut大小为0,则直接返回
    #     if cut_pmig_obj.n_majs() == 0:
    #         return False, None, None, None, None, None, None
    #
    #     # print("**********")
    #     # print(nodeset_leaves)
    #     # print(nodeset_visited)
    #     # 获得cut功能
    #     pmigsimu_obj = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=cut_pmig_obj)
    #     func1, func2, pflag = pmigsimu_obj.simu_for_exact_synthesis()
    #     # exact synthesis
    #     exsyn_obj = exact_synthesis.PMIG_Cut_ExactSynthesis(func1=func1, func2=func2, allow_polymorphic=pflag)
    #     sat_flag, model_nodes_list, model_po, new_pmig = exsyn_obj.search_minimum_mig(
    #         upper_limit_n=cut_pmig_obj.n_majs(), echo_mode=False)
    #
    #     # 应用优化后的cut
    #     if sat_flag:
    #         # print
    #         # print("发现可优化的割集：root = {}, 原割集大小 = {}, 优化后的割集大小 = {}".format(root_l, cut_pmig_obj.n_majs(), new_pmig.n_majs()))
    #         n_maj_compare = (cut_pmig_obj.n_majs(), new_pmig.n_majs())
    #         # 功能验证
    #         new_pmigsimu_obj = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=copy.deepcopy(new_pmig))
    #         new_func1, new_func2, new_pflag = new_pmigsimu_obj.simu_for_exact_synthesis()
    #         # print(new_func1)
    #         # print(func1)
    #         assert new_func1 == func1
    #         assert new_func2 == func2
    #
    #         # 应用
    #         optimized_mig_obj = PMIG(name=pmig_obj_r.attr_get_pmig_name(), polymorphic_type=pmig_obj_r.attr_ptype_get())
    #         # 原图中可被直接删除的nodes，即割集中除去root和leaves以外的其它所有nodes。
    #         list_nodes_to_be_deleted = []
    #         for ii_l in nodeset_visited:
    #             if (ii_l not in nodeset_leaves) and (ii_l != root_l):
    #                 list_nodes_to_be_deleted.append(ii_l)
    #         # print(list_nodes_to_be_deleted,"***")
    #         # literal映射字典
    #         map_dict = Map_for_ApplyOptiCut(deleted_literal=list_nodes_to_be_deleted, map_cut_pi=cut_map_pi)
    #
    #         # cut po在原图中的literal，即root_l
    #         po_literal_old = cut_map_po[1]
    #
    #         # 开始映射
    #         for ii_l in pmig_obj_r.get_iter_nodes_all():
    #             if pmig_obj_r.has_name(f=ii_l):
    #                 newnode_name = pmig_obj_r.get_name_by_id(f=ii_l)
    #             else:
    #                 newnode_name = None
    #
    #             if pmig_obj_r.is_const0(f=ii_l):
    #                 assert ii_l == PMIG.get_literal_const0()
    #
    #             elif pmig_obj_r.is_pi(f=ii_l):
    #                 newnode_l = optimized_mig_obj.create_pi(name=newnode_name)
    #                 map_dict.map_literal_old_to_new(l_old=ii_l, l_new=newnode_l)
    #
    #             elif ii_l == po_literal_old:
    #                 for ii_cut_l in new_pmig.get_iter_nodes_all():
    #                     if new_pmig.is_maj(f=ii_cut_l):
    #                         ch0_l_cut = new_pmig.get_maj_child0(f=ii_cut_l)
    #                         ch1_l_cut = new_pmig.get_maj_child1(f=ii_cut_l)
    #                         ch2_l_cut = new_pmig.get_maj_child2(f=ii_cut_l)
    #
    #                         ch0_l_new = map_dict.get_new_literal_of_cut(l_cut=ch0_l_cut)
    #                         ch1_l_new = map_dict.get_new_literal_of_cut(l_cut=ch1_l_cut)
    #                         ch2_l_new = map_dict.get_new_literal_of_cut(l_cut=ch2_l_cut)
    #
    #                         newnode_l = optimized_mig_obj.create_maj(child0=ch0_l_new, child1=ch1_l_new, child2=ch2_l_new)
    #                         map_dict.map_literal_cut_to_new(l_cut=ii_cut_l, l_new=newnode_l)
    #                     else:
    #                         assert (new_pmig.is_const0(f=ii_cut_l)) or (new_pmig.is_pi(f=ii_cut_l))
    #
    #                 # assert ii_cut_l == cut_map_po[0]
    #                 assert ii_cut_l == PMIG.get_noattribute_literal(new_pmig.get_po_fanin(po=0))
    #
    #                 newnode_l_withattr = newnode_l
    #                 if model_po[1]:
    #                     newnode_l_withattr = newnode_l_withattr + 1
    #                 if model_po[2]:
    #                     newnode_l_withattr = newnode_l_withattr + 2
    #
    #                 map_dict.map_literal_old_to_new(l_old=ii_l, l_new=newnode_l_withattr)
    #                 new_literal_of_root = newnode_l_withattr
    #
    #
    #
    #             elif pmig_obj_r.is_maj(f=ii_l):
    #                 if (ii_l not in list_nodes_to_be_deleted) and (ii_l != po_literal_old):
    #                     ch0_l_old = pmig_obj_r.get_maj_child0(f=ii_l)
    #                     ch1_l_old = pmig_obj_r.get_maj_child1(f=ii_l)
    #                     ch2_l_old = pmig_obj_r.get_maj_child2(f=ii_l)
    #
    #                     ch0_l_new = map_dict.get_new_literal_of_old(l_old=ch0_l_old)
    #                     # print(ch1_l_old)
    #                     ch1_l_new = map_dict.get_new_literal_of_old(l_old=ch1_l_old)
    #                     ch2_l_new = map_dict.get_new_literal_of_old(l_old=ch2_l_old)
    #
    #                     newnode_l = optimized_mig_obj.create_maj(child0=ch0_l_new, child1=ch1_l_new, child2=ch2_l_new)
    #                     map_dict.map_literal_old_to_new(l_old=ii_l, l_new=newnode_l)
    #                     if newnode_name != None:
    #                         optimized_mig_obj.set_name(f=newnode_l, name=newnode_name)
    #             else:
    #                 assert False
    #
    #         for ii_po_id, ii_po_fanin, ii_po_type in pmig_obj_r.get_iter_pos():
    #             # print(ii_po_fanin)
    #             # print(map_dict._dict_literal_old_to_new)
    #             new_po_fanin = map_dict.get_new_literal_of_old(l_old=ii_po_fanin)
    #             new_po_name = pmig_obj_r.get_name_by_po(po=ii_po_id)
    #             optimized_mig_obj.create_po(f=new_po_fanin, name=new_po_name, po_type=ii_po_type)
    #
    #
    #     else:
    #         new_pmig = None
    #         optimized_mig_obj = None
    #         n_maj_compare = 0
    #         new_literal_of_root = None
    #         info_tuple_cut = None
    #         info_tuple_model = None
    #
    #     info_tuple_model = (copy.deepcopy(model_nodes_list), copy.deepcopy(model_po))
    #     info_tuple_cut = (
    #     copy.deepcopy(cut_map_pi), copy.deepcopy(cut_map_po), copy.deepcopy(nodeset_leaves), copy.deepcopy(nodeset_visited))
    #     return sat_flag, copy.deepcopy(new_pmig), copy.deepcopy(
    #         optimized_mig_obj), n_maj_compare, new_literal_of_root, info_tuple_cut, info_tuple_model


########################################################################################################################
# class PMIG_optimization
#
# @Time    : 2021/10
# @Author  : c
#
# 对PMIG进行优化。
#
# 初始的PMIG：self._pmig_init不应当被修改，改动后的PMIG放在self._pmig_current中。
# 此外，可在self._pmig_savepoint_dict字典中存档。
#
# todo：可以增加一个随机的功能验证，在每次优化后，都将一两个随机的输入向量送入优化前后的图，观察输出是否一致。说不定可以发现错误。
#
#
########################################################################################################################
class PMIG_optimization:
    def __init__(self):
        self._pmig_init = None # 初始的PMIG，它不应当被修改
        self._ptype = None # PMIG的多态类型
        self._pmig_current = None # 当前的PMIG
        self._pmig_last = None  # 前一个PMIG
        self._pmig_savepoint_dict = {} # 字典，用于存档PMIG，key为存档名称,value为PMIG类型对象
        self._n_random_veri_default = None

    def initialization(self, mig_obj, n_random_veri = 10):
        '''
        初始化

        n_random_veri指定默认的随机功能验证次数

        :param mig_obj:
        :param n_random_veri:
        :return:
        '''
        assert isinstance(mig_obj, PMIG)
        self._pmig_init = copy.deepcopy(mig_obj)
        self._ptype = self._pmig_init.attr_ptype_get()
        self._pmig_current = copy.deepcopy(mig_obj)
        self._pmig_last = copy.deepcopy(mig_obj)
        self._pmig_savepoint_dict = {}
        assert isinstance(n_random_veri, int)
        assert n_random_veri >= 0
        self._n_random_veri_default = n_random_veri

#######
    def _function_verification_random(self, n_random_veri = None):
        '''
        随机的生成PI向量，用于比较当前的current pmig 和 last pmig的功能。

        随机次数可以指定，也可以使用默认值（initialization()方法指定）。

        :param n_random_veri:
        :return:
        '''
        if n_random_veri == None:
            n_random_veri = self._n_random_veri_default
        assert isinstance(n_random_veri, int)
        assert n_random_veri >= 0

        simu_obj_current = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=self.get_current_pmig())
        simu_obj_last = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=self.get_last_pmig())
        # simu_obj_init = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=self.get_init_pmig())
        pi_len = simu_obj_current.get_pis_len()
        # assert pi_len == simu_obj_init.get_pis_len()
        assert pi_len == simu_obj_last.get_pis_len()

        for ii_random in range(0, n_random_veri):
            vec_max = pow(2, pi_len)
            vec_value = random.randint(0, vec_max)
            vec_bin = bin(vec_value)[2:]
            vec_tuple = tuple(str.zfill(vec_bin, pi_len))
            # print(len(vec_tuple), pi_len, latch_len)
            assert len(vec_tuple) == pi_len
            vec_pi_tuple = vec_tuple[:pi_len]
            pi_vec = []
            for i in vec_pi_tuple:
                if int(i) == 0:
                    pi_vec.append(pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_00)
                elif int(i) == 1:
                    pi_vec.append(pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_11)
                else:
                    assert False

            result_pos_value_simple_1, result_pos_value_1, pos_selected_1, pi_vec_1 = simu_obj_current.simu_pos_value(pi_vec=pi_vec, allow_node_with_fixed_value=False)
            result_pos_value_simple_2, result_pos_value_2, pos_selected_2, pi_vec_2 = simu_obj_last.simu_pos_value(pi_vec=pi_vec, allow_node_with_fixed_value=False)
            # result_pos_value_simple_3, result_pos_value_3, pos_selected_3, pi_vec_3 = simu_obj_init.simu_pos_value(pi_vec=pi_vec, allow_node_with_fixed_value=False)

            # print(result_pos_value_simple_1)
            # print(result_pos_value_simple_2)
            # print(result_pos_value_simple_3)

            if result_pos_value_simple_1 != result_pos_value_simple_2:
                print("Random Verification failed!")
                print(result_pos_value_simple_1)
                print(result_pos_value_simple_2)
                return False
            # if result_pos_value_simple_1 != result_pos_value_simple_3:
            #     return False

        print("Random Verification x{} passed!".format(n_random_veri))
        return True

#######
    def _function_verification_random_for_delete_obsoleted_pos(self, n_random_veri = None):
        '''
        随机的生成PI向量，用于在清除OBSOLETE POs后比较current pmig 和 此前的last pmig的功能。

        随机次数可以指定，也可以使用默认值（initialization()方法指定）。

        :param n_random_veri:
        :return:
        '''
        if n_random_veri == None:
            n_random_veri = self._n_random_veri_default
        assert isinstance(n_random_veri, int)
        assert n_random_veri >= 0

        simu_obj_current = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=self.get_current_pmig())
        simu_obj_last = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=self.get_last_pmig())
        # simu_obj_init = pmig_logic.PMIG_LogicSimu_Comb(pmig_obj_r=self.get_init_pmig())
        pi_len = simu_obj_current.get_pis_len()
        # assert pi_len == simu_obj_init.get_pis_len()
        assert pi_len == simu_obj_last.get_pis_len()

        pos_last_without_obsolete_pos = []
        for ii_last_po_id, ii_last_po_fanin, ii_last_po_type in self.get_last_pmig().get_iter_pos_except_specified_type(i_type=PMIG.PO_OBSOLETE):
            ii_last_po_name = self.get_last_pmig().get_name_by_po_if_has(ii_last_po_id)
            pos_last_without_obsolete_pos.append((ii_last_po_fanin, ii_last_po_type, (ii_last_po_id, ii_last_po_name)))

        for ii_random in range(0, n_random_veri):
            vec_max = pow(2, pi_len)
            vec_value = random.randint(0, vec_max)
            vec_bin = bin(vec_value)[2:]
            vec_tuple = tuple(str.zfill(vec_bin, pi_len))
            # print(len(vec_tuple), pi_len, latch_len)
            assert len(vec_tuple) == pi_len
            vec_pi_tuple = vec_tuple[:pi_len]
            pi_vec = []
            for i in vec_pi_tuple:
                if int(i) == 0:
                    pi_vec.append(pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_00)
                elif int(i) == 1:
                    pi_vec.append(pmig_logic.PMIG_LogicSimu_Comb.LVALUE_V_11)
                else:
                    assert False

            # print(list(self.get_last_pmig().get_iter_pos()))
            # print(list(self.get_last_pmig().get_iter_pos_except_specified_type(i_type=PMIG.PO_OBSOLETE)))
            # print(list(self.get_current_pmig().get_iter_pos()))

            result_pos_value_simple_1, result_pos_value_1, pos_selected_1, pi_vec_1 = simu_obj_current.simu_pos_value(pi_vec=pi_vec, allow_node_with_fixed_value=False)
            result_pos_value_simple_2, result_pos_value_2, pos_selected_2, pi_vec_2 = simu_obj_last.simu_pos_value(pi_vec=pi_vec, pos_selected=pos_last_without_obsolete_pos, allow_node_with_fixed_value=False)
            # result_pos_value_simple_3, result_pos_value_3, pos_selected_3, pi_vec_3 = simu_obj_init.simu_pos_value(pi_vec=pi_vec, allow_node_with_fixed_value=False)

            # print(result_pos_value_simple_1)
            # print(result_pos_value_simple_2)
            # print(result_pos_value_simple_3)

            if result_pos_value_simple_1 != result_pos_value_simple_2:
                print("Delete OBSOLETE POs - Random Verification failed!")
                print(result_pos_value_simple_1)
                print(result_pos_value_simple_2)
                return False
            # if result_pos_value_simple_1 != result_pos_value_simple_3:
            #     return False

        print("Delete OBSOLETE POs - Random Verification x{} passed!".format(n_random_veri))
        return True



#######
    def update_current_pmig(self, new_pmig, random_veri = True):
        assert isinstance(new_pmig, PMIG)
        self._pmig_last = copy.deepcopy(self._pmig_current)
        self._pmig_current = copy.deepcopy(new_pmig)

        if random_veri:
            assert self._function_verification_random(n_random_veri=self._n_random_veri_default)

        print("---------------------")
        print("Update _pmig_current")
        print(self._pmig_last)
        print("------->")
        print(self._pmig_current)
        print("---------------------")



#######
    def get_current_pmig(self):
        return copy.deepcopy(self._pmig_current)

#######
    def get_last_pmig(self):
        return copy.deepcopy(self._pmig_last)

#######
    def get_init_pmig(self):
        return copy.deepcopy(self._pmig_init)


#######
    def savepoint_restore_to_the_last_pmig(self):
        print("Current PMIG is restored to the last version!")
        self._pmig_current = copy.deepcopy(self._pmig_last)
        self._pmig_last = None


#######
    def savepoint_save_current_pmig(self, name):
        assert isinstance(name, str)
        if name in self._pmig_savepoint_dict:
            print("Save current PMIG obj to savepoint. Key [" + name + "] created!")
        else:
            print("Save current PMIG obj to savepoint. The obj in key [" + name + "] is replaced!")
        self._pmig_savepoint_dict[name] = copy.deepcopy(self._pmig_current)

#######
    def savepoint_get_pmig(self, name):
        assert name in self._pmig_savepoint_dict
        return copy.deepcopy(self._pmig_savepoint_dict[name])

#######
    def savepoint_restore_pmig(self, name):
        assert name in self._pmig_savepoint_dict
        print("Current PMIG is restored to the version named as [" + name + "] !")
        # self._pmig_last = copy.deepcopy(self._pmig_current)
        # self._pmig_current = copy.deepcopy(self._pmig_savepoint_dict[name])
        self.update_current_pmig(new_pmig=self._pmig_savepoint_dict[name], random_veri=False)

#######
    def savepoint_delete_pmig(self, name):
        # assert name in self._pmig_savepoint_dict
        print("Remove key [" + name + '] in the savepoint!')
        self._pmig_savepoint_dict.pop(key=name)

#######
    def savepoint_delete_all(self):
        print("Savepoint initialized!")
        self._pmig_savepoint_dict = {}

#######
    def opti_clean_pos_by_type(self, po_type_tuple = (PMIG.PO_OBSOLETE, )):
        '''
        清除某些类型的POs， 并清除多余的nodes。

        :param po_type_tuple: TUPLE - POs类型元组，默认包含PMIG.PO_OBSOLETE.
        :return:
        '''
        # print('\n')
        print('>>> [PMIG_optimization] opti_clean_pos_by_type')
        # print('\n')
        assert isinstance(self._pmig_current, PMIG)
        new_pmig = self._pmig_current.pmig_clean_pos_by_type(po_type_tuple=po_type_tuple)
        self.update_current_pmig(new_pmig=new_pmig, random_veri=False)
        if po_type_tuple == (PMIG.PO_OBSOLETE, ):
            assert self._function_verification_random_for_delete_obsoleted_pos(n_random_veri=self._n_random_veri_default)

#######
    def opti_clean_irrelevant_nodes(self, pos = None):
        '''
        指定POs列表（指定id），清除与这些POs无关的node。

        :param pos: None (Default) or LIST - POs列表，默认包含当前全部POs.
        :return:
        '''
        # print('\n')
        print('>>> [PMIG_optimization] opti_clean_irrelevant_nodes')
        # print('\n')
        assert isinstance(self._pmig_current, PMIG)
        new_pmig = self._pmig_current.pmig_clean_irrelevant_nodes(pos=pos)
        if pos == None:
            random_veri = True
        else:
            random_veri = False
        self.update_current_pmig(new_pmig=new_pmig, random_veri=random_veri)

#######
    def opti_exact_synthesis_size_frompo(self, n_leaves):
        '''
        从上到下的exact synthesis。在使用该方法前请先使用opti_clean_irrelevant_nodes()方法对nodes进行排序。

        :param n_leaves:
        :return:
        '''
        # print('\n')
        print(">>> [PMIG_optimization] opti_exact_synthesis_size_frompo")

        flag_continue = True
        current_pmig_obj = self.get_current_pmig()
        assert isinstance(current_pmig_obj, PMIG)
        cnt_round = 1
        while flag_continue:
            print("ROUND {}".format(cnt_round))
            flag_continue = False
            maj_list = list(current_pmig_obj.get_iter_majs())
            for ii_maj_l in maj_list[::-1]:
                if (not flag_continue):
                    # print("Node {}".format(ii_maj_l))
                    sat_flag, optimized_mig_obj, n_maj_compare \
                        = PMIG_operator.op_cut_exact_synthesis_size(pmig_obj_r=current_pmig_obj,
                                                                    root_l=ii_maj_l,
                                                                    n_leaves=n_leaves,
                                                                    cut_computation_method='rec_driven',
                                                                    if_allow_0contribution=False)
                    if sat_flag:
                        flag_continue = True
                        # last_optimized_root_l = PMIG.get_noattribute_literal(f=new_literal_of_root)
                        current_pmig_obj = optimized_mig_obj
                        print("Round {}, Root {} - 已优化，{} MAJs -> {} MAJs".format(cnt_round, ii_maj_l, n_maj_compare[0],
                                                                                  n_maj_compare[1]))

            cnt_round = cnt_round + 1
        self.update_current_pmig(new_pmig=current_pmig_obj)
            # last_optimized_root_l = None # 用于记录上一个被优化的割集的root。由于优化后该root对应node的literal会减小，因此用此变量跳过在该root之上的nodes。
        #     for ii_maj_l in maj_list[::-1]:
        #         if (last_optimized_root_l == None) or ( (last_optimized_root_l != None) and (ii_maj_l < last_optimized_root_l) ):
        #             # print("Node {}".format(ii_maj_l))
        #             sat_flag, optimized_mig_obj, n_maj_compare \
        #                 = PMIG_operator.op_cut_exact_synthesis_size(pmig_obj_r=current_pmig_obj,
        #                                                             root_l=ii_maj_l,
        #                                                             n_leaves=n_leaves,
        #                                                             cut_computation_method='rec_driven',
        #                                                             if_allow_0contribution=False)
        #             if sat_flag:
        #                 flag_continue = True
        #                 last_optimized_root_l = PMIG.get_noattribute_literal(f=new_literal_of_root)
        #                 current_pmig_obj = optimized_mig_obj
        #                 print("Round {}, Root {} - 已优化，{} MAJs -> {} MAJs".format(cnt_round, ii_maj_l, n_maj_compare[0], n_maj_compare[1]))
        #
        #     cnt_round = cnt_round + 1
        # self.update_current_pmig(new_pmig=current_pmig_obj)


    # #######
    # def opti_exact_synthesis_size_frompo_allow_0contribution(self, n_leaves):
    #     '''
    #     与opti_exact_synthesis_size_frompo不同的是，该方法允许0优化的替换。但是，是否继续下一轮仍然不考虑0优化的替换。
    #
    #     从上到下的exact synthesis。在使用该方法前请先使用opti_clean_irrelevant_nodes()方法对nodes进行排序。
    #
    #     :param n_leaves:
    #     :return:
    #     '''
    #     # print('\n')
    #     print(">>> [PMIG_optimization] opti_exact_synthesis_size_frompo")
    #
    #     flag_continue = True
    #     current_pmig_obj = self.get_current_pmig()
    #     assert isinstance(current_pmig_obj, PMIG)
    #     cnt_round = 1
    #     cnt_0contri_only = 0 # 如果一轮中仅有0优化的替换，该变量加一。该变量用于指示是否连续几轮都是只有0优化的替换
    #     while flag_continue or (cnt_0contri_only < 2):
    #         print("ROUND {}, cnt:{}".format(cnt_round, cnt_0contri_only))
    #         flag_continue = False
    #         maj_list = list(current_pmig_obj.get_iter_majs())
    #         last_optimized_root_l = None  # 用于记录上一个被优化的割集的root。由于优化后该root对应node的literal会减小，因此用此变量跳过在该root之上的nodes。
    #         for ii_maj_l in maj_list[::-1]:
    #             if (last_optimized_root_l == None) or (
    #                     (last_optimized_root_l != None) and (ii_maj_l < last_optimized_root_l)):
    #                 # print("Node {}".format(ii_maj_l))
    #                 # if cnt_0contri_only == 0:
    #                 #     sat_flag, new_pmig, optimized_mig_obj, n_maj_compare, new_literal_of_root, info_tuple_cut, info_tuple_model \
    #                 #         = PMIG_operator.op_cut_exact_synthesis_size(pmig_obj_r=current_pmig_obj, root_l=ii_maj_l,
    #                 #                                                                         n_leaves=n_leaves)
    #                 # else:
    #                 #     sat_flag, new_pmig, optimized_mig_obj, n_maj_compare, new_literal_of_root, info_tuple_cut, info_tuple_model \
    #                 #         = PMIG_operator.op_cut_exact_synthesis_size_allow_0contribution(pmig_obj_r=current_pmig_obj, root_l=ii_maj_l,
    #                 #                                                     n_leaves=n_leaves)
    #                 sat_flag, new_pmig, optimized_mig_obj, n_maj_compare, new_literal_of_root, info_tuple_cut, info_tuple_model \
    #                     = PMIG_operator.op_cut_exact_synthesis_size(pmig_obj_r=current_pmig_obj,
    #                                                                                     root_l=ii_maj_l,
    #                                                                                     n_leaves=n_leaves,
    #                                                                                     cut_computation_method='rec_driven',
    #                                                                                     if_allow_0contribution=True)
    #                 if sat_flag:
    #                     assert n_maj_compare[0] >= n_maj_compare[1]
    #                     if n_maj_compare[0] > n_maj_compare[1]:
    #                         flag_continue = True
    #                         print("-------- Positive optimization! ------->")
    #                     last_optimized_root_l = PMIG.get_noattribute_literal(f=new_literal_of_root)
    #                     current_pmig_obj = optimized_mig_obj
    #                     print("Round {}, Root {} - 已替换，{} MAJs -> {} MAJs".format(cnt_round, ii_maj_l,
    #                                                                               n_maj_compare[0],
    #                                                                               n_maj_compare[1]))
    #
    #         if flag_continue:
    #             cnt_0contri_only = 0
    #         else:
    #             cnt_0contri_only = cnt_0contri_only + 1
    #         cnt_round = cnt_round + 1
    #     self.update_current_pmig(new_pmig=current_pmig_obj)

#######
    def opti_exact_synthesis_size_frompo_allow_0contribution(self, n_leaves):
        '''
        从上到下的exact synthesis。在使用该方法前请先使用opti_clean_irrelevant_nodes()方法对nodes进行排序。

        :param n_leaves:
        :return:
        '''
        # print('\n')
        print(">>> [PMIG_optimization] opti_exact_synthesis_size_frompo")

        cnt_0opti = 0
        max_0opti = 2
        flag_continue = True
        current_pmig_obj = self.get_current_pmig()
        assert isinstance(current_pmig_obj, PMIG)
        cnt_round = 1
        while flag_continue or (cnt_0opti <= max_0opti):
            cnt_0opti = cnt_0opti + 1
            print("ROUND {}".format(cnt_round))
            flag_continue = False
            maj_list = list(current_pmig_obj.get_iter_majs())
            for ii_maj_l in maj_list[::-1]:
                if (not flag_continue):
                    # print("Node {}".format(ii_maj_l))
                    sat_flag, optimized_mig_obj, n_maj_compare \
                        = PMIG_operator.op_cut_exact_synthesis_size(pmig_obj_r=current_pmig_obj,
                                                                    root_l=ii_maj_l,
                                                                    n_leaves=n_leaves,
                                                                    cut_computation_method='rec_driven',
                                                                    if_allow_0contribution=True)
                    if sat_flag:
                        if n_maj_compare[0] > n_maj_compare[1]:
                            cnt_0opti = 0
                            flag_continue = True
                        else:
                            assert n_maj_compare[0] == n_maj_compare[1]
                        # last_optimized_root_l = PMIG.get_noattribute_literal(f=new_literal_of_root)
                        current_pmig_obj = optimized_mig_obj
                        print("Round {}, Root {} - 已优化，{} MAJs -> {} MAJs".format(cnt_round, ii_maj_l,
                                                                                  n_maj_compare[0],
                                                                                  n_maj_compare[1]))

            cnt_round = cnt_round + 1
        self.update_current_pmig(new_pmig=current_pmig_obj)








