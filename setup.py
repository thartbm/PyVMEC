from distutils.core import setup
import setuptools
import matplotlib
import py2exe

import sys
sys.setrecursionlimit(3000)
import os

# pandas._libs.tslibs.conversion._TSObject should have an attribute __reduce_cython__
# in versions of pandas > 0.20.0 (at least for Python < 3.4)
# so: pip install pandas==0.20.0

# with psychopy 1.90.0 and pyglet 1.3.2 we get an error that the window has no close() attribute
# someone solved this like this:
# pip install psychopy==1.85.3
# pip install pyglet==1.3.0
# this removes the error, but the experiment still doesn't work

#Initialize Holder Files
preference_files = []
app_files = []
builder_files = []
lib23_files = []
pandas_libs_files = []
visual_files = []
misc_files = []

some_dlls = []
my_data_files=matplotlib.get_py2exe_datafiles()

#define which files you want to copy for data_files
for files in os.listdir('C:\\Python27\\Lib\\site-packages\\psychopy\\preferences\\'):
    f1 = 'C:\\Python27\\Lib\\site-packages\\psychopy\\preferences\\' + files
    preference_files.append(f1)

app_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk('C:\\Python27\\Lib\\site-packages\\psychopy\\app\\') for f in filenames]

lib23_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk('C:\\Python27\\Lib\\lib2to3\\') for f in filenames]

pandas_libs_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk('C:\\Python27\\Lib\\site-packages\\pandas\\_libs\\') for f in filenames] 

visual_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk('C:\\Python27\\Lib\\site-packages\\psychopy\\visual\\') for f in filenames]

misc_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk('C:\\Python27\\Lib\\site-packages\\psychopy\\misc\\') for f in filenames]


import glob

some_dlls += glob.glob('C:\\Python27\\DLLs\\libansari.*')
some_dlls += glob.glob('C:\\Python27\\DLLs\\liblbfgsb.*')
some_dlls += glob.glob('C:\\Python27\\DLLs\\libgetbreak.*')
some_dlls += glob.glob('C:\\Python27\\DLLs\\libdqag.*')
#some_dlls += 'C:\\Windows\\System32\\avbin.dll'

print(some_dlls)


all_files = [ ("psychopy\\preferences", preference_files),
              ("psychopy\\app", app_files),
              ("psychopy\\visual", visual_files),
              ("psychopy\\misc", misc_files),
              ('lib2to3', lib23_files),
              ("pandas\\_lib", pandas_libs_files),
              ]

#combine the files
#all_files = [("psychopy\\preferences", preference_files), my_data_files[0]]
#all_files = [("psychopy\\preferences", preference_files)]

all_files += some_dlls

import matplotlib as mpl
all_files += mpl.get_py2exe_datafiles()

#setup(options={"py2exe":{"dll_excludes":["MSVCP90.dll"]}}, console=['PyVMEC.py'], data_files=data_files)
setup(
    
    options = {
        "py2exe": {
            "includes": ["pandas",
                         "pyautogui",
                         "psychopy",
                         "psychopy.visual.shape",
                         "psychopy.visual.circle",
                         "psychopy.misc",
                         "UserList",
                         "UserString",
                         "numpy",
                         "scipy.sparse.csgraph._validation",
                         "scipy.linalg.cython_blas",
                         "scipy.linalg.cython_lapack",
                         "scipy.linalg",
                         "scipy.special._ufuncs_cxx",
                         "scipy._lib.messagestream",
                         "pyglet.resource",
                         "PIL.Image",
                         "pkg_resources._vendor.appdirs",
                         "pkg_resources._vendor.packaging",
                         "pkg_resources._vendor.packaging.version",
                         "pkg_resources._vendor.packaging.specifiers",
                         "pkg_resources._vendor.packaging.requirements"],
            "dll_excludes":["MSVCP90.dll"],
            "excludes":["gevent._socket3"],
            "skip_archive": True,
            "optimize": 2
            }
    },
    console=['PyVMEC.py'],
    data_files = all_files,

       )


# run this from command line with the following command:
# $ python setup.py py2exe
# from the directory where the to be compiled script is
