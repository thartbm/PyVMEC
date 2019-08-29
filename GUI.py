# this file has functions that create, populate and update the GUI
import wx
from psychopy.visual import Window, Circle, ShapeStim, TextStim, ImageStim
from psychopy import event, core
from psychopy.visual import shape
from gettext import install
from math import ceil
from os import path, makedirs, remove, listdir, rename
from shutil import copyfile
from json import load, dump
from copy import deepcopy
from numpy import array
#import path
import Tkinter as tk
import Exp as exp
import traceback
import Preprocess as pp
import csv

#import VMEC16 as vm
root = tk.Tk()
class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        if path.exists('VMEC.ico'):
            self.SetIcon(wx.Icon("VMEC.ico"))
        elif path.exists("PyVMEC-0.9.3" + path.sep + "VMEC.ico"):
            self.SetIcon(wx.Icon("PyVMEC-0.9.3" + path.sep + "VMEC.ico"))

        ### Gather Experiment names
        self.experiment_folder = "experiments" + path.sep
        if not(path.exists(self.experiment_folder)):
            makedirs(self.experiment_folder)
        if not(path.exists("data" + path.sep)):
            makedirs("data" + path.sep)
        self.experiment_list = listdir(self.experiment_folder)
        self.experiment_list_trimmed = []
        for i in self.experiment_list:
            self.experiment_list_trimmed.append(i.replace(".json", ""))
        if len(self.experiment_list_trimmed) == 0:
            self.experiment_list_trimmed = ["Empty"]

        ### Tasks
        self.task_list = ['None']
        self.participant_list = []
        self.participant_list_trimmed = []
        self.key_list = ['terminal_multiplier', 'pause_button_wait', 'terminal_feedback', 'pausetime', 'pause_instruction', 'rotation_direction']
        self.def_list = [0, 1.025, False, False, 5, "", 1]

        ### Current Experiment
        self.current_experiment = []
        self.current_experiment_name = ""
        self.highlit_experiment = ""
        self.experiment_holder = {'experiment': self.current_experiment, 'settings':{}}
        self.participant_markers = {0:[], 1:[], 2:[], 3:[]}

        ### Current Task
        self.highlit_task = ""
        self.highlit_task_num = 0
        self.min_angle_chosen = 40
        self.max_angle_chosen = 140
        self.num_trial_mult = 3
        self.num_target_chosen = 1
        self.num_trial_chosen = 1
        self.rotation_angle_chosen = 0
#        self.lag_chosen = ""
#        self.lag_chosen_err = ""
        self.num_target_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        self.rotation_angle_list = ["0" , "30", "45", "60", "75"]
        self.highlit_group = ""
        self.highlit_participant = ""

        ######################## VALID TEXT STUFF ##############################
#        self.valid_lag_text = ""
        self.valid_pause_text = ""
        self.valid_trial_num = 0

        ################### General Configuration Settings ###################
        self.general_cfg = {}
        self.FULLSCREEN = False
        self.MAX_TRIALS = 150
        self.MIN_TRIALS = 1
        self.MIN_TRIAL_BOOL = False
        self.DEFAULT_FRAME_SIZE = ((748, 649))
        self.PAUSE_FRAME_SIZE = ((566, 649))

        ######################################################################

        # Experiment stuff (column 1)
        self.Experiment_statictext = wx.StaticText(self, wx.ID_ANY, ("Experiments"))
        self.staticline_1 = wx.StaticLine(self, wx.ID_ANY, style=wx.EXPAND)
        self.experiment_settings_Button = wx.Button(self, wx.ID_ANY, "Experiment settings")
        self.exp_list_box = wx.ListBox(self, wx.ID_ANY, choices=self.experiment_list_trimmed)
        self.New_Button = wx.Button(self, wx.ID_ANY, ("New"))
        self.Delete_Button = wx.Button(self, wx.ID_ANY, ("Delete"))
        self.Load_Button = wx.Button(self, wx.ID_ANY, ("Load"))
        self.Save_Button = wx.Button(self, wx.ID_ANY, ("Save"))
        self.Run_Button = wx.Button(self, wx.ID_ANY, ("Run"))
        self.rename_experiment_button = wx.Button(self, wx.ID_ANY, ("Rename"))
        self.duplicate_experiment_Button = wx.Button(self, wx.ID_ANY, ('Duplicate'))



        # Task stuff (column 2)
        self.Task_statictext = wx.StaticText(self, wx.ID_ANY, ("Tasks"))
        self.rename_task_button = wx.Button(self, wx.ID_ANY, ("Rename"))
        self.static_line2 = wx.StaticLine(self, wx.ID_ANY, style=wx.EXPAND)
        self.task_list_box = wx.ListBox(self, wx.ID_ANY, choices=self.task_list)
        self.Plus_Button = wx.Button(self, wx.ID_ANY, ("New"))
        self.Minus_Button = wx.Button(self, wx.ID_ANY, ("Delete"))
        self.duplicate_task_Button = wx.Button(self, wx.ID_ANY, ("Duplicate"))


        # Task re-ordering (column 3)
        self.Move_Up_Button = wx.Button(self, wx.ID_ANY, (u"\u25b2"))
        self.Move_Down_Button = wx.Button(self, wx.ID_ANY, (u"\u25bc"))


        # Task settings 1 (column 4)
        self.radio_box_1 = wx.RadioBox(self, wx.ID_ANY, ("Task Type"), choices=[("Cursor"), ("No Cursor"), ("Error Clamp"), ("Pause")], majorDimension=1, style=wx.RA_SPECIFY_COLS)

        self.num_target_statictext = wx.StaticText(self, wx.ID_ANY, ("# Targets"))
        self.num_targ_CB = wx.ComboBox(self, wx.ID_ANY, value="3", choices=self.num_target_list, style=wx.CB_DROPDOWN)

        self.min_angle_statictext = wx.StaticText(self, wx.ID_ANY, ("Minimum T-Angle"))
        self.min_angle_CB = wx.Slider(self, wx.ID_ANY, minValue = 40, maxValue = 140, value = 40, style=wx.SL_HORIZONTAL | wx.SL_LABELS)

        self.max_angle_statictext = wx.StaticText(self, wx.ID_ANY, ("Maximum T-Angle"))
        self.max_angle_CB = wx.Slider(self, wx.ID_ANY, minValue = 40, maxValue = 140, value = 140, style=wx.SL_HORIZONTAL | wx.SL_LABELS)

        self.target_distance_txt = wx.StaticText(self, wx.ID_ANY, ("Target Distance %"))
        self.target_distance_slider = wx.Slider(self, wx.ID_ANY, minValue = 50, maxValue = 100, value=100, style = wx.SL_HORIZONTAL | wx.SL_LABELS)


        self.min_max_staticline = wx.StaticLine(self, wx.ID_ANY, style = wx.EXPAND)
        self.max_arrow_staticline = wx.StaticLine(self, wx.ID_ANY, style = wx.EXPAND)
        self.num_targets_staticline = wx.StaticLine(self, wx.ID_ANY, style = wx.EXPAND)
        self.num_trials_staticline = wx.StaticLine(self, wx.ID_ANY, style=wx.EXPAND)
        self.rotation_angle_staticline = wx.StaticLine(self, wx.ID_ANY, style=wx.EXPAND)
        self.rotation_change_staticline = wx.StaticLine(self, wx.ID_ANY, style=wx.EXPAND)
        self.target_distance_staticline = wx.StaticLine(self, wx.ID_ANY, style=wx.EXPAND)
#        self.group_listbox_statictext = wx.StaticText(self, wx.ID_ANY, "Group")
#        self.group_listbox_staticline = wx.StaticLine(self, wx.ID_ANY, style=wx.EXPAND)
#        self.group_listbox = wx.ListBox(self, wx.ID_ANY, choices=["Empty"])

        self.static_line_3 = wx.StaticLine(self, wx.ID_ANY, style=wx.EXPAND)


        # feedback things
        self.terminalfeedback_Radio_staticline = wx.StaticLine(self, wx.ID_ANY, style=wx.EXPAND)
#        self.max_angle_CB = wx.ComboBox(self, wx.ID_ANY, choices=[("Cursor"), ("No Cursor"), ("Error Clamp")], style=wx.CB_DROPDOWN)


        self.num_trials_statictext = wx.StaticText(self, wx.ID_ANY, ("# Trials"))
        self.num_trial_CB = wx.SpinCtrl(self, wx.ID_ANY, 'name', min=self.MIN_TRIALS, max=self.MAX_TRIALS, initial=1, style=wx.SP_ARROW_KEYS | wx.SP_WRAP)

        self.Rotation_angle_statictext = wx.StaticText(self, wx.ID_ANY, ("Rotation"))
#        self.Rotation_angle_CB = wx.ComboBox(self, wx.ID_ANY, value="0", choices=self.rotation_angle_list, style=wx.CB_DROPDOWN)
        self.Rotation_angle_slider = wx.Slider(self, wx.ID_ANY, minValue = -60, maxValue = 60, value=0, style = wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.Rotation_angle_end_statictext = wx.StaticText(self, wx.ID_ANY, ("Final rotation"))
        self.Rotation_angle_end_slider = wx.Slider(self, wx.ID_ANY, minValue = -60, maxValue = 60, value=0, style = wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.rot_change_statictext = wx.RadioBox(self, wx.ID_ANY, ("Rotation Change"), choices=[("Abrupt"), ("Gradual")], majorDimension=1, style=wx.RA_SPECIFY_COLS)
#        self.rotation_angle_direction = wx.RadioBox(self, wx.ID_ANY, ("Rotaton Direction"), choices=[("Counter-clockwise"), ("Clockwise")], majorDimension=1, style=wx.RA_SPECIFY_COLS)
        self.terminalfeedback_Radio = wx.CheckBox(self, wx.ID_ANY, ("Terminal Feedback"))
#        self.lag_static_text = wx.StaticText(self, wx.ID_ANY, (" Lag (ms)"))
#        self.lag_txt = wx.TextCtrl(self, wx.ID_ANY, ("0"))

        # pause things
        self.pause_static_text = wx.StaticText(self, wx.ID_ANY, ("Pause Time(s)"))
        self.pause_txt = wx.TextCtrl(self, wx.ID_ANY, ("0"))
        self.PM_static_text = wx.StaticText(self, wx.ID_ANY, (" Pause Message"))
        self.pause_message_txt = wx.TextCtrl(self, wx.ID_ANY, (""))
        self.pause_check = wx.CheckBox(self, wx.ID_ANY, ("Space to continue"))

        # Score Settings
        self.score_check = wx.CheckBox(self, wx.ID_ANY, ("Use Scoring System"))
        self.score_settings_button = wx.Button(self, wx.ID_ANY, ("Score Settings"))

        # Participant stuff (column 6)
        self.participants_statictext = wx.StaticText(self, wx.ID_ANY, "Participants")
        self.participants_staticline = wx.StaticLine(self, wx.ID_ANY, style = wx.EXPAND)
        self.participants_list_box = wx.ListBox(self, wx.ID_ANY, choices=["Empty"])
        self.continue_Button = wx.Button(self, wx.ID_ANY, ("Continue run"))
        self.recombine_Button = wx.Button(self, wx.ID_ANY, ("Recombine data"))
        self.preprocess_Button = wx.Button(self, wx.ID_ANY, ("Pre-Process"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.New_Press, self.New_Button)
        self.Bind(wx.EVT_BUTTON, self.Delete_Press, self.Delete_Button)
        self.Bind(wx.EVT_BUTTON, self.Load_Press, self.Load_Button)
        self.Bind(wx.EVT_BUTTON, self.Save_Press, self.Save_Button)
        self.Bind(wx.EVT_BUTTON, self.Run_Press, self.Run_Button)
        self.Bind(wx.EVT_BUTTON, self.Plus_Press, self.Plus_Button)
        self.Bind(wx.EVT_BUTTON, self.Minus_Press, self.Minus_Button)
        self.Bind(wx.EVT_RADIOBOX, self.Trial_Type_Press, self.radio_box_1)
        self.Bind(wx.EVT_BUTTON, self.experiment_settings_Button_Press, self.experiment_settings_Button)
        self.Bind(wx.EVT_BUTTON, self.continue_Button_Press, self.continue_Button)
        self.Bind(wx.EVT_BUTTON, self.recombine_Button_Press, self.recombine_Button)
        self.Bind(wx.EVT_BUTTON, self.duplicate_experiment, self.duplicate_experiment_Button)
        self.Bind(wx.EVT_BUTTON, self.duplicate_task, self.duplicate_task_Button)

        self.Bind(wx.EVT_SLIDER, self.min_angle_choose, self.min_angle_CB)
        self.Bind(wx.EVT_SLIDER, self.max_angle_choose, self.max_angle_CB)
        self.Bind(wx.EVT_SLIDER, self.target_distance_choose, self.target_distance_slider)

        self.Bind(wx.EVT_BUTTON, self.Move_Up, self.Move_Up_Button)
        self.Bind(wx.EVT_BUTTON, self.Move_Down, self.Move_Down_Button)
        self.Bind(wx.EVT_BUTTON, self.rename_experiment, self.rename_experiment_button)
        self.Bind(wx.EVT_BUTTON, self.rename_task, self.rename_task_button)
        self.Bind(wx.EVT_COMBOBOX, self.num_target_choose, self.num_targ_CB)
        self.Bind(wx.EVT_SPINCTRL, self.num_trial_choose, self.num_trial_CB)
#        self.Bind(wx.EVT_COMBOBOX, self.rot_angle_choose, self.Rotation_angle_CB)
        self.Bind(wx.EVT_SLIDER, self.rot_angle_choose, self.Rotation_angle_slider)
        self.Bind(wx.EVT_SLIDER, self.rot_angle_end_choose, self.Rotation_angle_end_slider)

        self.Bind(wx.EVT_RADIOBOX, self.Rot_Change_Press, self.rot_change_statictext)
#        self.Bind(wx.EVT_RADIOBOX, self.rotation_angle_direction_press, self.rotation_angle_direction)
#        self.Bind(wx.EVT_TEXT, self.Lag_Enter, self.lag_txt)
        self.Bind(wx.EVT_CHECKBOX, self.terminalfeedback_check_press, self.terminalfeedback_Radio)
        ### Pause events
        self.Bind(wx.EVT_TEXT, self.Pause_Enter, self.pause_txt)
        self.Bind(wx.EVT_TEXT, self.pause_message_make, self.pause_message_txt)
        self.Bind(wx.EVT_CHECKBOX, self.pause_check_press, self.pause_check)
        ### Experiment List Box Events
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.list_box_dclick, self.exp_list_box)
        self.Bind(wx.EVT_LISTBOX, self.list_box_click, self.exp_list_box)
        ### Task List Box Events
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.task_list_box_dclick, self.task_list_box)
        self.Bind(wx.EVT_LISTBOX, self.task_list_box_click, self.task_list_box)
        self.Bind(wx.EVT_BUTTON, self.preprocess_press, self.preprocess_Button)
        self.Bind(wx.EVT_LISTBOX, self.participants_list_box_click, self.participants_list_box)

        # Scoring System Events
        self.Bind(wx.EVT_CHECKBOX, self.score_check_press, self.score_check)
        self.Bind(wx.EVT_BUTTON, self.score_settings_press, self.score_settings_button)
#        self.Bind(wx.EVT_LISTBOX, self.group_listbox_click, self.group_listbox)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties

        self.SetTitle(("PyVMEC"))
#        self.SetSize((798, 462)) ## Set size to this when Pause is selected
        #self.SetSize(self.DEFAULT_FRAME_SIZE)

        # Experiment stuff
        self.Experiment_statictext.SetMinSize((70, 17))
        self.staticline_1.SetMinSize((175, 1))

        self.experiment_settings_Button.SetMinSize((175, 29))

        self.exp_list_box.SetMinSize((175, 250)) ################################
        self.exp_list_box.SetSelection(0)

        # row one of buttons:
        self.New_Button.SetMinSize((55, 29))
        self.rename_experiment_button.SetMinSize((55, 29))
        self.Delete_Button.SetMinSize((55, 29))

        # row two of buttons:
        self.duplicate_experiment_Button.SetMinSize((175, 29))


        # row tree:
        self.Load_Button.SetMinSize((85, 29))
        self.Save_Button.SetMinSize((85, 29))

        # row four:
        self.Run_Button.SetMinSize((175, 29))



        # Participant stuff
        self.participants_list_box.SetMinSize((175,350)) #################################
        self.participants_list_box.SetSelection(0)
        self.participants_staticline.SetMinSize((175, 1))
        self.continue_Button.SetMinSize((175, 29))
        self.continue_Button.Disable()
        self.recombine_Button.SetMinSize((175, 29))
        self.recombine_Button.Disable()
        self.preprocess_Button.SetMinSize((175, 29))


        # Task list stuff
        self.task_list_box.SetMinSize((175, 320))   ##############################################
        self.task_list_box.SetSelection(0)


        # first button row:
        self.Plus_Button.SetMinSize((55, 29))
        self.rename_task_button.SetMinSize((55, 29))
        self.Minus_Button.SetMinSize((55, 29))

        # second row:
        self.duplicate_task_Button.SetMinSize((175, 29))


        # Task properties panels stuff
#        self.group_listbox_staticline.SetMinSize((175, 22))
        self.static_line2.SetMinSize((175, 1))
        self.min_max_staticline.SetMinSize((175, 1))
        self.static_line_3.SetMinSize((175, 22))
        self.max_arrow_staticline.SetMinSize((175, 1))
        self.num_targets_staticline.SetMinSize((175, 1))
        self.num_trials_staticline.SetMinSize((175, 1))
        self.rotation_angle_staticline.SetMinSize((175, 1))
        self.rotation_change_staticline.SetMinSize((175, 1))
        self.terminalfeedback_Radio_staticline.SetMinSize((175, 1))

        self.Rotation_angle_end_slider.Disable()
        self.Rotation_angle_end_statictext.Disable()

#        self.group_listbox.SetMinSize((175,166))
        self.radio_box_1.SetSelection(0)
        self.Move_Up_Button.SetMinSize((30, 30))
        self.Move_Down_Button.SetMinSize((30, 30))
        self.num_targ_CB.SetMinSize((175, 29))
        self.num_targ_CB.SetSelection(-1)
#        self.num_trial_CB.SetSelection(-1)
#        self.Rotation_angle_CB.SetSelection(-1)
        self.rot_change_statictext.SetSelection(0)
        self.num_trial_CB.SetMinSize((175,29))

        ### Pause stuff
        self.pause_txt.SetMinSize((175,29))
        self.pause_message_txt.SetMinSize((175,29))

        # Scoring System
        self.score_settings_button.SetMinSize((175, 29))
        self.score_settings_button.Disable()

        # end wxGlade



    def __do_layout(self):
#        # begin wxGlade: MyFrame.__do_layout

        # 0, wx.EXPAND | wx.ALL, 5

        ### FIRST COLUMN IN GUI

        # has load/save buttons for experiments
        sizer_13 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_13.Add(self.Load_Button, 0, wx.EXPAND | wx.ALL, 3)
        sizer_13.Add(self.Save_Button, 0, wx.EXPAND | wx.ALL, 3)

        # has load/save buttons + the run button below it
        sizer_12 = wx.BoxSizer(wx.VERTICAL)
        sizer_12.Add(sizer_13, 0, wx.EXPAND | wx.ALL, 0)
        sizer_12.Add(self.Run_Button, 0, wx.EXPAND | wx.ALL, 3)

        # has new / rename / delete buttons (for experiments?)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)

        sizer_5a = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5a.Add(self.New_Button, 0, wx.EXPAND | wx.ALL, 3)
        sizer_5a.Add(self.rename_experiment_button, 0, wx.EXPAND | wx.ALL, 3)
        sizer_5a.Add(self.Delete_Button, 0, wx.EXPAND | wx.ALL, 3)


        sizer_5.Add(sizer_5a, 0, 0, 0)
        sizer_5.Add(self.duplicate_experiment_Button, 0, wx.EXPAND | wx.ALL, 3)

        # is this the sizer that has all the list of experiments?
        sizer_2 = wx.BoxSizer(wx.VERTICAL)

        # add some pre-defined buttons / lists
        sizer_2.Add(self.Experiment_statictext, 0, wx.EXPAND | wx.ALL, 3)
        sizer_2.Add(self.staticline_1, 0, wx.EXPAND | wx.BOTTOM, 0)
        sizer_2.Add(self.experiment_settings_Button, 0, wx.EXPAND | wx.RIGHT, 3)
        sizer_2.Add(self.exp_list_box, 0, wx.EXPAND | wx.RIGHT, 3)

        # add new / rename / delete and duplicate buttons
        sizer_2.Add(sizer_5, 0, wx.EXPAND | wx.ALL, 0)

        # add run sizer with run button
        sizer_2.Add(sizer_12, 0, wx.EXPAND | wx.ALL, 0)


        ### SECOND COLUMN IN GUI

        # is this the sizer with the task and participant list?
        sizer_3 = wx.BoxSizer(wx.VERTICAL)

        sizer_3.Add(self.Task_statictext, 0, wx.EXPAND | wx.ALL, 3)
        sizer_3.Add(self.static_line2, 0, wx.EXPAND | wx.BOTTOM, 0)
        sizer_3.Add(self.task_list_box, 0, wx.EXPAND | wx.LEFT, 3)

        # sizer for new / rename / delete task buttons
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(self.Plus_Button, 0, wx.EXPAND | wx.ALL, 3)
        sizer_4.Add(self.rename_task_button, 0, wx.EXPAND | wx.ALL, 3)
        sizer_4.Add(self.Minus_Button, 0, wx.EXPAND | wx.ALL, 3)
        sizer_3.Add(sizer_4, 0, wx.EXPAND | wx.ALL, 0)
        # also add duplicate button for tasks:
        sizer_3.Add(self.duplicate_task_Button, 0, wx.EXPAND | wx.ALL, 3)


        # THIRD COLUMN for GUI:

        # sizer for task up/down arrows
        sizer_task_arrows = wx.BoxSizer(wx.VERTICAL)
        sizer_task_arrows.Add(self.Move_Up_Button, 0, 45 | wx.ALL, 3)
        sizer_task_arrows.Add(self.Move_Down_Button, 0, 45 | wx.ALL, 3)


        # FOURTH COLUMN for GUI:
        # first column with task settings
        sizer_10 = wx.BoxSizer(wx.VERTICAL)

        sizer_10.Add(self.radio_box_1, 0, wx.EXPAND | wx.ALL, 3)
        sizer_10.Add(self.static_line_3, 0, wx.EXPAND | wx.ALL, 5)

        target_sizer = wx.BoxSizer(wx.VERTICAL)

        target_sizer.Add(self.num_target_statictext, 0, wx.EXPAND | wx.LEFT, 3)
        target_sizer.Add(self.num_targ_CB, 0, wx.EXPAND | wx.LEFT, 3)

        target_sizer.Add(self.min_angle_statictext, 0, wx.EXPAND | wx.ALL, 3)
        target_sizer.Add(self.min_angle_CB, 0, wx.EXPAND, 3)
        #sizer_10.Add(self.min_max_staticline, 0, wx.EXPAND | wx.BOTTOM, 0)
        target_sizer.Add(self.max_angle_statictext, 0, wx.EXPAND | wx.ALL, 3)
        target_sizer.Add(self.max_angle_CB, 0, wx.EXPAND | wx.ALL, 3)
        #sizer_10.Add(self.max_arrow_staticline, 0, wx.EXPAND | wx.ALL, 0)
        target_sizer.Add(self.target_distance_txt, 0, wx.EXPAND | wx.ALL, 3)
        target_sizer.Add(self.target_distance_slider, 0, wx.EXPAND | wx.ALL, 3)
        #sizer_10.Add(self.target_distance_staticline, 0, wx.EXPAND | wx.ALL, 3)

        sizer_10.Add(target_sizer, 0, wx.EXPAND, 0)

        # Add pause task stuff here?
        #sizer_10.Add(self.pause_static_text, 0, 0, 0)
        #sizer_10.Add(self.pause_txt, 0, 0, 0)
        #sizer_10.Add(self.PM_static_text, 0, 0, 0)
        #sizer_10.Add(self.pause_message_txt, 0, 0, 0)
        #sizer_10.Add(self.pause_check, 0, 0, 0)


        # FIFTH COLUMN in GUI?
        feedback_sizer = wx.BoxSizer(wx.VERTICAL)
        #sizer_9.Add(self.num_target_statictext, 0, wx.EXPAND | wx.LEFT, 3)
        #sizer_9.Add(self.num_targ_CB, 0, wx.EXPAND | wx.LEFT, 3)
        #sizer_9.Add(self.num_targets_staticline, 0, wx.EXPAND | wx.BOTTOM, 0)
        feedback_sizer.Add(self.num_trials_statictext, 0, wx.EXPAND | wx.LEFT, 3)
        feedback_sizer.Add(self.num_trial_CB, 0, wx.EXPAND | wx.LEFT, 3)
        #sizer_9.Add(self.num_trials_staticline, 0, wx.EXPAND | wx.BOTTOM, 0)
        feedback_sizer.Add(self.Rotation_angle_statictext, 0, wx.EXPAND | wx.LEFT, 3)
        feedback_sizer.Add(self.Rotation_angle_slider, 0, wx.EXPAND | wx.ALL, 3)
        feedback_sizer.Add(self.Rotation_angle_end_statictext, 0, wx.EXPAND | wx.LEFT, 3)
        feedback_sizer.Add(self.Rotation_angle_end_slider, 0, wx.EXPAND | wx.ALL, 3)
        #sizer_9.Add(self.rotation_angle_staticline, 0, wx.EXPAND | wx.ALL, 0)
#        sizer_9.Add(self.rotation_angle_direction, 0, wx.LEFT, 2)
        feedback_sizer.Add(self.rot_change_statictext, 0, wx.EXPAND | wx.LEFT, 3)
        #sizer_9.Add(self.rotation_change_staticline, 0, wx.EXPAND | wx.BOTTOM, 0)
#        sizer_9.Add(self.lag_static_text, 0, wx.LEFT, 2)
#        sizer_9.Add(self.lag_txt, 0, wx.LEFT, 2)
        #sizer_9.Add(self.terminalfeedback_Radio_staticline, 0, wx.EXPAND | wx.BOTTOM, 0)
        feedback_sizer.Add(self.terminalfeedback_Radio, 0, wx.EXPAND | wx.LEFT, 3)

        pause_sizer = wx.BoxSizer(wx.VERTICAL)
        # Add pause task stuff here?
        pause_sizer.Add(self.pause_static_text, 0, 0, 0)
        pause_sizer.Add(self.pause_txt, 0, 0, 0)
        pause_sizer.Add(self.PM_static_text, 0, 0, 0)
        pause_sizer.Add(self.pause_message_txt, 0, 0, 0)
        pause_sizer.Add(self.pause_check, 0, 0, 0)

        # Score System
        score_sizer = wx.BoxSizer(wx.VERTICAL)
        score_sizer.Add(self.score_check, 0, 0, 0)
        score_sizer.Add(self.score_settings_button, 0, 0, 0)

        sizer_9 = wx.BoxSizer(wx.VERTICAL)
        sizer_9.Add(feedback_sizer, 0, wx.EXPAND, 0)
        sizer_9.Add(pause_sizer, 0, wx.EXPAND, 0)
        sizer_9.Add(score_sizer, 0, wx.EXPAND, 0)

        # combine both task setting columns into 1 sizer?
        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8.Add(sizer_10, 0, wx.EXPAND | wx.ALL, 0)
        sizer_8.Add(sizer_9, 0, wx.EXPAND | wx.ALL, 0)


        # lag settings (invisible for now):
        sizer_7 = wx.BoxSizer(wx.VERTICAL)
#        sizer_7.Add(self.lag_static_text, 0, 0, 0)
#        sizer_7.Add(self.lag_txt, 0, 0, 0)

        # sizer with nothing?
        sizer_11 = wx.BoxSizer(wx.VERTICAL)

        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_7, 0, wx.EXPAND | wx.ALL, 0)
        sizer_6.Add(sizer_11, 0, wx.EXPAND | wx.ALL, 0)


        # new sizer for participant list and pre-processing button:
        participant_sizer = wx.BoxSizer(wx.VERTICAL)

        participant_sizer.Add(self.participants_staticline, 0, wx.EXPAND | wx.BOTTOM, 0)
        participant_sizer.Add(self.participants_statictext, 0, wx.EXPAND | wx.ALL, 3)
        participant_sizer.Add(self.participants_list_box, 0, wx.EXPAND | wx.RIGHT, 3)
        participant_sizer.Add(self.continue_Button, 0, wx.EXPAND | wx.RIGHT, 3)
        participant_sizer.Add(self.recombine_Button, 0, wx.EXPAND | wx.RIGHT, 3)

        # maybe there should be a divider here, or some static text?

        # add pre-process button here too
        participant_sizer.Add(self.preprocess_Button, 0, wx.EXPAND | wx.RIGHT, 3)


        # is this the main sizer, containing the 4 or 5 columns of the GUI?
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        # add first column to main GUI (experiment buttons and list)
        sizer_1.Add(sizer_2, 1, 0, 0)
        # add second column to main GUI (task buttons and list.. and for now the participant list plus buttons)
        sizer_1.Add(sizer_3, 1, 0, 0)
        # add task re-orderinf buttons:
        sizer_1.Add(sizer_task_arrows, 0, 0, 0)
        # add both task settings columns?
        sizer_1.Add(sizer_8, 2, wx.LEFT, 10)

        sizer_1.Add(sizer_6, 1, 0, 0) # this can probably be left out...

        sizer_1.Add(participant_sizer, 1, 0, 0)

        sizer_1.Fit (self)

        self.SetSizer(sizer_1)
        self.Layout()

        # Now hide the Pause stuff?
        #self.pause_static_text.Hide()
        #self.pause_txt.Hide()
        #self.PM_static_text.Hide()
        #self.pause_message_txt.Hide()
        #self.pause_check.Hide()

        self.pause_static_text.Enable(False)
        self.pause_txt.Enable(False)
        self.PM_static_text.Enable(False)
        self.pause_message_txt.Enable(False)
        self.pause_check.Enable(False)

        #for widget in pause_sizer.GetChildren():
        #    widget.Enable(False)



    def regular_experiment_show(self):
        ### Right most widgets ###
        #self.num_target_statictext.Show()
        #self.num_targ_CB.Show()
        #self.num_targets_staticline.Show()
        #self.num_trials_statictext.Show()
        #self.num_trial_CB.Show()
        #self.num_trials_staticline.Show()
        #self.Rotation_angle_statictext.Show()
        #self.Rotation_angle_slider.Show()
        #self.Rotation_angle_end_statictext.Show()
        #self.Rotation_angle_end_slider.Show()

        #self.rotation_angle_staticline.Show()
        #self.rot_change_statictext.Show()
        #self.rotation_change_staticline.Show()


        self.num_target_statictext.Enable(True)
        self.num_targ_CB.Enable(True)
        self.num_targets_staticline.Enable(True)
        self.num_trials_statictext.Enable(True)
        self.num_trial_CB.Enable(True)
        self.num_trials_staticline.Enable(True)
        self.Rotation_angle_statictext.Enable(True)
        self.Rotation_angle_slider.Enable(True)
        self.Rotation_angle_end_statictext.Enable(True)
        self.Rotation_angle_end_slider.Enable(True)

        self.rotation_angle_staticline.Enable(True)
        self.rot_change_statictext.Enable(True)
        self.rotation_change_staticline.Enable(True)

#        self.lag_static_text.Show()
#        self.lag_txt.Show()
        ###########
        #self.min_angle_CB.Show()
        #self.min_angle_statictext.Show()
        #self.min_max_staticline.Show()
        #self.max_angle_CB.Show()
        #self.max_angle_statictext.Show()
        #self.max_arrow_staticline.Show()
        #self.target_distance_slider.Show()
        #self.target_distance_txt.Show()
        #self.terminalfeedback_Radio.Show()
        #self.terminalfeedback_Radio_staticline.Show()


        self.min_angle_CB.Enable(True)
        self.min_angle_statictext.Enable(True)
        self.min_max_staticline.Enable(True)
        self.max_angle_CB.Enable(True)
        self.max_angle_statictext.Enable(True)
        self.max_arrow_staticline.Enable(True)
        self.target_distance_slider.Enable(True)
        self.target_distance_txt.Enable(True)
        self.terminalfeedback_Radio.Enable(True)
        self.terminalfeedback_Radio_staticline.Enable(True)
#        self.rotation_angle_direction.Show()
        ### Show ###
        if (self.current_experiment[self.highlit_task_num]['trial_type'] == 'no_cursor'):
#            self.Rotation_angle_statictext.Hide()
#            self.Rotation_angle_slider.Hide()
#            self.rotation_angle_staticline.Hide()
##            self.rotation_angle_direction.Hide()
#            self.lag_static_text.Hide()
#            self.lag_txt.Hide()


            #self.rot_change_statictext.Hide()
            #self.rotation_change_staticline.Hide()
            #self.terminalfeedback_Radio.Hide()
            #self.terminalfeedback_Radio_staticline.Hide()

            self.rot_change_statictext.Enable(False)
            self.rotation_change_staticline.Enable(False)
            self.terminalfeedback_Radio.Enable(False)
            self.terminalfeedback_Radio_staticline.Enable(False)

        #self.pause_static_text.Hide()
        #self.pause_txt.Hide()
        #self.PM_static_text.Hide()
        #self.pause_message_txt.Hide()
        #self.pause_check.Hide()

        #self.SetSize(self.DEFAULT_FRAME_SIZE)

        self.pause_static_text.Enable(False)
        self.pause_txt.Enable(False)
        self.PM_static_text.Enable(False)
        self.pause_message_txt.Enable(False)
        self.pause_check.Enable(False)

        # Scoring System
        self.score_check.Enable(True)
        self.score_settings_button.Enable(self.score_check.GetValue())


    def pause_experiment_show(self):
        ### Right most widgets ###
        #self.num_target_statictext.Hide()
        #self.num_targ_CB.Hide()
        #self.num_targets_staticline.Hide()
        #self.num_trials_statictext.Hide()
        #self.num_trial_CB.Hide()
        #self.num_trials_staticline.Hide()
        #self.Rotation_angle_statictext.Hide()
        #self.Rotation_angle_slider.Hide()
        #self.rotation_angle_staticline.Hide()
        #self.rot_change_statictext.Hide()
        #self.rotation_change_staticline.Hide()
#        self.lag_static_text.Hide()
#        self.lag_txt.Hide()
        ###
        #self.Rotation_angle_end_statictext.Hide()
        #self.Rotation_angle_end_slider.Hide()
        #self.min_angle_CB.Hide()
        #self.min_angle_statictext.Hide()
        #self.min_max_staticline.Hide()
        #self.max_angle_CB.Hide()
        #self.max_angle_statictext.Hide()
        #self.max_arrow_staticline.Hide()
        #self.target_distance_slider.Hide()
        #self.target_distance_txt.Hide()
        #self.terminalfeedback_Radio.Hide()
        #self.terminalfeedback_Radio_staticline.Hide()
#        self.rotation_angle_direction.Hide()
        ### Show ###
        #self.pause_static_text.Show()
        #self.pause_txt.Show()
        #self.PM_static_text.Show()
        #self.pause_message_txt.Show()
        #self.pause_check.Show()
        #self.SetSize(self.PAUSE_FRAME_SIZE)


        self.num_target_statictext.Enable(False)
        self.num_targ_CB.Enable(False)
        self.num_targets_staticline.Enable(False)
        self.num_trials_statictext.Enable(False)
        self.num_trial_CB.Enable(False)
        self.num_trials_staticline.Enable(False)
        self.Rotation_angle_statictext.Enable(False)
        self.Rotation_angle_slider.Enable(False)
        self.rotation_angle_staticline.Enable(False)
        self.rot_change_statictext.Enable(False)
        self.rotation_change_staticline.Enable(False)
        self.Rotation_angle_end_statictext.Enable(False)
        self.Rotation_angle_end_slider.Enable(False)
        self.min_angle_CB.Enable(False)
        self.min_angle_statictext.Enable(False)
        self.min_max_staticline.Enable(False)
        self.max_angle_CB.Enable(False)
        self.max_angle_statictext.Enable(False)
        self.max_arrow_staticline.Enable(False)
        self.target_distance_slider.Enable(False)
        self.target_distance_txt.Enable(False)
        self.terminalfeedback_Radio.Enable(False)
        self.terminalfeedback_Radio_staticline.Enable(False)

        self.pause_static_text.Enable(True)
        self.pause_txt.Enable(True)
        self.PM_static_text.Enable(True)
        self.pause_message_txt.Enable(True)
        self.pause_check.Enable(True)

        # Scoring System
        self.score_check.Enable(False)
        self.score_settings_button.Enable(False)


    def list_box_dclick(self, event):

        experimentFolder = self.highlit_experiment
        self.current_experiment_name = event.GetString()
        with open(self.experiment_folder + self.current_experiment_name + ".json", "rb") as f:
            self.experiment_holder = load(f)
            del self.task_list[:]
        self.current_experiment = self.experiment_holder['experiment']
        for i in range (0, len(self.current_experiment)):
            self.task_list.append(self.current_experiment[i]["task_name"])
        if len(self.task_list) == 0:
            self.task_list_box.Set(['Empty'])
        else:
            self.task_list_box.Set(self.task_list)
        #### REFRESH PARTICIPANT LIST #####
        if not(path.exists(path.join("data", experimentFolder))):
            makedirs(path.join("data",experimentFolder))
        self.participant_list = listdir(path.join("data", self.current_experiment_name))
        self.participant_list = [x for x in self.participant_list if ".csv" not in x]
        for i in self.participant_list:
            self.participant_list_trimmed.append(i.replace(".csv", ""))
        if len(self.participant_list_trimmed) == 0:
            self.participant_list_trimmed = ["Empty"]
        self.participant_markers = {0:[], 1:[], 2:[], 3:[]}
        self.generate_participant_markers()
        marked_participants = self.mark_participants()
        self.participants_list_box.Set(marked_participants)
        del self.participant_list_trimmed[:]
        #### CHECK IF ANY TASKS ####
        if len(self.experiment_holder['experiment']) > 0:
            self.Run_Button.Enable()
        else:
            self.Run_Button.Disable()
        event.Skip()

    def list_box_click(self, event):
        self.highlit_experiment = event.GetString() ## The highlighted experiment
        event.Skip()

    def task_list_box_click(self, event):
        self.highlit_task = event.GetString()
        self.highlit_task_num = event.GetSelection()
        try:
             #### CHECK JSON KEYS AND FILL MISSING KEYS WITH DEFAULTS ####
            for task in self.experiment_holder['experiment']:
                for idx, key, in enumerate(self.key_list):
                    if key in task.keys():
                        continue
                    else:
                        task[key] = self.def_list[idx]
            ### Trial number stuff
            self.valid_trial_num = self.current_experiment[self.highlit_task_num]['num_trials']
            if self.current_experiment[self.highlit_task_num]['num_targets'] > 2:
                self.num_trial_mult = self.current_experiment[self.highlit_task_num]['num_targets']
            elif self.current_experiment[self.highlit_task_num]['num_targets'] == 1:
                self.num_trial_mult = 3
            elif self.current_experiment[self.highlit_task_num]['num_targets'] == 2:
                self.num_trial_mult = 4
            ### Set Current Task Settings
            self.radio_box_1.SetSelection(exp.task_num(self.current_experiment[self.highlit_task_num]['trial_type'], True))
            self.num_trial_CB.SetValue(self.current_experiment[self.highlit_task_num]['num_trials'])
            self.num_targ_CB.SetStringSelection(str(self.current_experiment[self.highlit_task_num]['num_targets']))
            self.terminalfeedback_Radio.SetValue(self.current_experiment[self.highlit_task_num]['terminal_feedback'])
            self.target_distance_slider.SetValue(self.current_experiment[self.highlit_task_num]['target_distance_ratio']*100)
            self.rot_change_statictext.SetSelection(exp.rotation_num(self.current_experiment[self.highlit_task_num]['rotation_change_type'], True))
            self.Rotation_angle_slider.SetValue(self.current_experiment[self.highlit_task_num]['rotation_angle'])
            self.Rotation_angle_end_slider.SetValue(self.current_experiment[self.highlit_task_num]['final_rotation_angle'])
#            self.rotation_angle_direction.SetSelection(exp.rotation_direction_num(self.current_experiment[self.highlit_task_num]['rotation_angle_direction'], True))
            self.pause_check.SetValue(self.current_experiment[self.highlit_task_num]['pause_button_wait'])
            self.pause_txt.SetValue(str(self.current_experiment[self.highlit_task_num]['pausetime']))
            self.pause_message_txt.SetValue(self.current_experiment[self.highlit_task_num]['pause_instruction'])

            # Scoring System
            self.score_check.SetValue(self.current_experiment[self.highlit_task_num]['use_score'])


            if (self.current_experiment[self.highlit_task_num]['rotation_change_type'] == 'gradual'):
#                self.MIN_TRIAL_BOOL = True
                self.Rotation_angle_statictext.SetLabel("Initial rotation")
                self.Rotation_angle_end_statictext.Enable()
                self.Rotation_angle_end_slider.Enable()
            elif (self.current_experiment[self.highlit_task_num]['rotation_change_type'] == 'abrupt'):
                self.Rotation_angle_statictext.SetLabel("Rotation")
                self.Rotation_angle_end_slider.Disable()
                self.Rotation_angle_end_statictext.Disable()
            # Show or hide Pause menu
            if self.experiment_holder['experiment'][self.highlit_task_num]['trial_type'] == "pause":
                self.pause_experiment_show()
                try:
                    self.pause_txt.SetValue(str(self.current_experiment[self.highlit_task_num]['pausetime']))
                    self.pause_message_txt.SetValue(self.current_experiment[self.highlit_task_num]['pause_instruction'])
                except:
                    self.pause_txt.SetValue('3')
                    self.pause_message_txt.SetValue('')
            else:
                self.regular_experiment_show()

            self.min_angle_CB.SetValue(self.current_experiment[self.highlit_task_num]['min_angle'])
            self.max_angle_CB.SetValue(self.current_experiment[self.highlit_task_num]['max_angle'])
            try:
#                self.lag_txt.SetValue(str(self.current_experiment[self.highlit_task_num]['lag_value']))
                pass
            except:
                pass
#                self.lag_txt.SetValue("0")
        except Exception as e:
            print traceback.print_exc()
        event.Skip()

    def task_list_box_dclick(self, event):
        dlg = wx.TextEntryDialog(self, 'Change Task Name', 'Rename')
        dlg.SetValue("")
        if dlg.ShowModal() == wx.ID_OK:
            self.current_experiment[self.highlit_task_num]["task_name"] = dlg.GetValue()
        del self.task_list[:]
        for i in range (0, len(self.current_experiment)):
            self.task_list.append(self.current_experiment[i]['task_name'])
        self.task_list_box.Set(self.task_list)
        dlg.Destroy()
        event.Skip()

    def New_Press(self, event):  # wxGlade: MyFrame.<event_handler>
        dlg = wx.TextEntryDialog(self, 'Enter Name', 'Create new experiment')
        dlg.SetValue("")

        if listdir(self.experiment_folder) == []:
            del self.experiment_list_trimmed[:]
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.GetValue() in self.experiment_list_trimmed:
                dlg_warning = wx.MessageDialog(self, "Experiment already exists!", style=wx.OK|wx.CENTRE|wx.ICON_WARNING)
                dlg_warning.ShowModal()
                dlg_warning.Destroy()
                return
            new_experiment = []
            self.experiment_holder = {"experiment":[], "settings":{}}
            experimentFolder = dlg.GetValue()
            self.highlit_experiment = dlg.GetValue()
            with open(self.experiment_folder + dlg.GetValue() + ".json", "wb") as f:
                dump(new_experiment, f)
            f.close()
            self.experiment_list_trimmed.append(dlg.GetValue())
            self.exp_list_box.Set(self.experiment_list_trimmed)
            self.exp_list_box.SetSelection(len(self.experiment_list_trimmed) - 1)
            self.current_experiment_name = dlg.GetValue()
            with open(self.experiment_folder + self.current_experiment_name + ".json", "rb") as f:
                self.current_experiment = load(f)
                del self.task_list[:]
            self.task_list_box.Set(["Empty"])
            self.experiment_holder['settings']['fullscreen'] = False
            self.experiment_holder['settings']['flipscreen'] = False
            self.experiment_holder['settings']['viewscale'] = [1.00,1.00]
            self.experiment_holder['settings']['waitblanking'] = True
            self.experiment_holder['settings']['return_movement'] = False
            self.experiment_holder['settings']['custom_target_enable'] = False
            self.experiment_holder['settings']['custom_target_file'] = ""
            self.experiment_holder['settings']['custom_cursor_enable'] = False
            self.experiment_holder['settings']['custom_cursor_file'] = ""
            self.experiment_holder['settings']['custom_home_enable'] = False
            self.experiment_holder['settings']['custom_home_file'] = ""
            self.experiment_holder['settings']['custom_stim_enable'] = False
            self.experiment_holder['settings']['custom_stim_file'] = ""
            self.experiment_holder['settings']['experiment_folder'] =  dlg.GetValue()
            self.experiment_holder['settings']['screen'] = 0
            with open(self.experiment_folder + dlg.GetValue() + ".json", "wb") as f:
                dump(self.experiment_holder, f)
            f.close()
            if not(path.exists(path.join("data", experimentFolder))):
                makedirs(path.join("data",experimentFolder))
        dlg.Destroy()
        event.Skip()

    def Delete_Press(self, event):  # wxGlade: MyFrame.<event_handler>
        dlg = wx.MessageDialog(self, 'Confirm Deleting \"%s\"?\n' % self.highlit_experiment,
                               'Delete Confirmation')
        if dlg.ShowModal() == wx.ID_OK:
            remove(self.experiment_folder + self.highlit_experiment + ".json")
            self.experiment_list_trimmed.remove(self.highlit_experiment)
            if listdir(self.experiment_folder) == []:
                self.experiment_list_trimmed = ["Empty"]
            self.exp_list_box.Set(self.experiment_list_trimmed)
        dlg.Destroy()
        event.Skip()

    def Load_Press(self, event):  # wxGlade: MyFrame.<event_handler>
        experimentFolder = self.highlit_experiment
        self.current_experiment_name = self.highlit_experiment
        with open(self.experiment_folder + self.current_experiment_name + ".json", "rb") as f:
            self.experiment_holder = load(f)
            del self.task_list[:]
        self.current_experiment = self.experiment_holder['experiment']
        for i in range (0, len(self.current_experiment)):
            self.task_list.append(self.current_experiment[i]["task_name"])
        if len(self.task_list) == 0:
            self.task_list_box.Set(['Empty'])
        else:
            self.task_list_box.Set(self.task_list)
        #### REFRESH PARTICIPANT LIST #####
        if not(path.exists(path.join("data", experimentFolder))):
            makedirs(path.join("data",experimentFolder))
        self.participant_list = listdir(path.join("data", self.current_experiment_name))
        self.participant_list = [x for x in self.participant_list if ".csv" not in x]
        for i in self.participant_list:
            self.participant_list_trimmed.append(i.replace(".csv", ""))
        if len(self.participant_list_trimmed) == 0:
            self.participant_list_trimmed = ["Empty"]
        self.participant_markers = {0:[], 1:[], 2:[], 3:[]}
        self.generate_participant_markers()
        #### MARKERS TO PARTICIPANT LIST ####
        marked_participants = self.mark_participants()
        self.participants_list_box.Set(marked_participants)
        del self.participant_list_trimmed[:]
        #### CHECK IF ANY TASKS ####
        if len(self.experiment_holder['experiment']) > 0:
            self.Run_Button.Enable()
        else:
            self.Run_Button.Disable()
        event.Skip()

    def mark_participants(self):
        ### DOESN'T WORK IN WXPYTHON GUI ###
        marked_participant_list = []
        for participant in self.participant_list_trimmed:
            if participant in self.participant_markers[1]:
                marked_participant_list.append("[" + participant + "]")
            elif (participant in self.participant_markers[2]) or (participant in self.participant_markers[3]):
#               marked_participant_list.append("~" + participant + "~")
                continue
            else:
                marked_participant_list.append(participant)
        return marked_participant_list

    def unmark_participant(self, participant):
        unmarked = participant
        unmarked = unmarked.replace("~", "")
        unmarked = unmarked.replace("[", "")
        unmarked = unmarked.replace("]", "")
        return unmarked
    def Save_Press(self, event):
        dlg = wx.MessageDialog(self, "Save Experiment?", style=wx.CENTRE|wx.ICON_QUESTION|wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            with open(self.experiment_folder+self.current_experiment_name+".json", "wb") as f:
                dump(self.experiment_holder, f)
                f.close()
        dlg.Destroy()
        event.Skip()

    def Run_Press(self, event):  # wxGlade: MyFrame.<event_handle
        dlg = wx.TextEntryDialog(self, 'Enter name', 'Participant')
        dlg.SetValue("")
        experimentFolder = self.current_experiment_name
        self.Run_Button.Disable()
        if dlg.ShowModal() ==wx.ID_OK:
            if (path.exists("data"+path.sep + experimentFolder + path.sep + dlg.GetValue())):
                self.Run_Button.Enable()
                dlg2 = wx.MessageDialog(self, "Participant already exists!", style=wx.OK|wx.CENTRE|wx.ICON_WARNING)
                dlg2.ShowModal()
                dlg2.Destroy()
                return
            if not(path.exists(path.join("data", experimentFolder, dlg.GetValue()))):
                makedirs(path.join("data", experimentFolder, dlg.GetValue()))
            try:
                #### CHECK JSON KEYS AND FILL MISSING KEYS WITH DEFAULTS ####
                for task in self.experiment_holder['experiment']:
                    for idx, key, in enumerate(self.key_list):
                        if key in task.keys():
                            continue
                        else:
                            task[key] = self.def_list[idx]
                    if task['rotation_angle'] < 0:
                        task['rotation_direction'] = -1
                    else:
                        task['rotation_direction'] = 1
                participant = dlg.GetValue()
                with open(self.experiment_folder+self.current_experiment_name+".json", "wb") as f:
                    dump(self.experiment_holder, f)
                    f.close()
                #### Write Current Json into Participant Folder ####
                with open(path.join("data", self.current_experiment_name, participant, self.current_experiment_name + ".json"), "wb" ) as f:
                    dump(self.experiment_holder, f)
                    f.close()
                self.experiment_run = exp.run_experiment(participant, self.experiment_holder)
                if (len(self.experiment_run) != 0):
                    self.experiment_run.to_csv(path_or_buf = path.join("data", experimentFolder, dlg.GetValue(), dlg.GetValue() + "_COMPLETE.csv"), index=False)
            except Exception as e:
                self.Run_Button.Enable()
                print traceback.print_exc()
#                dlg3 = wx.MessageDialog(self, 'No experiment selected!', style=wx.OK|wx.CENTRE|wx.ICON_WARNING)
#                dlg3.ShowModal()
#                dlg3.Destroy()
                return
        else:
            self.Run_Button.Enable()
            pass
        #### REFRESH PARTICIPANT LIST #####
        if not(path.exists(path.join("data", experimentFolder))):
            makedirs(path.join("data", experimentFolder))
        self.participant_list = listdir(path.join("data", self.current_experiment_name))
        self.participant_list = [x for x in self.participant_list if ".csv" not in x]
        for i in self.participant_list:
            self.participant_list_trimmed.append(i.replace(".csv", ""))
        if len(self.participant_list_trimmed) == 0:
            self.participant_list_trimmed = ["Empty"]
        self.participant_markers = {0:[], 1:[], 2:[], 3:[]}
        self.generate_participant_markers()
        marked_participants = self.mark_participants()
        self.participants_list_box.Set(marked_participants)
        del self.participant_list_trimmed[:]
        dlg.Destroy()
        self.Run_Button.Enable()
        event.Skip()

    def Plus_Press(self, event):  # wxGlade: MyFrame.<event_handler>
        dlg = wx.TextEntryDialog(self, 'Enter Task Name', 'New Task')
        dlg.SetValue("")
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.GetValue() in self.task_list:
                dlg_warning = wx.MessageDialog(self, "Task name already exists!", style=wx.OK|wx.CENTRE|wx.ICON_WARNING)
                dlg_warning.ShowModal()
                dlg_warning.Destroy()
                return
            new_task = {}
            self.experiment_holder['experiment'] = self.current_experiment
            self.current_experiment.append(new_task)
            self.highlit_task_num = len(self.current_experiment) - 1
            self.current_experiment[self.highlit_task_num]["task_name"] = dlg.GetValue()
            self.current_experiment[self.highlit_task_num]['target_distance_ratio'] = float(100/100)
            self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN'] = 3
            self.current_experiment[self.highlit_task_num]['rotation_change_type'] = 'abrupt'
            self.current_experiment[self.highlit_task_num]['rotation_angle'] = 0
            self.current_experiment[self.highlit_task_num]['trial_type'] = 'cursor'
            self.current_experiment[self.highlit_task_num]['terminal_feedback_time'] = 0.5
            self.current_experiment[self.highlit_task_num]['num_targets'] = 3
#            self.current_experiment[self.highlit_task_num]['lag'] = 0
            self.current_experiment[self.highlit_task_num]['num_trials'] = 3
            self.current_experiment[self.highlit_task_num]['terminal_multiplier'] = 1.025
            self.current_experiment[self.highlit_task_num]['pause_button_wait'] = False
            self.current_experiment[self.highlit_task_num]['min_angle'] = 40
            self.current_experiment[self.highlit_task_num]['max_angle'] = 140
            self.current_experiment[self.highlit_task_num]['terminal_feedback'] = False
            self.current_experiment[self.highlit_task_num]['pausetime'] = 5
            self.current_experiment[self.highlit_task_num]['poll_type'] = 'x11'
            self.current_experiment[self.highlit_task_num]['rotation_angle_direction'] = 'Counter-clockwise'
            self.current_experiment[self.highlit_task_num]['pause_instruction'] = ""
            self.current_experiment[self.highlit_task_num]['final_rotation_angle'] = 0

            # Scoring System
            self.current_experiment[self.highlit_task_num]['use_score'] = False

#            with open(self.experiment_folder + self.current_experiment_name + ".json", "wb") as f:
#                dump(self.experiment_holder, f)
#                f.close()
            del self.task_list[:]
            for i in range (0, len(self.current_experiment)):
                self.task_list.append(self.current_experiment[i]['task_name'])
            self.task_list_box.Set(self.task_list)
            #### Set current highlit task to new task ####
            self.task_list_box.SetSelection(len(self.current_experiment) - 1)
            self.highlit_task = dlg.GetValue()
            self.highlit_task_num = len(self.current_experiment) - 1
            ### Set Current Task Settings
            self.radio_box_1.SetSelection(exp.task_num(self.current_experiment[self.highlit_task_num]['trial_type'], True))
            self.num_trial_CB.SetValue(self.current_experiment[self.highlit_task_num]['num_trials'])
            self.num_targ_CB.SetStringSelection(str(self.current_experiment[self.highlit_task_num]['num_targets']))
            self.pause_txt.SetValue(str(self.current_experiment[self.highlit_task_num]['pausetime']))
            self.pause_message_txt.SetValue(self.current_experiment[self.highlit_task_num]['pause_instruction'])
            # Show or hide Pause menu
            if self.current_experiment[self.highlit_task_num]['trial_type'] == "pause":
                self.pause_experiment_show()
                try:
                    self.pause_txt.SetValue(str(self.current_experiment[self.highlit_task_num]['pausetime']))
                    self.pause_message_txt.SetValue(self.current_experiment[self.highlit_task_num]['pause_instruction'])
                except:
                    self.pause_txt.SetValue('5')
                    self.pause_message_txt.SetValue('')
            else:
                self.regular_experiment_show()
            self.min_angle_CB.SetValue(self.current_experiment[self.highlit_task_num]['min_angle'])
            self.max_angle_CB.SetValue(self.current_experiment[self.highlit_task_num]['max_angle'])
            try:
                pass
#                self.lag_txt.SetValue(str(self.current_experiment[self.highlit_task_num]['lag_value']))
            except:
                pass
#                self.lag_txt.SetValue("0")
        else:
            pass
        dlg.Destroy()
        #### CHECK IF ANY TASKS ####
        if len(self.experiment_holder['experiment']) > 0:
            self.Run_Button.Enable()
        else:
            self.Run_Button.Disable()
        event.Skip()

    def Minus_Press(self, event):  # wxGlade: MyFrame.<event_handler>
        del self.current_experiment[self.highlit_task_num] # remove current task
        self.highlit_task_num = len(self.current_experiment) - 1
#        with open(self.experiment_folder + self.current_experiment_name + ".json", "wb") as f:
#            dump(self.current_experiment, f) #remove current task from file
#            f.close()
        del self.task_list[:]
        # refresh task list
        for i in range (0, len(self.current_experiment)):
            self.task_list.append(self.current_experiment[i]["task_name"])
        if len(self.task_list) == 0:
            self.task_list_box.Set(['None'])
        else:
            self.task_list_box.Set(self.task_list)
        #### CHECK IF ANY TASKS ####
        if len(self.experiment_holder['experiment']) > 0:
            self.Run_Button.Enable()
        else:
            self.Run_Button.Disable()
        event.Skip()

    def Trial_Type_Press(self, event):  # wxGlade: MyFrame.<event_handler>
        chosen_trial = event.GetString()
        try:
            if (chosen_trial == "Cursor"):
                self.current_experiment[self.highlit_task_num]["trial_type"] = "cursor"
                self.regular_experiment_show()
            elif(chosen_trial == "No Cursor"):
                self.current_experiment[self.highlit_task_num]["trial_type"] = "no_cursor"
                self.regular_experiment_show()
            elif(chosen_trial == "Pause"):
                self.current_experiment[self.highlit_task_num]["trial_type"] = "pause"
                self.pause_experiment_show()
            elif(chosen_trial == "Error Clamp"):
                self.current_experiment[self.highlit_task_num]["trial_type"] = "error_clamp"
                self.regular_experiment_show()
            if (chosen_trial != "Cursor"):
                self.current_experiment[self.highlit_task_num]['rotation_change_type'] = 'abrupt'
                self.MIN_TRIAL_BOOL = False
                self.rot_change_statictext.SetSelection(exp.rotation_num(self.current_experiment[self.highlit_task_num]['rotation_change_type'], True))
#            with open(self.experiment_folder+self.current_experiment_name+".json", "wb") as f:
#                dump(self.current_experiment, f)
#                f.close()
            # refresh task list
            del self.task_list[:]
            for i in range (0, len(self.current_experiment)):
                self.task_list.append(self.current_experiment[i]['task_name'])
            if len(self.task_list) == 0:
                self.task_list_box.Set(['None'])
            else:
                self.task_list_box.Set(self.task_list)
            self.task_list_box.SetSelection(self.highlit_task_num)
        except:
            pass
        # save change

        event.Skip()

    def min_angle_choose(self, event):  # wxGlade: MyFrame.<event_handler>
        self.min_angle_chosen = exp.myRounder(event.GetInt(), 5)
        if self.min_angle_chosen < self.max_angle_chosen:
            self.min_angle_CB.SetValue(self.min_angle_chosen)
        else:
            self.max_angle_chosen = self.min_angle_chosen
            self.min_angle_CB.SetValue(self.min_angle_chosen)
            self.max_angle_CB.SetValue(self.min_angle_chosen)
        self.current_experiment[self.highlit_task_num]['min_angle'] = self.min_angle_chosen
        self.current_experiment[self.highlit_task_num]['max_angle'] = self.max_angle_chosen
        #save
#        with open(self.experiment_folder+self.current_experiment_name+".json", "wb") as f:
#            dump(self.current_experiment, f)
#            f.close()
        event.Skip()

    def max_angle_choose(self, event):  # wxGlade: MyFrame.<event_handler>
        self.max_angle_chosen = exp.myRounder(event.GetInt(), 5)
        if self.max_angle_chosen > self.min_angle_chosen:
            self.max_angle_CB.SetValue(self.max_angle_chosen)
        else:
            self.min_angle_chosen = self.max_angle_chosen
            self.min_angle_CB.SetValue(self.min_angle_chosen)
            self.max_angle_CB.SetValue(self.min_angle_chosen)
        self.current_experiment[self.highlit_task_num]['min_angle'] = self.min_angle_chosen
        self.current_experiment[self.highlit_task_num]['max_angle'] = self.max_angle_chosen
        #save
#        with open(self.experiment_folder+self.current_experiment_name+".json", "wb") as f:
#            dump(self.current_experiment, f)
#            f.close()
        event.Skip()

    def Move_Up(self, event):  # wxGlade: MyFrame.<event_handler>
        if (self.highlit_task_num > 0):
            self.current_experiment[self.highlit_task_num], self.current_experiment[self.highlit_task_num - 1] = self.current_experiment[self.highlit_task_num - 1], self.current_experiment[self.highlit_task_num]
            self.highlit_task_num = self.highlit_task_num - 1
#        with open(self.experiment_folder+self.current_experiment_name+".json", "wb") as f:
#            dump(self.current_experiment, f)
#            f.close()
        # refresh task list
        del self.task_list[:]
        for i in range (0, len(self.current_experiment)):
            self.task_list.append(self.current_experiment[i]["task_name"])
        if len(self.task_list) == 0:
            self.task_list_box.Set(['None'])
        else:
            self.task_list_box.Set(self.task_list)
            self.task_list_box.SetSelection(self.highlit_task_num)
        event.Skip()

    def Move_Down(self, event):  # wxGlade: MyFrame.<event_handler>
        if (self.highlit_task_num < len(self.task_list) - 1):
            self.current_experiment[self.highlit_task_num], self.current_experiment[self.highlit_task_num + 1] = self.current_experiment[self.highlit_task_num + 1], self.current_experiment[self.highlit_task_num]
            self.highlit_task_num = self.highlit_task_num + 1
#        with open(self.experiment_folder+self.current_experiment_name+".json", "wb") as f:
#            dump(self.current_experiment, f)
#            f.close()
        # refresh task list
        del self.task_list[:]
        for i in range (0, len(self.current_experiment)):
            self.task_list.append(self.current_experiment[i]["task_name"])
        if len(self.task_list) == 0:
            self.task_list_box.Set(['None'])
        else:
            self.task_list_box.Set(self.task_list)
            self.task_list_box.SetSelection(self.highlit_task_num)
        event.Skip()

    def num_target_choose(self, event):  # wxGlade: MyFrame.<event_handler>
        self.num_target_chosen = int(event.GetString())
#        print self.num_trial_CB.GetValue()
#        print self.MIN_TRIAL_BOOL
        self.current_experiment[self.highlit_task_num]['num_targets'] = self.num_target_chosen
        self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN'] = ceil(float(self.Rotation_angle_slider.GetValue())/float(int(self.num_targ_CB.GetValue())))*(float(int(self.num_targ_CB.GetValue()))) + int(self.num_targ_CB.GetValue())
        ## Set num trial default
        if self.num_target_chosen > 2:
            if self.num_trial_CB.GetValue() < self.num_target_chosen:
                self.num_trial_CB.SetValue(self.num_target_chosen)
            self.num_trial_mult = self.num_target_chosen
        elif self.num_target_chosen == 1:
            if self.num_trial_CB.GetValue() < self.num_target_chosen:
                self.num_trial_CB.SetValue(3)
            self.num_trial_mult = 3
        elif self.num_target_chosen == 2:
            if self.num_trial_CB.GetValue() < self.num_target_chosen:
                self.num_trial_CB.SetValue(4)
            self.num_trial_mult = 4
        else:
            self.num_trial_mult = self.num_target_chosen
        if self.num_trial_CB.GetValue()%self.num_target_chosen != 0:
            self.num_trial_CB.SetValue(exp.myRounder(self.num_trial_CB.GetValue(),self.num_target_chosen))
        self.current_experiment[self.highlit_task_num]['num_trials'] = self.num_trial_CB.GetValue()
#        self.valid_trial_num = self.num_trial_CB.GetValue()

#        if self.MIN_TRIAL_BOOL == True and int(self.num_trial_CB.GetValue()) < int(self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN']):
#            self.num_trial_CB.SetValue(self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN'])
#            self.current_experiment[self.highlit_task_num]['num_trials'] = self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN']

        ## SAVE
#        with open(self.experiment_folder+self.current_experiment_name+".json", "wb") as f:
#            dump(self.current_experiment, f)
#            f.close()
        event.Skip()


    def num_trial_choose(self, event):  # wxGlade: MyFrame.<event_handler>
#        print self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN']
        if event.GetInt() == self.MIN_TRIALS or event.GetInt() >= self.MAX_TRIALS + 1:
            self.num_trial_CB.SetValue(self.valid_trial_num)
        elif event.GetInt() > self.valid_trial_num and event.GetInt() < (self.valid_trial_num + self.num_trial_mult) and (event.GetInt() + self.num_trial_mult) <= self.MAX_TRIALS :
            self.num_trial_CB.SetValue(self.valid_trial_num + self.num_trial_mult)
            self.valid_trial_num = self.valid_trial_num + self.num_trial_mult
        elif event.GetInt() < self.valid_trial_num and event.GetInt() > (self.valid_trial_num - self.num_trial_mult) and (self.valid_trial_num - self.num_trial_mult) > 0 and (event.GetInt() - self.num_trial_mult) > 0:
            self.num_trial_CB.SetValue(self.valid_trial_num - self.num_trial_mult)
            self.valid_trial_num = self.valid_trial_num - self.num_trial_mult
        else:
            self.num_trial_CB.SetValue(exp.myRounder(event.GetInt(), self.num_trial_mult))
            self.valid_trial_num = exp.myRounder(event.GetInt(), self.num_trial_mult)
        if event.GetInt() < self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN'] and self.MIN_TRIAL_BOOL == True:
            self.num_trial_CB.SetValue(self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN'])
            self.valid_trial_num = self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN']
        self.num_trial_chosen = self.valid_trial_num
        self.current_experiment[self.highlit_task_num]['num_trials'] = int(self.num_trial_chosen)
#        print self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN']
        ## SAVE
#        with open(self.experiment_folder+self.current_experiment_name+".json", "wb") as f:
#            dump(self.current_experiment, f)
#            f.close()
        event.Skip()

    def rot_angle_choose(self, event):  # wxGlade: MyFrame.<event_handler>
        self.rotation_angle_chosen = exp.myRounder(event.GetInt(), 1)
        self.Rotation_angle_slider.SetValue(self.rotation_angle_chosen)
        self.current_experiment[self.highlit_task_num]['rotation_angle'] = self.rotation_angle_chosen

        ### Gradual minimum trials (Outdated?) ####
#        self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN'] = (ceil(float(int(abs(self.Rotation_angle_slider.GetValue()))/float(int(self.num_targ_CB.GetValue())))))*(float(int(self.num_targ_CB.GetValue()))) + int(self.num_targ_CB.GetValue())
#        if self.MIN_TRIAL_BOOL == True and int(self.num_trial_CB.GetValue()) < int(self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN']):
#            self.num_trial_CB.SetValue(self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN'])
#            self.current_experiment[self.highlit_task_num]['num_trials'] = self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN']
#
#        if self.current_experiment[self.highlit_task_num]['rotation_angle'] < 0:
#            self.current_experiment[self.highlit_task_num]['rotation_direction'] = -1
#        else:
#            self.current_experiment[self.highlit_task_num]['rotation_direction'] = 1
        event.Skip()
    def rot_angle_end_choose(self, event):
        self.rotation_angle_chosen = exp.myRounder(event.GetInt(), 1)
        self.Rotation_angle_end_slider.SetValue(self.rotation_angle_chosen)
        self.current_experiment[self.highlit_task_num]['final_rotation_angle'] = self.rotation_angle_chosen
        event.Skip()

    def Rot_Change_Press(self, event):  # wxGlade: MyFrame.<event_handler>
        self.current_experiment[self.highlit_task_num]['rotation_change_type'] = (event.GetString()).lower()
        if (event.GetString().lower() == 'abrupt'):
#            self.MIN_TRIAL_BOOL = False
            self.Rotation_angle_end_slider.Disable()
            self.Rotation_angle_end_statictext.Disable()
            self.Rotation_angle_statictext.SetLabel("Rotation")
        elif (event.GetString().lower() == 'gradual'):
#            self.MIN_TRIAL_BOOL = True
            self.Rotation_angle_end_slider.Enable()
            self.Rotation_angle_end_statictext.Enable()
            self.Rotation_angle_statictext.SetLabel("Initial rotation")
#        if self.MIN_TRIAL_BOOL == True and int(self.num_trial_CB.GetValue()) < int(self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN']):
#            self.num_trial_CB.SetValue(self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN'])
#            self.current_experiment[self.highlit_task_num]['num_trials'] = self.current_experiment[self.highlit_task_num]['NUM_TRIAL_GRADUAL_MIN']
#
        event.Skip()

#    def Lag_Enter(self, event):  # wxGlade: MyFrame.<event_handler>
#        lag_conversion_factor = 37.2495/1000
#        curr_string = event.GetString()
#        if all(x in '0123456789' for x in curr_string):
#            self.valid_lag_text = curr_string
#        else:
#            self.lag_txt.SetValue(self.valid_lag_text)
#        if (event.GetString() == ''):
#            self.current_experiment[self.highlit_task_num]['lag'] = 0
#        else:
#            self.current_experiment[self.highlit_task_num]['lag'] = int(int(event.GetString())*lag_conversion_factor)
#            self.current_experiment[self.highlit_task_num]['lag_value'] = int(event.GetString())
##        with open(self.experiment_folder+self.current_experiment_name+".json", "wb") as f:
##            dump(self.experiment_holder, f)
##            f.close()
#
#        event.Skip()

    def Pause_Enter(self, event):  # wxGlade: MyFrame.<event_handler>
        curr_string = event.GetString()
        if all(x in '0123456789' for x in curr_string):
            self.valid_pause_text = curr_string
        else:
            self.pause_txt.SetValue(self.valid_pause_text)
        if (event.GetString() == ''):
            self.current_experiment[self.highlit_task_num]['pausetime'] = 0
        else:
            self.current_experiment[self.highlit_task_num]['pausetime'] = int(event.GetString())
#        with open(self.experiment_folder+self.current_experiment_name+".json", "wb") as f:
#            dump(self.current_experiment, f)
#            f.close()
        event.Skip()

    def pause_message_make(self, event):  # wxGlade: MyFrame.<event_handler>
        self.current_experiment[self.highlit_task_num]['pause_instruction'] = event.GetString()
#        with open(self.experiment_folder+self.current_experiment_name+".json", "wb") as f:
#            dump(self.current_experiment, f)
#            f.close()
        event.Skip()

    def pause_check_press(self, event):
        self.current_experiment[self.highlit_task_num]['pause_button_wait'] = event.IsChecked()
        event.Skip()

    def target_distance_choose(self, event):
        self.current_experiment[self.highlit_task_num]['target_distance_ratio'] = float(event.GetInt())/100
        event.Skip()

    def rename_experiment(self, event):
        dlg = wx.TextEntryDialog(self, 'Enter Name', 'Rename experiment')
        dlg.SetValue("")
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.GetValue() in self.experiment_list_trimmed:
                dlg_warning = wx.MessageDialog(self, "Experiment already exists!", style=wx.OK|wx.CENTRE|wx.ICON_WARNING)
                dlg_warning.ShowModal()
                dlg_warning.Destroy()
                return
            rename(self.experiment_folder + self.current_experiment_name + ".json", self.experiment_folder + dlg.GetValue() + ".json")
            rename(path.join("data", self.current_experiment_name), path.join("data", dlg.GetValue()))
            self.experiment_list = listdir(self.experiment_folder)
            del self.experiment_list_trimmed[:]
            for i in self.experiment_list:
                self.experiment_list_trimmed.append(i.replace(".json", ""))
            self.exp_list_box.Set(self.experiment_list_trimmed)
#            self.exp_list_box.SetSelection(len(self.experiment_list_trimmed) - 1)
            self.current_experiment_name = dlg.GetValue()
            with open(self.experiment_folder + self.current_experiment_name + ".json", "rb") as f:
                self.experiment_holder = load(f)
            self.experiment_holder['settings']['experiment_folder'] = dlg.GetValue()
            with open(self.experiment_folder + self.current_experiment_name + ".json", 'wb') as f:
                dump(self.experiment_holder, f)
                f.close()

        dlg.Destroy()
        event.Skip()

    def rename_task(self, event):
        dlg = wx.TextEntryDialog(self, 'Change Task Name', 'Rename')
        dlg.SetValue("")
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.GetValue() not in self.task_list:
                self.current_experiment[self.highlit_task_num]["task_name"] = dlg.GetValue()
            else:
                dlg_warning = wx.MessageDialog(self, "Task name already exists!", style=wx.OK|wx.CENTRE|wx.ICON_WARNING)
                dlg_warning.ShowModal()
                dlg_warning.Destroy()
                return
        del self.task_list[:]
        for i in range (0, len(self.current_experiment)):
            self.task_list.append(self.current_experiment[i]['task_name'])
        self.task_list_box.Set(self.task_list)
        dlg.Destroy()
        event.Skip()
    def terminalfeedback_check_press(self, event):
        self.current_experiment[self.highlit_task_num]['terminal_feedback'] = event.IsChecked()
        event.Skip()

    # Scoring System Events
    def score_check_press(self, event):
        self.current_experiment[self.highlit_task_num]['use_score'] = event.IsChecked()
        self.score_settings_button.Enable(event.IsChecked())
        event.Skip()

    def score_settings_press(self, event):
        scoreframe = ScoreFrame(self, wx.ID_ANY, "")
        scoreframe.Show(True)
        event.Skip()
#    def rotation_angle_direction_press(self, event):
#        self.current_experiment[self.highlit_task_num]['rotation_angle_direction'] = event.GetString()
#        event.Skip()
#    def group_listbox_click(self, event):
#        self.highlit_group = event.GetString()
#        event.Skip()

    def preprocess_press(self, event):
        preprocess = PreprocessFrame(self, wx.ID_ANY, "")
        preprocess.Show(True)
        event.Skip()

    def experiment_settings_Button_Press(self, event):
        settings = SettingsFrameV2(self, wx.ID_ANY, "")
        settings.Show(True)
        event.Skip()

    def participants_list_box_click(self, event):
        self.highlit_participant = self.unmark_participant(event.GetString())
#        print self.experiment_holder['participant'][self.highlit_participant]['state'], [len(self.experiment_holder['experiment']) - 1, self.experiment_holder['experiment'][-1]['num_trials'] - 1]
#        exp.concat_full(self.highlit_participant, self.experiment_holder)
        self.participant_markers = {0:[], 1:[], 2:[], 3:[]}
        self.generate_participant_markers()
        print self.highlit_participant
#        print self.participant_markers
#        if exp.get_participant_state(self.highlit_participant, self.experiment_holder) == [len(self.experiment_holder['experiment']), self.experiment_holder['experiment'][-1]['num_trials']]:
        if self.highlit_participant in self.participant_markers[0]:
            self.continue_Button.Disable()
            self.recombine_Button.Enable()
        elif self.highlit_participant in self.participant_markers[1]:
            self.continue_Button.Enable()
            self.recombine_Button.Disable()
        else:
            self.continue_Button.Disable()
            self.recombine_Button.Disable()
        event.Skip()
    def continue_Button_Press(self, event):
        dlg = wx.MessageDialog(self, "Continue running this participant?", style=wx.CENTRE|wx.ICON_QUESTION|wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            #### GET CURRENT EXPERIMENT STATE ####
            exp.continue_experiment(self.highlit_participant, self.experiment_holder)
        dlg.Destroy()
        event.Skip()

    def recombine_Button_Press(self, event):
        dlg = wx.MessageDialog(self, "Recombine this participants data?", style=wx.CENTRE|wx.ICON_QUESTION|wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            #### GET CURRENT EXPERIMENT STATE ####
            exp.concat_full(self.highlit_participant, self.experiment_holder)
        dlg.Destroy()
        event.Skip()

    def generate_participant_markers(self):
        for participant in self.participant_list:
            participant_experiment_file = {}
            try:
                with open(path.join("data", self.current_experiment_name, participant, self.current_experiment_name + ".json"), "rb") as f:
                    participant_experiment_file = load(f)
                    f.close()
            except:
                pass
            if exp.get_participant_state(participant, self.experiment_holder) == [len(self.experiment_holder['experiment']), self.experiment_holder['experiment'][-1]['num_trials']]:
                if participant_experiment_file == self.experiment_holder:
                    self.participant_markers[0].append(participant)
                elif participant_experiment_file != self.experiment_holder:
                    self.participant_markers[2].append(participant)
            elif exp.get_participant_state(participant, self.experiment_holder) != [len(self.experiment_holder['experiment']), self.experiment_holder['experiment'][-1]['num_trials']]:
                if participant_experiment_file == self.experiment_holder:
                    self.participant_markers[1].append(participant)
                elif participant_experiment_file != self.experiment_holder:
                    self.participant_markers[2].append(participant)
            else:
                self.participant_markers[3].append(participant)

    def compare(self, participant, current_experiment):
        participant_experiment_file = {}
        try:
            with open(path.join("data", current_experiment['settings']['experiment_folder'], participant, current_experiment['settings']['experiment_folder'] + ".json"), "rb") as f:
                participant_experiment_file = load(f)
                f.close()

            comparison = participant_experiment_file == current_experiment
            return comparison
        except:
            print "No json found in participant folder"

    def duplicate_experiment(self, event):
        dlg = wx.TextEntryDialog(self, 'Enter Name', 'Duplicate experiment')
        dlg.SetValue("")
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.GetValue() in self.experiment_list_trimmed:
                dlg_warning = wx.MessageDialog(self, "Experiment already exists!", style=wx.OK|wx.CENTRE|wx.ICON_WARNING)
                dlg_warning.ShowModal()
                dlg_warning.Destroy()
                return
            copyfile(self.experiment_folder + self.current_experiment_name + ".json", self.experiment_folder + dlg.GetValue() + ".json")

#            self.exp_list_box.SetSelection(len(self.experiment_list_trimmed) - 1)
            self.current_experiment_name = dlg.GetValue()
            with open(self.experiment_folder + self.current_experiment_name + ".json", "rb") as f:
                self.experiment_holder = load(f)
            self.experiment_holder['settings']['experiment_folder'] = dlg.GetValue()
#            self.experiment_holder['participant'] = {}
            with open(self.experiment_folder + self.current_experiment_name + ".json", 'wb') as f:
                dump(self.experiment_holder, f)
                f.close()
            if not(path.exists(path.join("data", self.experiment_holder['settings']['experiment_folder']))):
                makedirs(path.join("data", self.experiment_holder['settings']['experiment_folder']))
            self.experiment_list_trimmed.append(dlg.GetValue())
            self.exp_list_box.Set(self.experiment_list_trimmed)
            self.exp_list_box.SetSelection(self.experiment_list_trimmed.index(dlg.GetValue()))
            self.current_experiment_name = dlg.GetValue()
            self.highlit_experiment = dlg.GetValue()
            experimentFolder = self.highlit_experiment
            with open(self.experiment_folder + self.current_experiment_name + ".json", "rb") as f:
                self.experiment_holder = load(f)
                del self.task_list[:]
            self.current_experiment = self.experiment_holder['experiment']
            for i in range (0, len(self.current_experiment)):
                self.task_list.append(self.current_experiment[i]["task_name"])
            if len(self.task_list) == 0:
                self.task_list_box.Set(['Empty'])
            else:
                self.task_list_box.Set(self.task_list)
            #### REFRESH PARTICIPANT LIST #####
            if not(path.exists(path.join("data", experimentFolder))):
                makedirs(path.join("data",experimentFolder))
            self.participant_list = listdir(path.join("data", self.current_experiment_name))
            for i in self.participant_list:
                self.participant_list_trimmed.append(i.replace(".csv", ""))
            if len(self.participant_list_trimmed) == 0:
                self.participant_list_trimmed = ["Empty"]
            self.participants_list_box.Set(self.participant_list_trimmed)
            del self.participant_list_trimmed[:]
            #### CHECK IF ANY TASKS ####
            if len(self.experiment_holder['experiment']) > 0:
                self.Run_Button.Enable()
            else:
                self.Run_Button.Disable()

        dlg.Destroy()
        event.Skip()
    def duplicate_task(self, event):
        dlg = wx.TextEntryDialog(self, 'Change Task Name', 'Duplicate Task')
        dlg.SetValue("")
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.GetValue() in self.task_list:
                dlg_warning = wx.MessageDialog(self, "Task name already exists!", style=wx.OK|wx.CENTRE|wx.ICON_WARNING)
                dlg_warning.ShowModal()
                dlg_warning.Destroy()
                return
            copy_task = deepcopy(self.current_experiment[self.highlit_task_num])
            self.current_experiment.append(copy_task)
            self.highlit_task_num = len(self.current_experiment) - 1
            self.highlit_task = dlg.GetValue()
            self.current_experiment[self.highlit_task_num]["task_name"] = dlg.GetValue()
        del self.task_list[:]
        for i in range (0, len(self.current_experiment)):
            self.task_list.append(self.current_experiment[i]['task_name'])
        self.task_list_box.Set(self.task_list)
        dlg.Destroy()
        self.task_list_box.SetSelection(self.highlit_task_num)
        event.Skip()

    def concat_csv(self, participant):
        file_list = []
        for i in range(0, len(self.current_experiment)):
            for j in range(0, self.current_experiment[i]['num_trials']):
                file_list.append(self.current_experiment[i]['task_name'] + '_' + str(j))
############################### SETTINGS Panel ##############################

class SettingsFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        ### Empty image preset ###
        self.empty_image = wx.EmptyImage(35,35)
        ### OPTION STATES ###
        self.fullscreen_state = self.Parent.experiment_holder['settings']['fullscreen']
        self.flipscreen_state = self.Parent.experiment_holder['settings']['flipscreen']
        self.waitblanking_state = self.Parent.experiment_holder['settings']['waitblanking']
        self.viewscale_state = self.Parent.experiment_holder['settings']['viewscale']
        self.collect_return_movement_state = self.Parent.experiment_holder['settings']['return_movement']
        self.enable_custom_target_state = self.Parent.experiment_holder['settings']['custom_target_enable']
        self.custom_target_file_state = self.Parent.experiment_holder['settings']['custom_target_file']
        self.enable_custom_cursor_state = self.Parent.experiment_holder['settings']['custom_cursor_enable']
        self.custom_cursor_file_state = self.Parent.experiment_holder['settings']['custom_cursor_file']
        self.enable_custom_home_state = self.Parent.experiment_holder['settings']['custom_home_enable']
        self.custom_home_file_state = self.Parent.experiment_holder['settings']['custom_home_file']


        ###############
        self.fullscreen_toggle = wx.CheckBox(self, wx.ID_ANY, "Fullscreen")
        self.flipscreen_toggle = wx.CheckBox(self, wx.ID_ANY, "Flip-Screen")
        self.waitblanking_toggle = wx.CheckBox(self, wx.ID_ANY, "wait for blanking")

        # ADD TWO sliders... or should it be textboxes?
        self.viewscaleX_slider = wx.Slider(self, wx.ID_ANY, minValue = 30, maxValue = 130, value = 100, style = wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.viewscaleY_slider = wx.Slider(self, wx.ID_ANY, minValue = 30, maxValue = 130, value = 100, style = wx.SL_HORIZONTAL | wx.SL_LABELS)

        self.collect_return_movement_toggle = wx.CheckBox(self, wx.ID_ANY, "Collect return movement")
        self.enable_custom_target = wx.CheckBox(self, wx.ID_ANY, "Enable custom target")
        self.custom_target_file = wx.FilePickerCtrl(self, wx.ID_ANY, path="", style=wx.FLP_USE_TEXTCTRL, wildcard = "PNG and JPEG and BMP and JPG files (*.png;*.jpeg;*.bmp;*.jpg)|*.png;*.jpeg;*.bmp;*.jpg")
        self.custom_target_preview = wx.StaticBitmap(self, wx.ID_ANY, bitmap=wx.BitmapFromImage(self.empty_image), size=[35,35])
        self.enable_custom_cursor = wx.CheckBox(self, wx.ID_ANY, "Enable custom cursor")
        self.custom_cursor_file = wx.FilePickerCtrl(self, wx.ID_ANY, path="", style=wx.FLP_USE_TEXTCTRL, wildcard = "PNG and JPEG and BMP and JPG files (*.png;*.jpeg;*.bmp;*.jpg)|*.png;*.jpeg;*.bmp;*.jpg")
        self.custom_cursor_preview = wx.StaticBitmap(self, wx.ID_ANY, bitmap=wx.BitmapFromImage(self.empty_image), size=[35,35])
        self.enable_custom_home = wx.CheckBox(self, wx.ID_ANY, "Enable custom home")
        self.custom_home_file = wx.FilePickerCtrl(self, wx.ID_ANY, path="", style=wx.FLP_USE_TEXTCTRL, wildcard = "PNG and JPEG and BMP and JPG files (*.png;*.jpeg;*.bmp;*.jpg)|*.png;*.jpeg;*.bmp;*.jpg")
        self.custom_home_preview = wx.StaticBitmap(self, wx.ID_ANY, bitmap=wx.BitmapFromImage(self.empty_image), size=[35,35])



        self.apply_button = wx.Button(self, wx.ID_ANY, "Apply Changes")
        self.cancel_button = wx.Button(self, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_CHECKBOX, self.fullscreen_toggle_press, self.fullscreen_toggle)
        self.Bind(wx.EVT_CHECKBOX, self.flipscreen_toggle_press, self.flipscreen_toggle)
        self.Bind(wx.EVT_CHECKBOX, self.waitblanking_toggle_press, self.waitblanking_toggle)

        self.Bind(wx.EVT_SLIDER, self.viewscale_slide, self.viewscaleX_slider)
        self.Bind(wx.EVT_SLIDER, self.viewscale_slide, self.viewscaleY_slider)

        self.Bind(wx.EVT_CHECKBOX, self.collect_return_movement_toggle_press, self.collect_return_movement_toggle)
        self.Bind(wx.EVT_CHECKBOX, self.enable_custom_target_press, self.enable_custom_target)
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.custom_target_file_choose, self.custom_target_file)
        self.Bind(wx.EVT_CHECKBOX, self.enable_custom_cursor_press, self.enable_custom_cursor)
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.custom_cursor_file_choose, self.custom_cursor_file)
        self.Bind(wx.EVT_CHECKBOX, self.enable_custom_home_press, self.enable_custom_home)
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.custom_home_file_choose, self.custom_home_file)

        self.Bind(wx.EVT_BUTTON, self.apply_button_press, self.apply_button)
        self.Bind(wx.EVT_BUTTON, self.cancel_button_press, self.cancel_button)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("Settings")
        self.SetSize((200,350))
        self.fullscreen_toggle.SetValue(self.Parent.experiment_holder['settings']['fullscreen'])
        self.flipscreen_toggle.SetValue(self.Parent.experiment_holder['settings']['flipscreen'])
        self.waitblanking_toggle.SetValue(self.Parent.experiment_holder['settings']['waitblanking'])
        self.viewscaleX_slider.SetValue(self.Parent.experiment_holder['settings']['viewscale'][0]*100)
        self.viewscaleY_slider.SetValue(self.Parent.experiment_holder['settings']['viewscale'][1]*100)
        self.collect_return_movement_toggle.SetValue(self.Parent.experiment_holder['settings']['return_movement'])
        self.enable_custom_target.SetValue(self.Parent.experiment_holder['settings']['custom_target_enable'])
        self.enable_custom_home.SetValue(self.Parent.experiment_holder['settings']['custom_home_enable'])
        self.enable_custom_cursor.SetValue(self.Parent.experiment_holder['settings']['custom_cursor_enable'])
        self.custom_target_file.SetPath(self.Parent.experiment_holder['settings']['custom_target_file'])
        self.custom_home_file.SetPath(self.Parent.experiment_holder['settings']['custom_home_file'])
        self.custom_cursor_file.SetPath(self.Parent.experiment_holder['settings']['custom_cursor_file'])

        if self.Parent.experiment_holder['settings']['custom_target_file'] != "":
            image = wx.Image(self.Parent.experiment_holder['settings']['custom_target_file'], wx.BITMAP_TYPE_ANY)
            image.Rescale(35,35)
            self.custom_target_preview.SetBitmap(wx.BitmapFromImage(image))
        else:
            self.custom_target_preview.SetBitmap(wx.BitmapFromImage(self.empty_image))

        if self.Parent.experiment_holder['settings']['custom_home_file'] != "":
            image = wx.Image(self.Parent.experiment_holder['settings']['custom_home_file'], wx.BITMAP_TYPE_ANY)
            image.Rescale(35,35)
            self.custom_home_preview.SetBitmap(wx.BitmapFromImage(image))
        else:
            self.custom_home_preview.SetBitmap(wx.BitmapFromImage(self.empty_image))

        if self.Parent.experiment_holder['settings']['custom_cursor_file'] != "":
            image = wx.Image(self.Parent.experiment_holder['settings']['custom_cursor_file'], wx.BITMAP_TYPE_ANY)
            image.Rescale(35,35)
            self.custom_cursor_preview.SetBitmap(wx.BitmapFromImage(image))
        else:
            self.custom_cursor_preview.SetBitmap(wx.BitmapFromImage(self.empty_image))


        if self.enable_custom_target_state == False:
            self.custom_target_file.Disable()
            self.custom_target_preview.Disable()
        elif self.enable_custom_target_state == True:
            self.custom_target_file.Enable()
            self.custom_target_preview.Enable()

        if self.enable_custom_home_state == False:
            self.custom_home_file.Disable()
            self.custom_home_preview.Disable()
        elif self.enable_custom_home_state == True:
            self.custom_home_file.Enable()
            self.custom_home_preview.Enable()

        if self.enable_custom_cursor_state == False:
            self.custom_cursor_file.Disable()
            self.custom_cursor_preview.Disable()
        elif self.enable_custom_cursor_state == True:
            self.custom_cursor_file.Enable()
            self.custom_cursor_preview.Enable()
    def __do_layout(self):
        horizontal_main = wx.BoxSizer(wx.HORIZONTAL)
        vertical_1 = wx.BoxSizer(wx.VERTICAL)
        vertical_1.Add(self.fullscreen_toggle, 0, wx.TOP, 2)
        vertical_1.Add(self.flipscreen_toggle, 0, wx.TOP, 2)
        vertical_1.Add(self.waitblanking_toggle, 0, wx.TOP, 2)
        vertical_1.Add(self.viewscaleX_slider, 0, wx.EXPAND | wx.ALL, 2)
        vertical_1.Add(self.viewscaleY_slider, 0, wx.EXPAND | wx.ALL, 2)
        vertical_1.Add(self.collect_return_movement_toggle, 0, wx.TOP, 2)
        vertical_1.Add(self.enable_custom_target, 0, wx.TOP, 2)
        horizontal_1 = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_1.Add(self.custom_target_preview,0, wx.LEFT, 2)
        horizontal_1.Add(self.custom_target_file, 0, wx.RIGHT, 2)
        vertical_1.Add(horizontal_1)
        vertical_1.Add(self.enable_custom_home, 0, wx.TOP, 2)
        horizontal_2 = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_2.Add(self.custom_home_preview,0, wx.LEFT, 2)
        horizontal_2.Add(self.custom_home_file, 0, wx.RIGHT, 2)
        vertical_1.Add(horizontal_2)
        vertical_1.Add(self.enable_custom_cursor, 0, wx.TOP, 2)
        horizontal_3 = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_3.Add(self.custom_cursor_preview, 0, wx.LEFT, 2)
        horizontal_3.Add(self.custom_cursor_file, 0, wx.RIGHT, 2)
        vertical_1.Add(horizontal_3)

        vertical_1.Add(self.apply_button, 0, wx.BOTTOM, 2)
        vertical_1.Add(self.cancel_button, 0, wx.BOTTOM, 2)
        horizontal_main.Add(vertical_1, 1, 0, 0)

        self.SetSizer(horizontal_main)
        self.Layout()

    def fullscreen_toggle_press(self, event):
        self.fullscreen_state = event.IsChecked()
        event.Skip()
    def flipscreen_toggle_press(self, event):
        self.flipscreen_state = event.IsChecked()
        event.Skip()
    #def viewscale_slide(self, event):  # wxGlade: MyFrame.<event_handler>
    #    self.viewscale_state = [self.viewscaleX_slider/100., self.viewscaleY_slider/100.]
    #    self.experiment_holder['settings']['viewscale'] = self.viewscale_state
    #    event.Skip()

    def collect_return_movement_toggle_press(self, event):
        self.collect_return_movement_state = event.IsChecked()
        event.Skip()

    def enable_custom_target_press(self, event):
        self.enable_custom_target_state = event.IsChecked()
        if self.enable_custom_target_state == False:
            self.custom_target_file.Disable()
            self.custom_target_preview.Disable()
        elif self.enable_custom_target_state == True:
            self.custom_target_file.Enable()
            self.custom_target_preview.Enable()
        event.Skip()

    def custom_target_file_choose(self, event):
        self.custom_target_file_state = event.GetPath()
        image = wx.Image(self.custom_target_file_state, wx.BITMAP_TYPE_ANY)
        image.Rescale(35,35)
        self.custom_target_preview.SetBitmap(wx.BitmapFromImage(image))
        event.Skip()

    def enable_custom_home_press(self, event):
        self.enable_custom_home_state = event.IsChecked()
        if self.enable_custom_home_state == False:
            self.custom_home_file.Disable()
            self.custom_home_preview.Disable()
        elif self.enable_custom_home_state == True:
            self.custom_home_file.Enable()
            self.custom_home_preview.Enable()
        event.Skip()

    def custom_home_file_choose(self, event):
        self.custom_home_file_state = event.GetPath()
        image = wx.Image(self.custom_home_file_state, wx.BITMAP_TYPE_ANY)
        image.Rescale(35,35)
        self.custom_home_preview.SetBitmap(wx.BitmapFromImage(image))
        event.Skip()

    def enable_custom_cursor_press(self, event):
        self.enable_custom_cursor_state = event.IsChecked()
        if self.enable_custom_cursor_state == False:
            self.custom_cursor_file.Disable()
            self.custom_cursor_preview.Disable()
        elif self.enable_custom_cursor_state == True:
            self.custom_cursor_file.Enable()
            self.custom_cursor_preview.Enable()
        event.Skip()

    def custom_cursor_file_choose(self, event):
        self.custom_cursor_file_state = event.GetPath()
        image = wx.Image(self.custom_cursor_file_state, wx.BITMAP_TYPE_ANY)
        image.Rescale(35,35)
        self.custom_cursor_preview.SetBitmap(wx.BitmapFromImage(image))
        event.Skip()

    def apply_button_press(self, event):
        self.Parent.experiment_holder['settings']['fullscreen'] = self.fullscreen_state
        self.Parent.experiment_holder['settings']['flipscreen'] = self.flipscreen_state
        self.Parent.experiment_holder['settings']['waitblanking'] = self.waitblanking_state
        self.Parent.experiment_holder['settings']['viewscale'] = self.viewscale_state
        self.Parent.experiment_holder['settings']['return_movement'] = self.collect_return_movement_state
        self.Parent.experiment_holder['settings']['custom_target_enable'] = self.enable_custom_target_state
        self.Parent.experiment_holder['settings']['custom_target_file'] = self.custom_target_file_state
        self.Parent.experiment_holder['settings']['custom_home_enable'] = self.enable_custom_home_state
        self.Parent.experiment_holder['settings']['custom_home_file'] = self.custom_home_file_state
        self.Parent.experiment_holder['settings']['custom_cursor_enable'] = self.enable_custom_cursor_state
        self.Parent.experiment_holder['settings']['custom_cursor_file'] = self.custom_cursor_file_state

        self.Destroy()
        event.Skip()
    def cancel_button_press(self, event):
        self.Destroy()
        event.Skip()

###################### SETTINGS FRAME VERSION 2 #####################
class SettingsFrameV2(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        ### Empty image preset ###
        self.empty_image = wx.EmptyImage(35,35)
        ### OPTION STATES ###
        self.fullscreen_state = self.Parent.experiment_holder['settings']['fullscreen']
        self.flipscreen_state = self.Parent.experiment_holder['settings']['flipscreen']
        self.waitblanking_state = self.Parent.experiment_holder['settings']['waitblanking']
        self.viewscale_state = self.Parent.experiment_holder['settings']['viewscale']
        self.collect_return_movement_state = self.Parent.experiment_holder['settings']['return_movement']
        self.enable_custom_stim_state = self.Parent.experiment_holder['settings']['custom_stim_enable']
        self.custom_stim_file_state = self.Parent.experiment_holder['settings']['custom_stim_file']
        self.screen_choose_state = str(self.Parent.experiment_holder['settings']['screen'])
       ###############
        self.fullscreen_toggle = wx.CheckBox(self, wx.ID_ANY, "Fullscreen")
        self.flipscreen_toggle = wx.CheckBox(self, wx.ID_ANY, "Flip-Screen")
        self.waitblanking_toggle = wx.CheckBox(self, wx.ID_ANY, "wait for blanking")
        self.viewscaleX_text = wx.StaticText(self, wx.ID_ANY, ("Horizontal view-scale:"))
        self.viewscaleX_slider = wx.Slider(self, wx.ID_ANY, minValue = 30, maxValue = 130, value = self.viewscale_state[0]*100, style = wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.viewscaleY_text = wx.StaticText(self, wx.ID_ANY, ("Vertical view-scale:"))
        self.viewscaleY_slider = wx.Slider(self, wx.ID_ANY, minValue = 30, maxValue = 130, value = self.viewscale_state[1]*100, style = wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.collect_return_movement_toggle = wx.CheckBox(self, wx.ID_ANY, "Collect return movement")
        self.enable_custom_stim = wx.CheckBox(self, wx.ID_ANY, "Enable custom stimuli")
        self.custom_stim_file = wx.DirPickerCtrl(self, wx.ID_ANY, path="", style=wx.DIRP_USE_TEXTCTRL)

        self.screen_choose_text = wx.StaticText(self, wx.ID_ANY, ("Monitor:"))
        self.screen_choose = wx.ComboBox(self, wx.ID_ANY, value='0', choices=['0', '1'])

        self.apply_button = wx.Button(self, wx.ID_ANY, "Apply Changes")
        self.cancel_button = wx.Button(self, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_CHECKBOX, self.fullscreen_toggle_press, self.fullscreen_toggle)
        self.Bind(wx.EVT_CHECKBOX, self.flipscreen_toggle_press, self.flipscreen_toggle)
        self.Bind(wx.EVT_CHECKBOX, self.waitblanking_toggle_press, self.waitblanking_toggle)

        self.Bind(wx.EVT_SLIDER, self.viewscale_slide, self.viewscaleX_slider)
        self.Bind(wx.EVT_SLIDER, self.viewscale_slide, self.viewscaleY_slider)

        self.Bind(wx.EVT_CHECKBOX, self.collect_return_movement_toggle_press, self.collect_return_movement_toggle)
        self.Bind(wx.EVT_CHECKBOX, self.enable_custom_stim_press, self.enable_custom_stim)
        self.Bind(wx.EVT_DIRPICKER_CHANGED, self.custom_stim_file_choose, self.custom_stim_file)
        self.Bind(wx.EVT_COMBOBOX, self.screen_choose_press, self.screen_choose)

        self.Bind(wx.EVT_BUTTON, self.apply_button_press, self.apply_button)
        self.Bind(wx.EVT_BUTTON, self.cancel_button_press, self.cancel_button)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("Settings")
        self.SetSize((300,450))
        self.fullscreen_toggle.SetValue(self.Parent.experiment_holder['settings']['fullscreen'])
        self.flipscreen_toggle.SetValue(self.Parent.experiment_holder['settings']['flipscreen'])
        self.waitblanking_toggle.SetValue(self.Parent.experiment_holder['settings']['waitblanking'])
        self.viewscaleX_slider.SetValue(int(self.Parent.experiment_holder['settings']['viewscale'][0]*100))
        self.viewscaleY_slider.SetValue(int(self.Parent.experiment_holder['settings']['viewscale'][1]*100))
        self.collect_return_movement_toggle.SetValue(self.Parent.experiment_holder['settings']['return_movement'])
        self.enable_custom_stim.SetValue(self.Parent.experiment_holder['settings']['custom_stim_enable'])
        self.custom_stim_file.SetPath(self.Parent.experiment_holder['settings']['custom_stim_file'])
        self.screen_choose.SetSelection(self.Parent.experiment_holder['settings']['screen'])
        if self.Parent.experiment_holder['settings']['custom_stim_enable'] == False:
            self.custom_stim_file.Disable()
        else:
            self.custom_stim_file.Enable()
    def __do_layout(self):
        horizontal_main = wx.BoxSizer(wx.HORIZONTAL)
        vertical_1 = wx.BoxSizer(wx.VERTICAL)
        vertical_1.Add(self.fullscreen_toggle, 0, wx.TOP, 2)
        vertical_1.Add(self.flipscreen_toggle, 0, wx.TOP, 2)
        vertical_1.Add(self.waitblanking_toggle, 0, wx.TOP, 2)
        vertical_1.Add(self.viewscaleX_text, 0, wx.TOP, 2)
        vertical_1.Add(self.viewscaleX_slider, 0, wx.EXPAND, 2)
        vertical_1.Add(self.viewscaleY_text, 0, wx.TOP, 2)
        vertical_1.Add(self.viewscaleY_slider, 0, wx.EXPAND, 2)
        vertical_1.Add(self.screen_choose_text, 0, wx.TOP, 2)
        vertical_1.Add(self.screen_choose, 0, wx.TOP, 2)
        vertical_1.Add(self.collect_return_movement_toggle, 0, wx.TOP, 2)
        vertical_1.Add(self.enable_custom_stim, 0, wx.TOP, 2)
        vertical_1.Add(self.custom_stim_file, 0, wx.TOP, 2)
        vertical_1.Add(self.apply_button, 0, wx.BOTTOM, 2)
        vertical_1.Add(self.cancel_button, 0, wx.BOTTOM, 2)
        horizontal_main.Add(vertical_1, 1, 0, 0)

        self.SetSizer(horizontal_main)
        self.Layout()

    def fullscreen_toggle_press(self, event):
        self.fullscreen_state = event.IsChecked()
        event.Skip()
    def flipscreen_toggle_press(self, event):
        self.flipscreen_state = event.IsChecked()
        event.Skip()
    def waitblanking_toggle_press(self, event):
        self.waitblanking_state = event.IsChecked()
        event.Skip()

    def viewscale_slide(self, event):  # wxGlade: MyFrame.<event_handler>
        self.viewscale_state = [self.viewscaleX_slider.GetValue()/100., self.viewscaleY_slider.GetValue()/100.]
        #self.experiment_holder['settings']['viewscale'] = self.viewscale_state
        event.Skip()

    def collect_return_movement_toggle_press(self, event):
        self.collect_return_movement_state = event.IsChecked()
        event.Skip()

    def enable_custom_stim_press(self, event):
        self.enable_custom_stim_state = event.IsChecked()
        if self.enable_custom_stim_state == False:
            self.custom_stim_file.Disable()
        elif self.enable_custom_stim_state == True:
            self.custom_stim_file.Enable()
        event.Skip()

    def custom_stim_file_choose(self, event):
        self.custom_stim_file_state = event.GetPath()
        event.Skip()
    def screen_choose_press(self, event):
        self.screen_choose_state = event.GetString()
        event.Skip()


    def apply_button_press(self, event):
        self.Parent.experiment_holder['settings']['fullscreen'] = self.fullscreen_state
        self.Parent.experiment_holder['settings']['flipscreen'] = self.flipscreen_state
        self.Parent.experiment_holder['settings']['waitblanking'] = self.waitblanking_state
        self.Parent.experiment_holder['settings']['viewscale'] = self.viewscale_state
        self.Parent.experiment_holder['settings']['return_movement'] = self.collect_return_movement_state
        self.Parent.experiment_holder['settings']['custom_stim_enable'] = self.enable_custom_stim_state
        self.Parent.experiment_holder['settings']['custom_stim_file'] = self.custom_stim_file_state
        self.Parent.experiment_holder['settings']['screen'] = int(self.screen_choose_state)
        self.Destroy()
        event.Skip()
    def cancel_button_press(self, event):
        self.Destroy()
        event.Skip()
###################### PREPROCESSING FRAME ##########################
class PreprocessFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        ########## Initial Presets#############
        self.cfg = {}
        self.highlit_participant = ""
        self.highlit_ignore = ""
        self.highlit_task = ""
        self.highlit_task_ignore = ""
        self.participant_list = []
        self.participant_list_trimmed = []
        self.task_list = []
        self.std_list = []
        for i in range(1, 9):
            self.std_list.append(str(i*0.5))
        ########## Dynamic Data ###############
        self.participant_list_dynamic = []
        self.ignore_list_dynamic = []
        self.task_list_dynamic = []
        self.ignore_task_list_dynamic = []

        ####################################
        self.list_box_size = [150,300]
        self.switch_button_size = [50,50]
        self.participant_static_text = wx.StaticText(self, wx.ID_ANY, ("Participants"))
        self.ignore_participant_static_text = wx.StaticText(self, wx.ID_ANY, ("Ignore Participants"))
        self.task_static_text = wx.StaticText(self, wx.ID_ANY, ("Tasks"))
        self.ignore_task_static_text = wx.StaticText(self, wx.ID_ANY, ("Ignore Tasks"))

        self.participant_pool = wx.ListBox(self, wx.ID_ANY, choices=[])
        self.ignore_pool = wx.ListBox(self, wx.ID_ANY, choices=[])
        self.task_pool = wx.ListBox(self, wx.ID_ANY, choices=[])
        self.ignore_task_pool = wx.ListBox(self, wx.ID_ANY, choices=[])
        #self.participant_to_ignore = wx.Button(self, wx.ID_ANY, (u"\u2bab"))
        self.participant_to_ignore = wx.Button(self, wx.ID_ANY, (u">>"))
        #self.ignore_to_participant = wx.Button(self, wx.ID_ANY, (u"\u2ba8"))
        self.ignore_to_participant = wx.Button(self, wx.ID_ANY, (u"<<"))
        #self.task_to_ignore = wx.Button(self, wx.ID_ANY, (u"\u2bab"))
        self.task_to_ignore = wx.Button(self, wx.ID_ANY, (u">>"))
        #self.ignore_to_task = wx.Button(self, wx.ID_ANY, (u"\u2ba8"))
        self.ignore_to_task = wx.Button(self, wx.ID_ANY, (u"<<"))
        self.preprocess_button = wx.Button(self, wx.ID_ANY, ("Pre-Process Participants"))
        self.std_menu_list = wx.ComboBox(self, wx.ID_ANY, value='2.0', choices = self.std_list, style=wx.CB_DROPDOWN)
        ####################################
        self.one_or_split_rbutton = wx.RadioBox(self, wx.ID_ANY, label='File output style', choices=['One file','Split by task'], style=wx.RA_SPECIFY_ROWS, majorDimension=2)
        self.output_type_text = wx.StaticText(self, wx.ID_ANY, 'Output type')
        self.trial = wx.CheckBox(self, wx.ID_ANY, label='Trial')
        self.block = wx.CheckBox(self, wx.ID_ANY, label='Block')
        self.target = wx.CheckBox(self, wx.ID_ANY, label='Target')
        self.error_style = wx.RadioBox(self, wx.ID_ANY, label='Dependent variable', choices=['Cursor error', 'Reach Deviation'], style=wx.RA_SPECIFY_ROWS, majorDimension=2)
        self.outlier_removal_check = wx.CheckBox(self, wx.ID_ANY, label="Remove outliers by std")
        self.outlier_removal_window_check = wx.CheckBox(self, wx.ID_ANY, label="Remove outliers by window")
#        self.upper_slider_text = wx.StaticText(self, wx.ID_ANY, "Upper bound")
        self.lower_slider_text = wx.StaticText(self, wx.ID_ANY, "Half window size (deg)")
        self.outlier_removal_window_lower_slider = wx.Slider(self, wx.ID_ANY, minValue = 15, maxValue = 90, value=90, style = wx.SL_HORIZONTAL | wx.SL_LABELS)
#        self.outlier_removal_window_upper_slider = wx.Slider(self, wx.ID_ANY, minValue = 30, maxValue = 90, value=30, style = wx.SL_HORIZONTAL | wx.SL_LABELS)

#        self.output_type = wx.RadioBox(self, wx.ID_ANY, label='Output type', choices=['Trial','Block','Target'], style=wx.RA_SPECIFY_ROWS, majorDimension=3)
#        self.error_text = wx.StaticText(self, wx.ID_ANY, "Error output")
#        self.error_cbox_1 = wx.CheckBox(self, wx.ID_ANY, label='Cursor error')
#        self.error_cbox_2 = wx.CheckBox(self, wx.ID_ANY, label='Reach deviation')

        self.Bind(wx.EVT_LISTBOX, self.participant_pool_click, self.participant_pool)
        self.Bind(wx.EVT_LISTBOX, self.ignore_pool_click, self.ignore_pool)
        self.Bind(wx.EVT_LISTBOX, self.task_pool_click, self.task_pool)
        self.Bind(wx.EVT_LISTBOX, self.ignore_task_pool_click, self.ignore_task_pool)
        self.Bind(wx.EVT_BUTTON, self.participant_to_ignore_click, self.participant_to_ignore)
        self.Bind(wx.EVT_BUTTON, self.ignore_to_participant_click, self.ignore_to_participant)
        self.Bind(wx.EVT_BUTTON, self.task_to_ignore_click, self.task_to_ignore)
        self.Bind(wx.EVT_BUTTON, self.ignore_to_task_click, self.ignore_to_task)
        self.Bind(wx.EVT_BUTTON, self.preprocess_button_click, self.preprocess_button)
        self.Bind(wx.EVT_RADIOBOX, self.one_or_split_rbutton_click, self.one_or_split_rbutton)
        self.Bind(wx.EVT_CHECKBOX, self.trial_click, self.trial)
        self.Bind(wx.EVT_CHECKBOX, self.block_click, self.block)
        self.Bind(wx.EVT_CHECKBOX, self.target_click, self.target)
        self.Bind(wx.EVT_RADIOBOX, self.error_style_click, self.error_style)
        self.Bind(wx.EVT_CHECKBOX, self.outlier_removal_check_click, self.outlier_removal_check)
        self.Bind(wx.EVT_COMBOBOX, self.std_menu_list_choose, self.std_menu_list)
        self.Bind(wx.EVT_CHECKBOX, self.outlier_removal_window_check_click, self.outlier_removal_window_check)
        self.Bind(wx.EVT_SLIDER, self.outlier_removal_window_lower_slider_choose, self.outlier_removal_window_lower_slider)
#        self.Bind(wx.EVT_SLIDER, self.outlier_removal_window_upper_slider_choose, self.outlier_removal_window_upper_slider)
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("Pre-Process")
        self.SetSize((735,570))
#        self.testButton.SetMinSize((1,1))
        self.participant_pool.SetMinSize(self.list_box_size)
        self.ignore_pool.SetMinSize(self.list_box_size)
        self.task_pool.SetMinSize(self.list_box_size)
        self.ignore_task_pool.SetMinSize(self.list_box_size)
        self.participant_to_ignore.SetMinSize(self.switch_button_size)
        self.ignore_to_participant.SetMinSize(self.switch_button_size)
        self.task_to_ignore.SetMinSize(self.switch_button_size)
        self.ignore_to_task.SetMinSize(self.switch_button_size)
        self.block.SetValue(True)
        self.trial.SetValue(True)
#        self.outlier_removal_slider.Disable()
#        self.std_menu_list.Enable()
        self.outlier_removal_check.SetValue(True)
        self.outlier_removal_window_check.SetValue(True)
        self.cfg['dependent_variable'] = self.error_style.GetString(self.error_style.GetSelection()).lower()
        self.cfg['trial'] = self.trial.IsChecked()
        self.cfg['block'] = self.block.IsChecked()
        self.cfg['target'] = self.target.IsChecked()
        self.cfg['output_style'] = self.one_or_split_rbutton.GetString(self.one_or_split_rbutton.GetSelection()).lower()
        self.cfg['outliers'] = self.outlier_removal_check.IsChecked()
        self.cfg['outlier_scale'] = float(self.std_menu_list.GetValue())
        self.cfg['outliers_win'] = self.outlier_removal_window_check.IsChecked()
#        self.cfg['window_upper'] = self.outlier_removal_window_upper_slider.GetValue()
        self.cfg['window_limit'] = self.outlier_removal_window_lower_slider.GetValue()

        ############ Pull Data from Parent frame ##########
#        self.participant_list = listdir(path.join("data", self.Parent.current_experiment_name))
#        self.participant_list = [x for x in self.participant_list if '.csv' not in x]
#        for i in self.participant_list:
#            self.participant_list_trimmed.append(i.replace(".csv", ""))
#        if len(self.participant_list_trimmed) == 0:
#            self.participant_list_trimmed = ["Empty"]
#        self.participant_pool.Set(self.participant_list_trimmed)
#        self.participant_list_dynamic = deepcopy(self.participant_list_trimmed)
#        del self.participant_list_trimmed[:]
        self.Parent.participant_markers = {0:[], 1:[], 2:[], 3:[]}
        self.Parent.generate_participant_markers()
        self.participant_list_dynamic = deepcopy(self.Parent.participant_markers[0])
        self.participant_pool.Set(self.participant_list_dynamic)
        for i in range(0, len(self.Parent.current_experiment)):
            if (self.Parent.current_experiment[i]['trial_type'] != 'pause'):
                self.task_list.append(self.Parent.current_experiment[i]["task_name"])
        self.task_list_dynamic = deepcopy(self.task_list)
        self.task_pool.Set(self.task_list)

    def __do_layout(self):
        horizontal_main = wx.BoxSizer(wx.HORIZONTAL)
        vertical_pp = wx.BoxSizer(wx.VERTICAL)
        vertical_pp.Add(self.participant_static_text, 0, wx.CENTER, 5)
        vertical_pp.Add(self.participant_pool, 0, 0, 2)
        vertical_pp.Add(self.error_style, 0, 0, 2)
        vertical_pp.Add(self.preprocess_button, 0, 0, 2)
        horizontal_main.Add(vertical_pp)
        vertical_1 = wx.BoxSizer(wx.VERTICAL)
        vertical_1.Add(self.participant_to_ignore, 0, wx.TOP, 100)
        vertical_1.Add(self.ignore_to_participant, 0, 0, 2)
        horizontal_main.Add(vertical_1)
        vertical_ip = wx.BoxSizer(wx.VERTICAL)
        vertical_ip.Add(self.ignore_participant_static_text, 0, wx.CENTER, 5)
        vertical_ip.Add(self.ignore_pool, 0, wx.RIGHT, 2)
        vertical_ip.Add(self.output_type_text, 0, 0, 2)
        vertical_ip.Add(self.trial, 0, 0, 2)
        vertical_ip.Add(self.block, 0, 0, 2)
        vertical_ip.Add(self.target, 0, 0, 2)
        horizontal_main.Add(vertical_ip)
        vertical_tp = wx.BoxSizer(wx.VERTICAL)
        vertical_tp.Add(self.task_static_text, 0, wx.CENTER, 5)
        vertical_tp.Add(self.task_pool, 0, 0, 2)
        vertical_tp.Add(self.one_or_split_rbutton, 0, 0, 2)
        horizontal_main.Add(vertical_tp)
        vertical_2 = wx.BoxSizer(wx.VERTICAL)
        vertical_2.Add(self.task_to_ignore, 0, wx.TOP, 100)
        vertical_2.Add(self.ignore_to_task, 0, 0, 2)
        horizontal_main.Add(vertical_2)
        vertical_itp = wx.BoxSizer(wx.VERTICAL)
        vertical_itp.Add(self.ignore_task_static_text, 0, wx.CENTER, 5)
        vertical_itp.Add(self.ignore_task_pool, 0, 0, 2)
        vertical_itp.Add(self.outlier_removal_window_check, 0, 0, 2)
#        vertical_itp.Add(self.upper_slider_text, 0, 0, 2)
#        vertical_itp.Add(self.outlier_removal_window_upper_slider, 0, wx.EXPAND, 2)
        vertical_itp.Add(self.lower_slider_text, 0, 0, 2)
        vertical_itp.Add(self.outlier_removal_window_lower_slider, 0, wx.EXPAND, 2)
        vertical_itp.Add(self.outlier_removal_check, 0, 0, 2)
        vertical_itp.Add(self.std_menu_list, 0, wx.EXPAND, 2)
        horizontal_main.Add(vertical_itp)

        self.SetSizer(horizontal_main)
        self.Layout()

    def participant_pool_click(self, event):
        self.highlit_participant = event.GetString()
        event.Skip()
    def ignore_pool_click(self, event):
        self.highlit_ignore = event.GetString()
        event.Skip()
    def task_pool_click(self, event):
        self.highlit_task = event.GetString()
        event.Skip()
    def ignore_task_pool_click(self, event):
        self.highlit_task_ignore = event.GetString()
        event.Skip()
    def participant_to_ignore_click(self, event):
        if self.highlit_participant not in self.ignore_list_dynamic:
            self.ignore_list_dynamic.append(self.highlit_participant)
            self.participant_list_dynamic.remove(self.highlit_participant)
            self.ignore_pool.Set(self.ignore_list_dynamic)
            self.participant_pool.Set(self.participant_list_dynamic)
        event.Skip()
    def ignore_to_participant_click(self, event):
        if self.highlit_ignore not in self.participant_list_dynamic:
            self.participant_list_dynamic.append(self.highlit_ignore)
            self.ignore_list_dynamic.remove(self.highlit_ignore)
            self.participant_pool.Set(self.participant_list_dynamic)
            self.ignore_pool.Set(self.ignore_list_dynamic)
        event.Skip()
    def task_to_ignore_click(self, event):
        if self.highlit_task not in self.ignore_task_list_dynamic:
            self.ignore_task_list_dynamic.append(self.highlit_task)
            self.task_list_dynamic.remove(self.highlit_task)
            self.task_pool.Set(self.task_list_dynamic)
            self.ignore_task_pool.Set(self.ignore_task_list_dynamic)
        event.Skip()
    def ignore_to_task_click(self, event):
        if self.highlit_task_ignore not in self.task_list_dynamic:
            self.task_list_dynamic.append(self.highlit_task_ignore)
            self.ignore_task_list_dynamic.remove(self.highlit_task_ignore)
            self.task_pool.Set(self.task_list_dynamic)
            self.ignore_task_pool.Set(self.ignore_task_list_dynamic)
        event.Skip()
    def one_or_split_rbutton_click(self, event):
        self.cfg['output_style'] = event.GetString().lower()
        event.Skip()
    def trial_click(self, event):
        self.cfg['trial'] = event.IsChecked()
        event.Skip()
    def block_click(self, event):
        self.cfg['block'] = event.IsChecked()
        event.Skip()
    def target_click(self, event):
        self.cfg['target'] = event.IsChecked()
        event.Skip()
    def error_style_click(self, event):
        self.cfg['dependent_variable'] = event.GetString().lower()
        event.Skip()
    def outlier_removal_check_click(self, event):
        if event.IsChecked() == True:
#            self.outlier_removal_slider.Enable()
            self.std_menu_list.Enable()
        elif event.IsChecked() == False:
#            self.outlier_removal_slider.Disable()
            self.std_menu_list.Disable()
        self.cfg['outliers'] = event.IsChecked()
        event.Skip()
#    def outlier_removal_slider_choose(self, event):
#        self.cfg['outlier_scale'] = float(event.GetInt())/float(10)
#        event.Skip()
    def std_menu_list_choose(self, event):
        self.cfg['outlier_scale'] = float(event.GetString())
        event.Skip()
    def outlier_removal_window_check_click(self, event):
        if event.IsChecked() == True:
            self.outlier_removal_window_lower_slider.Enable()
#            self.outlier_removal_window_upper_slider.Enable()
#            self.upper_slider_text.Enable()
            self.lower_slider_text.Enable()
        elif event.IsChecked() == False:
            self.outlier_removal_window_lower_slider.Disable()
#            self.outlier_removal_window_upper_slider.Disable()
#            self.upper_slider_text.Disable()
            self.lower_slider_text.Disable()
        self.cfg['outliers_win'] = event.IsChecked()
        event.Skip()
#    def outlier_removal_window_upper_slider_choose(self, event):
#        self.cfg['window_upper'] = event.GetInt()
#        print event.GetInt()
#        event.Skip()
    def outlier_removal_window_lower_slider_choose(self, event):
        self.cfg['window_limit'] = event.GetInt()
        event.Skip()

    def preprocess_button_click(self, event):
        try:
            preprocessed_data = pp.process_participants(self.participant_list_dynamic, self.task_list_dynamic, self.Parent.experiment_holder, self.cfg)
            if isinstance(preprocessed_data, basestring):
                participant_name = preprocessed_data.split("/")[2]
                dlg_warning = wx.MessageDialog(self, "(" + preprocessed_data + ")" + " contains incomplete data!\n\n" + "From participant: " + participant_name + "\n\nConsider ignoring for pre-processing or deleting participant entirely", style=wx.OK|wx.CENTRE|wx.ICON_WARNING)
                dlg_warning.ShowModal()
                dlg_warning.Destroy()
                return

            p_index = array([self.cfg['trial'], self.cfg['block'], self.cfg['target']]).nonzero()[0]
            types = ['trial', 'block', 'target']
            for idx in p_index:
                outtype = types[idx]
                file_name = "%s_%s"%(self.Parent.current_experiment_name, outtype)
                if self.cfg['output_style'] == 'one file':
                    file_path = path.join("data",self.Parent.current_experiment_name, file_name + ".csv")
                    with open(file_path, 'wb') as csvfile:
                        csvwriter = csv.writer(csvfile)
                        csvwriter.writerow(preprocessed_data[0][idx])
                        csvwriter.writerows(preprocessed_data[1][idx])
                if self.cfg['output_style'] == 'split by task':
                    for split, task in enumerate(self.task_list_dynamic):
                        file_path = path.join("data",self.Parent.current_experiment_name, file_name + "_" + task +".csv")
                        task_index = (array(preprocessed_data[1][idx])[:,0] == task).nonzero()[0]
                        task_data = array(preprocessed_data[1][idx])[task_index]
                        with open(file_path, 'wb') as csvfile:
                            csvwriter = csv.writer(csvfile)
                            csvwriter.writerow(preprocessed_data[0][idx])
                            csvwriter.writerows(task_data)
                self.Destroy()
        except Exception as e:
            traceback.print_exc()
        event.Skip()


# Score System Frame
class ScoreFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        self.SetTitle("Scoring System Settings")
        self.SetSize((735,250))

    def __set_properties__(self):
        print("implement me")

    def __do_layout(self):
        print("implement me")

# end of class MyFrame
class MyApp(wx.App):
    def OnInit(self):
        PyVMEC = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(PyVMEC)
        PyVMEC.Show()
        return True

# end of class MyApp

#if __name__ == "__main__":
def start():
    install("app") # replace with the appropriate catalog name

    app = MyApp(0)
    app.MainLoop()
