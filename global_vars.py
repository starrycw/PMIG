# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/5/19
# @Author  : c
# @File    : global_vars.py
#

# Functions
def _init():
    '''
    WARNING: It must be called at the beginning of the program and should only be called once.

    :return: 0(Success)
    '''
    global _global_dict
    _global_dict = {}
    ########################################################################################
    # Pre-defined global variables
    set_value_ifundefined('cnt_warning', 0)
    set_value('echo_mode', 3)
    set_path('path_main', '/home/elaina/Workspace/Projects/PyCharm/Polymorphic-MIG-dev-pre')
    set_path('path_abc_srcdir', get_value('path_main') + '/examples')
    set_path('path_aiger_dir', get_value('path_main') + '/tools/aiger')
    ########################################################################################
    return 0

def set_value(name, value):
    '''
    Create or modify a global variable

    :param name: String - Variable name
    :param value: Any - Variable value
    :return: Any - Current value of this variable
    '''
    _global_dict[name] = value
    return get_value(name)

def set_path(name, value):
    '''
    Create or modify a global path variable

    :param name: String - Variable name. (It is recommended to start with "path_" )
    :param value: String - New path
    :return: String - Current path
    '''
    # value must be of str type
    if not (isinstance(value, str)):
        print("[Warning] global_vars: ", name, "must be of str type! (", value, ")")
        print("[Warning] global_vars: Failed to initialize global variable:", name )
        set_cnt("cnt_warning", 1)
        return 1
    # The last char of value cannot be '/'
    if value[-1] == '/':
        value = value[0:-1]
    # set value
    set_value(name, value)
    return get_value(name)

def set_value_ifundefined(name, value):
    '''
    Create and modify a global variable only if it does not defined

    :param name: String - Variable name
    :param value: Any - Variable value
    :return: Current value of this variable.
    '''
    if _global_dict.get(name) == None:
        set_value(name, value)

def set_cnt(name, add_value):
    '''
    Create or modify a global counter. It will be defined first if not yet.

    :param name: String - Cnt name
    :param add_value: Int - 0 (Reset to 0) or !0 (cnt = cnt + add_value).

    :return: Int - Current cnt value
    '''
    if _global_dict.get(name) == None:
        set_value(name, 0)
    if add_value == 0:
        set_value(name, 0)
    else:
        set_value(name, get_value(name) + add_value)
    return get_value(name)

def get_value(name, defValue = None):
    '''
    Get the value of a global variable. If it does not exist, return defValue.

    :param name: String - Variable name
    :param defValue: Any - The value returned if the variable does not exist
    :return: Any - Variable value (if existed) or defValue (if not exist)
    '''
    try:
        return _global_dict[name]
    except KeyError:
        return defValue




