# PyVMEC
A Python-based GUI to create and run visuo-motor experiments.

## Environment:

- Python 2.7 *Application created and tested working on Python 2.7.15*
- wxpython 3.0.2 > For Windows: available on sourceforge https://sourceforge.net/projects/wxpython/files/wxPython/3.0.2.0/
(Download wxPython3.0-win64-3.0.2.0-py27.exe and run)
  For Linux: wxpython 3.0.2 available as default version through apt / synaptic package installer on Debian based distributions.

## Dependencies:

`pip install -U numpy scipy pandas six psychopy==1.85.3 pyglet==1.3.0`

`pip install json_tricks configobj screeninfo pyautogui`

## Troubleshooting:

Experiment window not showing any objects, or window not appearing at all:
-Make sure openGL Version is 2.0+
-Easily fixed by updating graphics drivers.

## Developers:

Julius Martin [https://github.com/juliusjgm12] - September 2017 to December 2018

