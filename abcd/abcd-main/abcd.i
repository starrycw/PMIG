%module abcd
%{
    #include <stdio.h>
    #include <time.h>
    typedef struct Abc_Frame_t_ Abc_Frame_t;
    extern void            Abc_Start();
    extern void            Abc_Stop();
    extern Abc_Frame_t *   Abc_FrameGetGlobalFrame();
    extern int Cmd_CommandExecute( Abc_Frame_t * pAbc, const char * sCommand );
%}

extern void            Abc_Start();
extern void            Abc_Stop();
extern Abc_Frame_t *   Abc_FrameGetGlobalFrame();
extern int Cmd_CommandExecute( Abc_Frame_t * pAbc, const char * sCommand );

// in clean abc directory first do the following
//     make ABC_USE_NO_READLINE=1 ABC_USE_PIC=1 libabc.so

// Now in the abc/src directory, first add abcd.i file then
//     swig -python abcd.i
// Find the appropriate Python.h file location for the include
//     gcc -fPIC -c -I/home/macd/anaconda3/include/python3.8 -I/home/macd/ghub/abc/src abcd_wrap.c
//     g++ -shared -fPIC -o _abcd.so `find . -name \*.o`

// Now you can 'import abcd' in Python (if abcd.py and _abcd.so are together and on your sys.path)

// Some Python helper code

%pythoncode %{

import os
import sys
from ctypes import CDLL
libc = CDLL('libc.so.6')
import tempfile


def abc_start():
    Abc_Start()
    pAbc = Abc_FrameGetGlobalFrame()
    def abc_cmd(scmd):
        old_fno = os.dup(sys.stdout.fileno())
        fd = tempfile.TemporaryFile()
        os.dup2(fd.fileno(), 1)
        status = Cmd_CommandExecute(pAbc, scmd)
        libc.fflush(None)
        os.dup2(old_fno, 1)

        fd.seek(0)
        msg = fd.read().decode()
        fd.close()
        return status, msg

    return abc_cmd
%}    
