from distutils.core import setup
import py2exe

#data_files = []

#import matplotlib as mpl
#data_files += mpl.get_py2exe_datafiles()

#setup(options={"py2exe":{"dll_excludes":["MSVCP90.dll"]}}, console=['PyVMEC.py'], data_files=data_files)
setup( options = {
    "py2exe": {
        "includes": ["pandas"],
        "dll_excludes":["MSVCP90.dll"],
        "excludes":["gevent._socket3"] }
    },
       console=['PyVMEC.py'])


# run this from command line with the following command:
# $ python setup.py py2exe
# from the directory where the to be compiled script is
