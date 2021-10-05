# PMIG

#### 说明

- 1\.  如何获取库文件(以Manjaro Linux 21 为例)
  - (1) 安装make, gcc, swig：
    ```
    sudo pacman -S make
    sudo pacman -S gcc
    sudo pacman -S swig
    ```
    
  - (2) 在ABC主目录执行：
    ```
    make ABC_USE_NO_READLINE=1 ABC_USE_PIC=1 libabc.so
    ```
    
  - (3) 将 abcd.i文件复制到/src目录中，并在/src目录中执行：
    ```
    swig -python abcd.i
    ```
    
  - (4) 确定Python.h所在的位置，例如 ：
    ```
    /usr/include/python3.9/
    ```
    在/src目录中依次执行：
    ```
    gcc -fPIC -c -I/usr/include/python3.9/ -I/home/xxx/abc-master/src abcd_wrap.c
    g++ -shared -fPIC -o _abcd.so `find . -name \*.o`
    ```
    


#### Reference
[1]. https://github.com/Berkeley-abc/abc

[2]. https://github.com/macd/abcd



