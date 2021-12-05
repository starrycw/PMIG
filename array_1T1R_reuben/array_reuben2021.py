# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/12/01
# @Author  : c

# 定义能够表示一个[1]中1T1R阵列的类。
# [1] J. Reuben and S. Pechmann, “Accelerated Addition in Resistive RAM Array Using Parallel-Friendly Majority Gates,” IEEE Trans. VLSI Syst., vol. 29, no. 6, pp. 1108–1121, Jun. 2021, doi: 10.1109/TVLSI.2021.3068470.
import copy
from pmig import graphs

class _Base_Array_Reuben2021:
    def __init__(self, n_row, n_sa, available_col_per_sa, list_sa_polymorphic, array_name=None):
        '''

        :param n_row: 阵列的行数
        :param n_sa: 阵列的SA数。在该阵列中，每个SA对应着8列。
        :param available_col_per_sa: 每个SA可用的列数（1～8）。在该阵列中，每个SA对应着8列，但该变量限制了可用的列数。例如，若该变量为3,则只每个SA只允许对前三列进行操作。
        :param list_sa_polymorphic: 列表，元素应为Bool。每个元素对应着一个SA。若为False，则对应SA的输出路径上无多态BUF/INV门；若为True，则对应SA的输出路径上有一个多态BUF/INV门。
        :param array_name: 阵列名称。默认为None。
        '''

        # Name
        if array_name:
            assert isinstance(array_name, str)
        self._arrayName = array_name # 阵列名称

        # Size
        assert isinstance(n_row, int)
        assert isinstance(n_sa, int)
        assert isinstance(available_col_per_sa, int)
        assert n_row > 0
        assert n_sa > 0
        assert 0 < available_col_per_sa <= 8
        self._arraySizeRow = n_row # 阵列行数
        self._arraySizeSA = n_sa # 阵列的SA数。在该阵列，每个SA对应着8列。
        self._arraySizeAvailableColPerSA = available_col_per_sa # 每个SA对应着8列，但该变量限制了可用的列数。例如，若该变量为3,则只每个SA只允许对前三列进行操作。


        # Array
        # 需要注意的是，本类与要映射的PMIG相互独立，只提供记录每个rram此时代表的literal或阻值等信息的更新/读出方法。

        self._arrayDataLiteral = n_row * [n_sa * [8 * [None]]] # 元素应当为PMIG对象中的Literal。None代表未初始化。
        # 索引从外到内分别为：行序号（0 ～ 行数-1）, SA序号（0 ～ SA数-1）， 该行中与该SA对应的元素序号（0～7）。

        self._arrayDataResistance = n_row * [n_sa * [8 * [None]]]  # 元素应当为阻值状态。True-LRS， False-HRS， None-未初始化
        # 索引从外到内分别为：行序号（0 ～ 行数-1）, SA序号（0 ～ SA数-1）， 该行中与该SA对应的元素序号（0～7）。

        # SA属性
        self._arraySAPolymorphic = copy.deepcopy(list_sa_polymorphic) # 元素应当为Bool，表示对应SA后面是否连接了一个多态BUF/INV门。
        assert isinstance(list_sa_polymorphic, list)
        assert len(list_sa_polymorphic) == n_sa
        for temp_i in list_sa_polymorphic:
            assert temp_i in (True, False)

        self._arrayPolymorphicState = n_sa * [None]  # 元素应当为Bool，表示当前多态门处于状态1(False)还是状态2(True)。需要注意的是，若采用温度等环境信号控制，那这个列表中的值应保持一致。

    def reset_rrams(self):
        '''
        重置存储RRAMliteral/阻值状态的变量到初始的未定义状态。

        :return:
        '''

        n_row = self.array_get_n_row()
        n_sa = self.array_get_n_sa()

        self._arrayDataLiteral = n_row * [n_sa * [8 * [None]]]  # 元素应当为PMIG对象中的Literal。None代表未初始化。
        # 索引从外到内分别为：行序号（0 ～ 行数-1）, SA序号（0 ～ SA数-1）， 该行中与该SA对应的元素序号（0～7）。

        self._arrayDataResistance = n_row * [n_sa * [8 * [None]]]  # 元素应当为阻值状态。True-LRS， False-HRS， None-未初始化
        # 索引从外到内分别为：行序号（0 ～ 行数-1）, SA序号（0 ～ SA数-1）， 该行中与该SA对应的元素序号（0～7）。

    def array_get_n_sa(self):
        '''
        返回阵列的SA数。

        :return: int
        '''
        return self._arraySizeSA

    def array_get_n_row(self):
        '''
        返回阵列的行数。

        :return: int
        '''
        return self._arraySizeRow

    def array_get_n_available_col_per_sa(self):
        '''
        返回阵列中一个SA限制可用的列数。

        :return: int
        '''
        return self._arraySizeAvailableColPerSA

    def array_get_polymorphic_flags(self):
        '''
        返回一个列表，其元素为Bool，分别表示是对应SA后面是否存在一个BUF/INV多态门。

        :return: list(bool)
        '''
        return copy.deepcopy(self._arraySAPolymorphic)

    def array_get_polymorphic_states(self):
        '''
        返回一个列表，其元素为Bool，分别表示是对应SA后面的BUF/INV多态门是处于状态1（False）还是状态2（True）。

        :return: list(bool)
        '''
        return copy.deepcopy(self._arrayPolymorphicState)

    def array_get_rrams_literal(self):
        '''
        返回所有rram的literal，即self._arrayDataLiteral。

        :return:
        '''
        return copy.deepcopy(self._arrayDataLiteral)

    def array_get_rrams_resistance(self):
        '''
        返回所有rram的阻值状态，即self._arrayDataResistance。

        :return:
        '''
        return copy.deepcopy(self._arrayDataResistance)

    def update_rram_literal(self, idx_row, idx_SA, idx_col, new_literal):
        '''
        更新某个RRAM的Literal

        :param idx_row:
        :param idx_SA:
        :param idx_col:
        :param new_literal:
        :return:
        '''
        assert isinstance(idx_row, int)
        assert isinstance(idx_SA, int)
        assert isinstance(idx_col, int)
        assert isinstance(new_literal, int)
        assert 0 <= idx_row < self.array_get_n_row()
        assert 0 <= idx_SA < self.array_get_n_sa()
        assert 0 <= idx_col < self.array_get_n_available_col_per_sa()

        self._arrayDataLiteral[idx_row][idx_SA][idx_col] = new_literal

    def update_rram_resistance(self, idx_row, idx_SA, idx_col, new_state):
        '''
        更新某个RRAM的阻值状态

        :param idx_row:
        :param idx_SA:
        :param idx_col:
        :param new_state:
        :return:
        '''
        assert isinstance(idx_row, int)
        assert isinstance(idx_SA, int)
        assert isinstance(idx_col, int)
        assert isinstance(new_state, bool)
        assert 0 <= idx_row < self.array_get_n_row()
        assert 0 <= idx_SA < self.array_get_n_sa()
        assert 0 <= idx_col < self.array_get_n_available_col_per_sa()

        self._arrayDataResistance[idx_row][idx_SA][idx_col] = new_state

    def get_rram_literal(self, idx_row, idx_SA, idx_col):
        '''
        获取某个RRAM的Literal

        :param idx_row:
        :param idx_SA:
        :param idx_col:
        :return:
        '''
        assert isinstance(idx_row, int)
        assert isinstance(idx_SA, int)
        assert isinstance(idx_col, int)
        assert 0 <= idx_row < self.array_get_n_row()
        assert 0 <= idx_SA < self.array_get_n_sa()
        assert 0 <= idx_col < self.array_get_n_available_col_per_sa()

        return self._arrayDataLiteral[idx_row][idx_SA][idx_col]

    def get_rram_resistance(self, idx_row, idx_SA, idx_col):
        '''
        获取某个RRAM的阻值状态

        :param idx_row:
        :param idx_SA:
        :param idx_col:
        :return:
        '''
        assert isinstance(idx_row, int)
        assert isinstance(idx_SA, int)
        assert isinstance(idx_col, int)
        assert 0 <= idx_row < self.array_get_n_row()
        assert 0 <= idx_SA < self.array_get_n_sa()
        assert 0 <= idx_col < self.array_get_n_available_col_per_sa()

        return self._arrayDataResistance[idx_row][idx_SA][idx_col]


    def init_rrams(self, method):
        '''
        初始化阵列中的RRAM。

        method = 'LRS': 所有可用的RRAM被初始化为LRS（Literal = 0）。

        :param method:
        :return:
        '''
        # 全部置为LRS
        if method == 'LRS':
            for temp_i_row in range(0, self.array_get_n_row()):
                for temp_i_sa in range(0, self.array_get_n_sa()):
                    for temp_i_col in range(0, self.array_get_n_available_col_per_sa()):
                        self.update_rram_literal(idx_row=temp_i_row,
                                                 idx_SA=temp_i_sa,
                                                 idx_col=temp_i_col,
                                                 new_literal=0)
                        self.update_rram_resistance(idx_row=temp_i_row,
                                                    idx_SA=temp_i_sa,
                                                    idx_col=temp_i_col,
                                                    new_state=True)

        else:
            assert False

    @staticmethod
    def sm_compute_maj_resistance_state(rs_0, rs_1, rs_2):
        '''
        输入三个阻值状态作为MAJ扇入，返回MAJ输出的阻值状态。

        其中，阻值状态可以为：True（表示LRS），False（表示HRS），None（表示未知）。
        该方法不允许任一个RRAM处于未定义状态！

        :param rs_0:
        :param rs_1:
        :param rs_2:
        :return:
        '''
        assert rs_0 in (True, False, None)
        assert rs_1 in (True, False, None)
        assert rs_2 in (True, False, None)

        if rs_0 == rs_1:
            return rs_0
        elif rs_1 == rs_2:
            return rs_1
        elif rs_2 == rs_0:
            return rs_2
        else:
            return None


class Array_Reuben2021_LiteralOnly(_Base_Array_Reuben2021):
    def __init__(self, n_row, n_sa, available_col_per_sa, list_sa_polymorphic, array_name=None):
        '''

        :param n_row: 阵列的行数
        :param n_sa: 阵列的SA数。在该阵列中，每个SA对应着8列。
        :param available_col_per_sa: 每个SA可用的列数（1～8）。在该阵列中，每个SA对应着8列，但该变量限制了可用的列数。例如，若该变量为3,则只每个SA只允许对前三列进行操作。
        :param list_sa_polymorphic: 列表，元素应为Bool。每个元素对应着一个SA。若为False，则对应SA的输出路径上无多态BUF/INV门；若为True，则对应SA的输出路径上有一个多态BUF/INV门。
        :param array_name: 阵列名称。默认为None。
        '''
        super().__init__(n_row=n_row,
                         n_sa=n_sa,
                         available_col_per_sa=available_col_per_sa,
                         list_sa_polymorphic=list_sa_polymorphic,
                         array_name=array_name)


    def operation_READ(self, idx_row, list_idx_col_of_sa):
        '''
        READ操作。指定行（idx_row）和各个SA的列（list_idx_of_sa，有要读取的对象时元素为0～7，没有要读取的对象时元素为None）。
        返回literal元组。
        其中，literal元组中每一个元素都为literal。

        该操作考虑多态门影响，但INV信号保持为0。
        该方法不允许读取处于未定义状态的RRAM！

        :param idx_row: int
        :param list_idx_col_of_sa: list(int/None)
        :return:
        '''
        assert isinstance(idx_row, int)
        assert isinstance(list_idx_col_of_sa, list)
        assert 0 <= idx_row < self.array_get_n_row()
        assert len(list_idx_col_of_sa) == self.array_get_n_sa()
        result_literal = []
        temp_idx_sa = 0
        temp_polymorphic_flags = self.array_get_polymorphic_flags()
        temp_polymorphic_states = self.array_get_polymorphic_states()

        for temp_i_col in list_idx_col_of_sa:
            if temp_i_col is None:
                result_literal.append(None)
            else:
                assert 0 <= temp_i_col < self.array_get_n_available_col_per_sa()
                temp_i_literal = self.get_rram_literal(idx_row=idx_row, idx_SA=temp_idx_sa, idx_col=temp_i_col)
                assert isinstance(temp_i_literal, int)
                # polymorphic
                if temp_polymorphic_flags[temp_idx_sa]:
                    temp_i_literal = graphs.PMIG.polymorphic_literal_if(f=temp_i_literal, c=True)
                result_literal.append(temp_i_literal)

            temp_idx_sa = temp_idx_sa + 1
            assert 0 <= temp_idx_sa <= self.array_get_n_sa()

        result_literal_tuple = tuple(result_literal)
        return result_literal_tuple

    def operation_NOT(self, idx_row, list_idx_col_of_sa):
        '''
        NOT操作。指定行（idx_row）和各个SA的列（list_idx_of_sa，有要读取的对象时元素为0～7，没有要读取的对象时元素为None）。
        返回literal元组。
        其中，literal元组中每一个元素都为literal。

        该操作考虑多态门影响，但INV信号保持为1。
        该方法不允许读取处于未定义状态的RRAM！

        :param idx_row: int
        :param list_idx_col_of_sa: list(int/None)
        :return:
        '''
        assert isinstance(idx_row, int)
        assert isinstance(list_idx_col_of_sa, list)
        assert 0 <= idx_row < self.array_get_n_row()
        assert len(list_idx_col_of_sa) == self.array_get_n_sa()
        result_literal = []
        temp_idx_sa = 0
        temp_polymorphic_flags = self.array_get_polymorphic_flags()
        temp_polymorphic_states = self.array_get_polymorphic_states()

        for temp_i_col in list_idx_col_of_sa:
            if temp_i_col is None:
                result_literal.append(None)
            else:
                assert 0 <= temp_i_col < self.array_get_n_available_col_per_sa()
                temp_i_literal = self.get_rram_literal(idx_row=idx_row, idx_SA=temp_idx_sa, idx_col=temp_i_col)
                assert isinstance(temp_i_literal, int)
                # inverter
                temp_i_literal = graphs.PMIG.negate_literal_if(f=temp_i_literal, c=True)
                # polymorphic
                if temp_polymorphic_flags[temp_idx_sa]:
                    temp_i_literal = graphs.PMIG.polymorphic_literal_if(f=temp_i_literal, c=True)
                result_literal.append(temp_i_literal)

            temp_idx_sa = temp_idx_sa + 1
            assert 0 <= temp_idx_sa <= self.array_get_n_sa()

        result_literal_tuple = tuple(result_literal)
        return result_literal_tuple




    def operation_MAJORITY(self, idx_row, list_idx_col_of_sa):
        '''
        Majority操作。指定首行（idx_row）和各个SA的列（list_idx_of_sa，有要读取的对象时元素为0～7，没有要读取的对象时元素为None）。
        返回literal元组。
        其中，literal元组中每一个元素都为4元素的元组（扇入0的literal, 扇入1的literal, 扇入2的literal, 扇出是否添加多态属性）。


        该操作考虑多态门影响，但INV信号保持为0。

        :param idx_row:
        :param list_idx_col_of_sa:
        :return:
        '''
        assert isinstance(idx_row, int)
        assert isinstance(list_idx_col_of_sa, list)
        assert 0 <= idx_row < self.array_get_n_row() - 2 # 会选中行idx_row以及其下面紧跟的2行。
        assert len(list_idx_col_of_sa) == self.array_get_n_sa()
        result_literal = []
        temp_idx_sa = 0
        temp_polymorphic_flags = self.array_get_polymorphic_flags()
        temp_polymorphic_states = self.array_get_polymorphic_states()

        for temp_i_col in list_idx_col_of_sa:
            if temp_i_col is None:
                result_literal.append(None)
            else:
                assert 0 <= temp_i_col < self.array_get_n_available_col_per_sa()
                # RRAM 0
                temp_i0_literal = self.get_rram_literal(idx_row=idx_row, idx_SA=temp_idx_sa, idx_col=temp_i_col)
                assert isinstance(temp_i0_literal, int)
                # RRAM 1
                temp_i1_literal = self.get_rram_literal(idx_row=idx_row+1, idx_SA=temp_idx_sa, idx_col=temp_i_col)
                assert isinstance(temp_i1_literal, int)
                # RRAM 2
                temp_i2_literal = self.get_rram_literal(idx_row=idx_row+2, idx_SA=temp_idx_sa, idx_col=temp_i_col)
                assert isinstance(temp_i2_literal, int)
                # Majority
                temp_imaj_literal_only = (temp_i0_literal, temp_i1_literal, temp_i2_literal)

                # polymorphic
                temp_imaj_literal_polymorphic_flag = False
                if temp_polymorphic_flags[temp_idx_sa]:
                    temp_imaj_literal_polymorphic_flag = True

                temp_imaj_literal_tuple = temp_imaj_literal_only + (temp_imaj_literal_polymorphic_flag, )
                result_literal.append(temp_imaj_literal_tuple)
            temp_idx_sa = temp_idx_sa + 1
            assert 0 <= temp_idx_sa <= self.array_get_n_sa()

        result_literal_tuple = tuple(result_literal)
        return result_literal_tuple


    def operation_WRITE(self, idx_row, list_to_be_write):
        '''
        WRITE操作。指定行（idx_row）和要写入的literal（ list_to_be_write=[ (SA地址_1, 列地址_1, literal_1), (SA地址_2, 列地址_2, literal_2), ... ]。


        :param idx_row: int
        :param list_to_be_write: list( tuple(int) )
        :return:
        '''
        assert isinstance(idx_row, int)
        assert isinstance(list_to_be_write, list)
        assert 0 <= idx_row < self.array_get_n_row()
        temp_list_idx_col_used = []

        for temp_i_to_be_write in list_to_be_write:
            assert isinstance(temp_i_to_be_write, tuple)
            assert len(temp_i_to_be_write) == 3
            temp_i_idx_sa = temp_i_to_be_write[0]
            temp_i_idx_col = temp_i_to_be_write[1]
            temp_i_literal = temp_i_to_be_write[2]
            assert isinstance(temp_i_idx_sa, int)
            assert isinstance(temp_i_idx_col, int)
            assert isinstance(temp_i_literal, int)
            assert 0 <= temp_i_idx_sa < self.array_get_n_sa()
            assert 0 <= temp_i_idx_col < self.array_get_n_available_col_per_sa()
            assert (temp_i_idx_sa, temp_i_idx_col) not in temp_list_idx_col_used
            temp_list_idx_col_used.append( (temp_i_idx_sa, temp_i_idx_col) )
            self.update_rram_literal(idx_row=idx_row, idx_SA=temp_i_idx_sa, idx_col=temp_i_idx_col, new_literal=temp_i_literal)


