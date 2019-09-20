PYTHON_ROOT=/build/toolchain/lin32/python-2.5
PYTHON_BIN=$PYTHON_ROOT/bin/python

rm -rf freeze
mkdir freeze
cd freeze

#/home/mabramow/bin/python2.5 /home/mabramow/sw/Python-2.5.2/Tools/freeze/freeze.py 
   #-p ~/sw/Python-2.5.2 

$PYTHON_BIN /home/mabramow/sw/Python-2.5.2/Tools/freeze/freeze.py \
   -p $PYTHON_ROOT \
   -X copy -X distutils -X macpath -X macurl2path -X ntpath -X nturl2path \
   -X os2emxpath -X popen2 -X pydoc -X email -X _threading_local \
   -X ftplib -X gopherlib \
   -X doctest -X difflib -X pdb -X base64 -X locale -X gettext \
   -X quopri -X uu \
   ../vmware-cmd2 \
   -m encodings.ascii -m readline -m operator -m site

# Can't get rid of threading, b/c pyVim.connect depends on it

make CC=/build/toolchain/lin32/gcc-3.4.6/bin/i686-linux-gcc \
     CXX=/build/toolchain/lin32/gcc-3.4.6/bin/i686-linux-g++ \
     LDFLAGS=-L/build/toolchain/lin32/RHEL5/lib

./vmware-cmd2
