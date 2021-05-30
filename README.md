# Polymorphic-MIG-dev

#### 介绍
多态MIG

#### 环境需求
Linux & Python 3.9

#### 安装教程
- 1\.  下载并解压。
- 2\.  按照 https://github.com/macd/abcd 中的方法，编译ABC( https://github.com/Berkeley-abc/abc )，
    并将得到的abcd.py和_abcd.so文件放置于./abcd目录。具体步骤如下 (以Manjaro Linux 21 为例)：
  - (1) 安装make, gcc, swig。依次执行：
    ```
    sudo pacman -S make
    sudo pacman -S gcc
    sudo pacman -S swig
    ```
    
  - (2) 下载 ABC( https://github.com/Berkeley-abc/abc ) 并解压至空文件夹， 并在解压后的目录执行：
    ```
    make ABC_USE_NO_READLINE=1 ABC_USE_PIC=1 libabc.so
    ```
    
  - (3) 将 abcd.i文件复制到abc-master/src目录中，并在该目录中执行：
    ```
    swig -python abcd.i
    ```
    abcd.i文件可从本仓库./abcd目录中获取，或者从 https://github.com/macd/abcd 下载。
    
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

