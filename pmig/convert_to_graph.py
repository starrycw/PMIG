# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/5/19
# @Author  : c
# @File    : convert_to_graph.py
#
# Convert source file (verilog, blif, ...) to graph (AIG, MIG)

# import
import sys
sys.path.append("..")
import abcd.abcd as my_abc
import subprocess
import os

# Exception
class ReturnCodeError(Exception):
    pass
class InaccessibleFileError(Exception):
    pass

# Function: convert_to_aiger
def convert_to_aiger(abc_srcdir, abc_srcfile, aiger_dir, abc_ops = ("strash", "rewrite"), echo_mode = 3):
    '''
    Convert design source file (verilog, blif, ...) to AIGER file (aig, aag).

    :param abc_srcdir: String - The path of source file (without file name).
    :param abc_srcfile: String - The full name of source file (with extension, eg. "adder.v").
    :param aiger_dir: String - The path of aiger tools.
    :param abc_ops: Tuple with strings - The operations performed by ABC, such as: ("strash", "rewrite").
    :param echo_mode: Int - 0 (ERRORs only); 1 (WARNINGs); 2 (INFOs); 3 (All).

    :return: State, warningcnt: State=0 if no error occurred
    '''

    try:
        if echo_mode > 2: print("****[pmig/design_to_aiger/convert_to_aiger]****")
        if echo_mode > 2: print("*********************BEGIN*********************")

        # warningcnt. It should be a return value instead of a global var!
        warningcnt = 0

        #Some checks
        if not isinstance(abc_srcdir, str):
            raise TypeError("convert_to_aiger: The param 'abc_srcdir' must be of string type! (value: {})".format(abc_srcdir))
        if not isinstance(abc_srcfile, str):
            raise TypeError("convert_to_aiger: The param 'abc_srcfile' must be of string type! (value: {})".format(abc_srcfile))
        if not isinstance(aiger_dir, str):
            raise TypeError("convert_to_aiger: The param 'aiger_dir' must be of string type! (value: {})".format(aiger_dir))
        if not isinstance(abc_ops, tuple):
            raise TypeError("convert_to_aiger: The param 'abc_ops' must be of tuple type! (value: {})".format(abc_ops))
        if abc_srcdir[-1] == '/':
            abc_srcdir = abc_srcdir[0:-1]
        if aiger_dir[-1] == '/':
            aiger_dir = aiger_dir[0:-1]
        if not os.access(aiger_dir + '/aigtoaig', os.R_OK):
            raise InaccessibleFileError("convert_to_aiger: aigtoaig (" + aiger_dir + "/aigtoaig) is not accessible!")
        if not os.access(abc_srcdir + '/' + abc_srcfile, os.R_OK):
            raise InaccessibleFileError("convert_to_aiger: source file (" + abc_srcdir + '/' + abc_srcfile + ") is not accessible!")

        # abc: start
        abc = my_abc.abc_start()

        # abc: read source file
        status, msg = abc("read " + abc_srcdir + '/' + abc_srcfile)
        if status != 0:
            raise ReturnCodeError("abc: " + msg)
        else:
            if echo_mode > 1:
                print("[INFO] abc: Read source file " + abc_srcdir + '/' + abc_srcfile)
                status, msg = abc("print_stats")
                print("[INFO] abc: Current state: \n" + msg)

        # abc: Perform operations
        for op in abc_ops:
            # abc: strash (Structual hashing)
            if op == "strash":
                status, msg = abc("strash")
                if status != 0:
                    raise ReturnCodeError("abc: " + msg)
                else:
                    if echo_mode > 1:
                        status, msg = abc("print_stats")
                        print("[INFO] abc: Structural hashing performed! Current state: \n" + msg)

            # abc: rewrite (Rewriting)
            elif op == "rewrite":
                status, msg = abc("rewrite")
                if status != 0:
                    raise ReturnCodeError("abc: " + msg)
                else:
                    if echo_mode > 1:
                        status, msg = abc("print_stats")
                        print("[INFO] abc: Rewriting performed! Current state: \n" + msg)

            # alias resyn2      "b; rw; rf; b; rw; rwz; b; rfz; rwz; b"
            elif op == "resyn2":
                status, msg = abc('balance; rewrite; refactor; balance; rewrite; rewrite -z; balance; refactor -z; rewrite -z; balance')
                if status != 0:
                    raise ReturnCodeError("abc: " + msg)
                else:
                    if echo_mode > 1:
                        status, msg = abc("print_stats")
                        print("[INFO] abc: resyn2 performed! Current state: \n" + msg)




            # abc: Undefined op
            else:
                if echo_mode > 0:
                    print("[WARNING] abc: Undefined operation \"" + op + "\"!")
                warningcnt = warningcnt + 1

        # abc: Write .aig file
        status, msg = abc("write_aiger " + abc_srcdir + '/' + abc_srcfile + ".aig")
        if status != 0:
            raise ReturnCodeError("abc: Failed to write aig file: " + abc_srcdir + '/' + abc_srcfile + ".aig" + " (" + msg + ")")
        else:
            if echo_mode > 1:
                print("[INFO] abc: Save binary AIGER file (aig) to " + abc_srcdir + '/' + abc_srcfile + ".aig")

        # aigtoaig: convert aig to aag
        process_status = subprocess.run(aiger_dir + "/aigtoaig" + " " + abc_srcdir + '/' + abc_srcfile + ".aig " + \
                                        abc_srcdir + '/' + abc_srcfile + ".aag", shell=True)
        if process_status.returncode != 0:
            raise ReturnCodeError("aigtoaig: " + process_status.args)
        else:
            if echo_mode > 1: print(
                "[INFO] aigtoaig: Save ASCII AIGER file (aag) to " + abc_srcdir + '/' + abc_srcfile + ".aag")

        # finally
        my_abc.Abc_Stop()
        if echo_mode > 2:
            print("[INFO] convert_to_graph: Return with", warningcnt, "warning(s).")
        return 0, warningcnt

    except Exception as e:
        print("[ERROR] convert_to_graph: An error occurred! The details are as follows: \n       ", e)
        return 1, warningcnt

    finally:
        my_abc.Abc_Stop()
        if echo_mode > 2:
            print("*********************END*********************")
# END of Function: convert_to_aiger