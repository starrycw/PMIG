# Polymorphic-MIG-dev

#### 介绍
多态MIG

#### 环境需求
Linux & Python 3.9

#### 安装教程
- 1\.  下载本仓库并解压。
- 2\.  下载ABC并解压 [1]。然后将其编译为Python可调用的库文件 [2]。将得到的abcd.py和_abcd.so文件放置于./abcd目录。具体步骤如下 (以Manjaro Linux 21 为例)：
  - (1) 安装make, gcc, swig。依次执行：
    ```
    sudo pacman -S make
    sudo pacman -S gcc
    sudo pacman -S swig
    ```
    
  - (2) 下载 ABC [1] 并解压至空文件夹， 并在解压后的目录执行：
    ```
    make ABC_USE_NO_READLINE=1 ABC_USE_PIC=1 libabc.so
    ```
    
  - (3) 将 abcd.i文件复制到abc-master/src目录中，并在该目录中执行：
    ```
    swig -python abcd.i
    ```
    abcd.i文件可从本仓库./abcd目录中获取，或者从 [2] 下载。
    
  - (4) 确定Python.h所在的位置，例如 ：
    ```
    /usr/include/python3.9/
    ```
    在abc-master/src目录中依次执行：
    ```
    gcc -fPIC -c -I/usr/include/python3.9/ -I/home/xxx/abc-master/src abcd_wrap.c
    g++ -shared -fPIC -o _abcd.so `find . -name \*.o`
    ```
    
#### 使用说明

1.  xxxx
2.  xxxx
3.  xxxx

#### Reference
[1]. https://github.com/Berkeley-abc/abc
[2]. https://github.com/macd/abcd



