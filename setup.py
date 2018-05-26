from distutils.core import setup
import setuptools
import py2exe

import sys
sys.setrecursionlimit(3000)
import os

#Initialize Holder Files
preference_files = []
app_files = []
builder_files = []
#my_data_files=matplotlib.get_py2exe_datafiles()

#define which files you want to copy for data_files
for files in os.listdir('C:\\Python27\\Lib\\site-packages\\psychopy\\preferences\\'):
    f1 = 'C:\\Python27\\Lib\\site-packages\\psychopy\\preferences\\' + files
    preference_files.append(f1)

###if you might need to import the app files
##for files in filter(os.path.isfile, os.listdir('C:\\Python27\\Lib\\site-packages\\psychopy\\app\\')):
##    f1 = 'C:\\Python27\\Lib\\site-packages\\psychopy\\app\\' + files
##    app_files.append(f1)
##
###adding builder files
##for files in os.listdir('C:\\Python27\\Lib\\site-packages\\psychopy\\app\\builder\\'):
##    f1 = 'C:\\Python27\\Lib\\site-packages\\psychopy\\app\\builder\\' + files
##    builder_files.append(f1)

app_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk('C:\\Python27\\Lib\\site-packages\\psychopy\\app\\') for f in filenames]

all_files = [("psychopy\\preferences", preference_files),("psychopy\\app", app_files)]

#combine the files
#all_files = [("psychopy\\preferences", preference_files), my_data_files[0]]
#all_files = [("psychopy\\preferences", preference_files)]


#import matplotlib as mpl
#data_files += mpl.get_py2exe_datafiles()

#setup(options={"py2exe":{"dll_excludes":["MSVCP90.dll"]}}, console=['PyVMEC.py'], data_files=data_files)
setup(
    
    options = {
        "py2exe": {
            "includes": ["pandas", "psychopy", "UserList", "UserString"],
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
