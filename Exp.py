# with functions that run a trial sequence as passed to it, and stores the data appropriately
import os
from psychopy import event, visual, core
import numpy as np
import math
import pandas as pd
import os.path
import random
import Tkinter as tk
import copy
from ctypes import *
from time import time


root = tk.Tk()
def addWorkSpaceLimits(cfg = {}):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    trimmed_width = int((float(2)/float(3))*float(screen_width))
    trimmed_height = int((float(2)/float(3))*float(screen_height))
    if (trimmed_width < 2*trimmed_height):
        active_height = trimmed_width/2
    else:
        active_height = trimmed_height/2   
    active_width = trimmed_width
    cfg['active_width'] = active_width
    cfg['active_height'] = active_height
    return cfg

class myMouse:
  Xlib = CDLL("libX11.so.6")
  display = Xlib.XOpenDisplay(None)
  if display == 0: sys.exit(2)
  w = Xlib.XRootWindow(display, c_int(0))
  (root_id, child_id) = (c_uint32(), c_uint32())
  (root_x, root_y, win_x, win_y) = (c_int(), c_int(), c_int(), c_int())
  mask = c_uint()
  
  width = root.winfo_screenwidth()
  height = root.winfo_screenheight()

  def Pos(self):
    ret = self.Xlib.XQueryPointer(self.display, c_uint32(self.w), byref(self.root_id), byref(self.child_id), byref(self.root_x), byref(self.root_y), byref(self.win_x), byref(self.win_y), byref(self.mask))
    if ret == 0: sys.exit(1)
    return [self.root_x.value - (self.width/2), -1 * (self.root_y.value - (self.height/2)), time()] # c_int can't be used by regular Python to do math, but the values of c_ints are ints - also, we return the current time

def myRounder(x, base):
    return int(base * round(float(x)/base))    
    
def task_namer(given_task, function):
    if (function == True):
        if (given_task == "cursor"):
            return "Cursor"
        if (given_task == "no_cursor"):
            return "No Cursor"
        if (given_task == "pause"):
            return "Pause Task"
        if (given_task == "error_clamp"):
            return "Error Clamp"
    elif (function == False):
        if (given_task == "Cursor"):
            return "cursor"
        if (given_task == "No Cursor"):
            return "no_cursor"
        if (given_task == "Pause Task"):
            return "pause"
        if (given_task == "Error Clamp"):
            return "error_clamp"
            
def task_num(given_task, function):
    if (function == True):
        if (given_task == "cursor"):
            return 0
        if (given_task == "no_cursor"):
            return 1
        if (given_task == "pause"):
            return 2
        if (given_task == "error_clamp"):
            return 3
    elif (function == False):
        if (given_task == 0):
            return "cursor"
        if (given_task == 1):
            return "no_cursor"
        if (given_task == 2):
            return "pause"
        if (given_task == 3):
            return "error_clamp"
def cart2pol(coord=[]):
    rho = np.sqrt(coord[0]**2 + coord[1]**2)
    phi = np.arctan2(coord[1], coord[0])
    return [rho, phi]

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)
        
def get_dist(select_pos, target_pos):
    vector = [target_pos[0] - select_pos[0], target_pos[1] - select_pos[1]]
    return np.linalg.norm(vector)
def get_vect(select_pos, target_pos):
    vector = [target_pos[0] - select_pos[0], target_pos[1] - select_pos[1]]
    return vector

def get_uvect(vector):
    uvect = vector/np.linalg.norm(vector)
    return uvect
def get_vector_projection(moving_vect, static_vect):
    static_uvect = get_uvect(static_vect)
    scalar_proj = np.dot(moving_vect, static_uvect)
    return scalar_proj*static_uvect      
def angle_split(min_angle, max_angle, num_splits):
    angles = []
    for i in range(0, num_splits):
        if (num_splits%2 == 1):
            new_angle = min_angle + int(math.ceil(((float(max_angle) - float(min_angle))/(float(num_splits) - 1))))*i
        else:
            new_angle = min_angle + int(math.floor(((float(max_angle) - float(min_angle))/(float(num_splits) - 1))))*i
        if (i == num_splits - 1):
            new_angle = max_angle
        angles.append(new_angle)
    return angles
    
def experiment_cursor(angle, distance, cfg={}):
    end_X = distance * math.cos(math.radians(angle))
    end_Y = (distance * math.sin(math.radians(angle))) - cfg['active_height']/2
    ### Creates Window object
    myWin=cfg['win']
    ### Creates Mouse object
    if (cfg['poll_type'] == 'psychopy'):
        myMouse = cfg['mouse']
        ### Gets current CPU Time
        myTime = cfg['time']
    elif (cfg['poll_type'] == 'x11'):
        myMouse = cfg['x11_mouse']
        ### Gets current CPU Time
        myTime = myMouse.Pos()[2]
    
    ### Creates cursor circle Object
    myCircle = cfg['cursor_circle']
    ### Creates a circle object to be used as starting point      
    startCircle = cfg['start_circle']
    ### Creates a Target circle
    endCircle = cfg['end_circle']
    ### Define Parameters here
    startPos=cfg['starting_pos']
    endPos=[end_X, end_Y]   
    ### Instantiating Checking Variables Here
    touchStart=False
    phase_one = False
    phase_two = False
    show_target = False
    show_home = True
    ### These variables record timestamps and mouse positions (Used to calculate mouse velocity)
    prev_timestamp = 0
    prev_X = 0
    prev_Y = 0
    velocity = 0
    ### Instantiating return dictionary and arrays within it
    timePos_dict = {}
    timeArray = []
    mouseposXArray = []
    mouseposYArray = []
    cursorposXArray = []
    cursorposYArray = []
    ### target circle position
    endCircle.setPos(endPos)
    ### starting circle 
    startCircle.setPos(startPos)
    if (cfg['poll_type'] == 'psychopy'):
        mousePos=myMouse.getPos()
    elif (cfg['poll_type'] == 'x11'):
        mousePos = [myMouse.Pos()[0], myMouse.Pos()[1]]
    circle_pos = mousePos
    myCircle.setPos(circle_pos)
    while (core.getTime() - cfg['time']) < 10:
        ### mouse Position
        if (cfg['poll_type'] == 'psychopy'):
            mousePos=myMouse.getPos()
            current_timestamp = core.getTime() - myTime
        elif (cfg['poll_type'] == 'x11'):
            mousePos = [myMouse.Pos()[0], myMouse.Pos()[1]]
            current_timestamp = myMouse.Pos()[2] - myTime
        

        if (show_home == True):
            startCircle.draw()
        if (show_target == True):
            endCircle.draw()
            
        ### Cursor Circle
        current_pos = mousePos
        if (cfg['lag'] == 0):
            rotated_X = current_pos[0]*math.cos(math.radians(cfg['rotation_angle'])) - current_pos[1]*math.sin(math.radians(cfg['rotation_angle']))
            rotated_Y = current_pos[0]*math.sin(math.radians(cfg['rotation_angle'])) + current_pos[1]*math.cos(math.radians(cfg['rotation_angle']))
            circle_pos = [rotated_X, rotated_Y]
            myCircle.setPos(circle_pos)
        else:            
            if (len(cursorposXArray) <= cfg['lag']):
                rotated_X = circle_pos[0]
                rotated_Y = circle_pos[1]
            if (len(cursorposXArray) > cfg['lag']):
                rotated_X = mouseposXArray[-cfg['lag']]*math.cos(math.radians(cfg['rotation_angle'])) - (mouseposYArray[-cfg['lag']] - cfg['active_height']/2)*math.sin(math.radians(cfg['rotation_angle']))
                rotated_Y = mouseposXArray[-cfg['lag']]*math.sin(math.radians(cfg['rotation_angle'])) + (mouseposYArray[-cfg['lag']] - cfg['active_height']/2)*math.cos(math.radians(cfg['rotation_angle']))
                circle_pos = [rotated_X, rotated_Y]
                myCircle.setPos(circle_pos)
            
        myCircle.draw()
#        print(circle_pos, core.getTime() - cfg['time']) 
        ### Adding Values to appropriate Arrays
        timeArray.append(current_timestamp)
        mouseposXArray.append(current_pos[0])
        mouseposYArray.append(current_pos[1] + cfg['active_height']/2)
        cursorposXArray.append(rotated_X)
        cursorposYArray.append(rotated_Y + cfg['active_height']/2)
        
        
        if (prev_timestamp != 0):
            change_in_time = current_timestamp - prev_timestamp
            velocity = (np.linalg.norm([current_pos[0] - prev_X, current_pos[1] - prev_Y]))/change_in_time
#            print (velocity)
            
        prev_timestamp = current_timestamp
        prev_X = current_pos[0]
        prev_Y = current_pos[1]
        
    #    if (all(mousePos)==all(startPos)):
        if ((get_dist(circle_pos, startPos) < 10) and velocity < 35 and touchStart == False):
            touchStart=True
            show_target = True
            show_home = False
            phase_one = True
          
        if (touchStart==True and phase_one == True):          
            if ((get_dist(circle_pos, endPos) < 10) and velocity < 35 and cfg['terminal_feedback'] == False):
                phase_two = True
                show_target = False
                show_home = True
            ### Terminal FeedBack Portion
            elif ((get_dist(circle_pos, startPos) >= cfg['terminal_multiplier']*get_dist(startPos, endPos)) and cfg['terminal_feedback'] == True):
                timer = core.getTime()
                while ((core.getTime() - timer) < cfg['terminal_feedback_time']):
                    myCircle.draw()
                    if (cfg['poll_type'] == 'psychopy'):
                        timeArray.append(core.getTime() - myTime)
                        mouseposXArray.append(myMouse.getPos()[0])
                        mouseposYArray.append(myMouse.getPos()[1] + cfg['active_height']/2)
                    elif (cfg['poll_type'] == 'x11'):
                        timeArray.append(myMouse.Pos()[2] - myTime)
                        mouseposXArray.append(myMouse.Pos()[0])
                        mouseposYArray.append(myMouse.Pos()[1] + cfg['active_height']/2)
                    cursorposXArray.append(rotated_X)
                    cursorposYArray.append(rotated_Y + cfg['active_height']/2)
                    myWin.flip()
                
                timePos_dict['task_num'] = cfg['task_num']
                timePos_dict['trial_num'] = cfg['trial_num']
                timePos_dict['trial_type'] = cfg['trial_type']
                timePos_dict['target_angle_degrees'] = angle
                timePos_dict['homex_px'] = startPos[0]
                timePos_dict['homey_px'] = startPos[1] + cfg['active_height']/2
                timePos_dict['targetx_px'] = endPos[0]
                timePos_dict['targety_px'] = endPos[1] + cfg['active_height']/2
                timePos_dict['time_s'] = timeArray
                timePos_dict['mousex_px'] = mouseposXArray
                timePos_dict['mousey_px'] = mouseposYArray
                timePos_dict['cursorx_px'] = cursorposXArray
                timePos_dict['cursory_px'] = cursorposYArray
                timePos_dict['terminal_feedback_boolean'] = cfg['terminal_feedback']
                return timePos_dict
            
        if (phase_two == True and (get_dist(circle_pos, startPos) < 10) and velocity < 35):
            timePos_dict['task_num'] = cfg['task_num']
            timePos_dict['trial_num'] = cfg['trial_num']
            timePos_dict['trial_type'] = cfg['trial_type']
            timePos_dict['target_angle_degrees'] = angle
            timePos_dict['homex_px'] = startPos[0]
            timePos_dict['homey_px'] = startPos[1] + cfg['active_height']/2
            timePos_dict['targetx_px'] = endPos[0]
            timePos_dict['targety_px'] = endPos[1] + cfg['active_height']/2
            timePos_dict['time_s'] = timeArray
            timePos_dict['mousex_px'] = mouseposXArray
            timePos_dict['mousey_px'] = mouseposYArray
            timePos_dict['cursorx_px'] = cursorposXArray
            timePos_dict['cursory_px'] = cursorposYArray
            timePos_dict['terminal_feedback_boolean'] = cfg['terminal_feedback']
            return timePos_dict
        myWin.flip()
    timePos_dict['task_num'] = cfg['task_num']
    timePos_dict['trial_num'] = cfg['trial_num']
    timePos_dict['trial_type'] = cfg['trial_type']
    timePos_dict['target_angle_degrees'] = angle
    timePos_dict['homex_px'] = startPos[0]
    timePos_dict['homey_px'] = startPos[1] + cfg['active_height']/2
    timePos_dict['targetx_px'] = endPos[0]
    timePos_dict['targety_px'] = endPos[1] + cfg['active_height']/2
    timePos_dict['time_s'] = timeArray
    timePos_dict['mousex_px'] = mouseposXArray
    timePos_dict['mousey_px'] = mouseposYArray
    timePos_dict['cursorx_px'] = cursorposXArray
    timePos_dict['cursory_px'] = cursorposYArray
    timePos_dict['terminal_feedback_boolean'] = cfg['terminal_feedback']
    #myWin.close()
    return timePos_dict
    
#################################### NO CURSOR ###############################    
def experiment_no_cursor(angle, distance, cfg={}):
    end_X = distance * math.cos(math.radians(angle))
    end_Y = (distance * math.sin(math.radians(angle))) - cfg['active_height']/2
    ### Creates Window object
    myWin=cfg['win']
    ### Creates Mouse object
    myMouse = cfg['mouse']
    ### Gets current CPU Time
    if (cfg['poll_type'] == 'psychopy'):
        myTime = cfg['time']
        myMouse = cfg['mouse']
    elif (cfg['poll_type'] == 'x11'):
        myMouse = cfg['x11_mouse']
        myTime = myMouse.Pos()[2]
    ### Creates cursor circle Object
    myCircle = cfg['cursor_circle']
    ### Creates a circle object to be used as starting point      
    startCircle = cfg['start_circle']
    ### Creates a Target circle
    endCircle = cfg['end_circle']
    ### Define Parameters here
    startPos=cfg['starting_pos']
    endPos=[end_X, end_Y]   
    ### Instantiating Checking Variables Here
    touchStart = False
#    doneTrial = False
    showStart = True
    showCursor = True
    timerSet = False
    phase_one = False
    showTarget = False
#    phase_two = False
    velocity = 0
    ### These variables record timestamps and mouse positions (Used to calculate mouse velocity)
    prev_timestamp = 0
    timer_timestamp = 0
    stop_time = 0
    prev_X = 0
    prev_Y = 0
    ### Instantiating return dictionary and arrays within it
    timePos_dict = {}
    timeArray = []
    mouseposXArray = []
    mouseposYArray = []
    cursorposXArray = []
    cursorposYArray = []
    ### set end circle position
    endCircle.setPos(endPos)
    ### starting circle 
    startCircle.setPos(startPos)
    while (core.getTime() - cfg['time']) < 20:
        

        
        if (showStart == True):
            startCircle.draw()
        if (showTarget == True):
            endCircle.draw()

        
        ### Cursor Circle
        
        if (cfg['poll_type'] == 'psychopy'):
            current_pos = myMouse.getPos()
            current_timestamp = core.getTime() - myTime
        elif (cfg['poll_type'] == 'x11'):
            current_pos = [myMouse.Pos()[0], myMouse.Pos()[1]]
            current_timestamp = myMouse.Pos()[2] - myTime
        
        rotated_X = current_pos[0]*math.cos(math.radians(cfg['rotation_angle'])) - current_pos[1]*math.sin(math.radians(cfg['rotation_angle']))
        rotated_Y = current_pos[0]*math.sin(math.radians(cfg['rotation_angle'])) + current_pos[1]*math.cos(math.radians(cfg['rotation_angle']))
        circle_pos = [rotated_X, rotated_Y]
        myCircle.setPos(circle_pos)
#        myCircle.draw()
        if (showCursor == True):
            myCircle.draw() 
        
        ### Adding Values to appropriate Arrays
        timeArray.append(current_timestamp)
        mouseposXArray.append(current_pos[0])
        mouseposYArray.append(current_pos[1] + cfg['active_height']/2)
        cursorposXArray.append(rotated_X)
        cursorposYArray.append(rotated_Y + cfg['active_height']/2)
        
        ### Finding velocity of cursor here
        if (prev_timestamp != 0):
            change_in_time = current_timestamp - prev_timestamp
            velocity = (np.linalg.norm([current_pos[0] - prev_X, current_pos[1] - prev_Y]))/change_in_time
#            print (velocity)
            
        prev_timestamp = current_timestamp
        prev_X = current_pos[0]
        prev_Y = current_pos[1]
        

        if ((get_dist(circle_pos, startPos) < 10) and velocity < 35):
            touchStart=True
        
        if ((get_dist(circle_pos, startPos) > 10) and touchStart == True and phase_one == False):
            showStart = False
            showCursor = False
            
        ### stop timer
        if (velocity < 30 and timerSet == False and cfg['terminal_feedback'] == False):
            timer_timestamp = current_timestamp
            timerSet = True
        stop_time = current_timestamp - timer_timestamp
        if (velocity > 30 and timerSet == True and cfg['terminal_feedback'] == False):
            timerSet = False
            stop_time = 0  
        
#        print(stop_time, timerSet)
        ### Starting position was touched show target
        if (touchStart==True and phase_one==False):
            showTarget = True
            
 
            
        if (touchStart==True and phase_one==False and (get_dist(circle_pos, startPos) > get_dist(startPos, endPos)/2) and stop_time > 0.75 and cfg['terminal_feedback'] == False):
            phase_one = True
            showStart = True
            showTarget = False
            
#            print("Phase One Done")
        if (phase_one==True and (get_dist(circle_pos, startPos) < get_dist(startPos, endPos)/4)):
            showCursor = True
            if (get_dist(circle_pos, startPos) < 10):
                timePos_dict['task_num'] = cfg['task_num']
                timePos_dict['trial_num'] = cfg['trial_num']
                timePos_dict['trial_type'] = cfg['trial_type']
                timePos_dict['target_angle_degrees'] = angle
                timePos_dict['time_s'] = timeArray
                timePos_dict['homex_px'] = startPos[0]
                timePos_dict['homey_px'] = startPos[1] + cfg['active_height']/2
                timePos_dict['targetx_px'] = endPos[0]
                timePos_dict['targety_px'] = endPos[1] + cfg['active_height']/2
                timePos_dict['mousex_px'] = mouseposXArray
                timePos_dict['mousey_px'] = mouseposYArray
                timePos_dict['cursorx_px'] = cursorposXArray
                timePos_dict['cursory_px'] = cursorposYArray 
                timePos_dict['terminal_feedback_degrees'] = cfg['terminal_feedback']
                return timePos_dict
        ######## Terminal FeedBack Portion
                
        if (cfg['terminal_feedback'] == True and (get_dist(circle_pos, startPos) >= cfg['terminal_multiplier']*get_dist(startPos, endPos) + 5) and touchStart == True):
            timer = core.getTime()
            while ((core.getTime() - timer) < cfg['terminal_feedback_time']):
                myCircle.draw()
                if (cfg['poll_type'] == 'psychopy'):
                    timeArray.append(core.getTime() - myTime)
                    mouseposXArray.append(myMouse.getPos()[0])
                    mouseposYArray.append(myMouse.getPos()[1] + cfg['active_height']/2)
                elif (cfg['poll_type'] == 'x11'):
                    timeArray.append(myMouse.Pos()[2] - myTime)
                    mouseposXArray.append(myMouse.Pos()[0])
                    mouseposYArray.append(myMouse.Pos()[1] + cfg['active_height']/2)
                cursorposXArray.append(rotated_X)
                cursorposYArray.append(rotated_Y + cfg['active_height']/2)
                myWin.flip()
            timePos_dict['task_num'] = cfg['task_num']    
            timePos_dict['trial_num'] = cfg['trial_num']
            timePos_dict['trial_type'] = cfg['trial_type']
            timePos_dict['target_angle_degrees'] = angle
            timePos_dict['homex_px'] = startPos[0]
            timePos_dict['homey_px'] = startPos[1] + cfg['active_height']/2
            timePos_dict['targetx_px'] = endPos[0]
            timePos_dict['targety_px'] = endPos[1] + cfg['active_height']/2
            timePos_dict['time_s'] = timeArray
            timePos_dict['mousex_px'] = mouseposXArray
            timePos_dict['mousey_px'] = mouseposYArray
            timePos_dict['cursorx_px'] = cursorposXArray
            timePos_dict['cursory_px'] = cursorposYArray
            timePos_dict['terminal_feedback_degrees'] = cfg['terminal_feedback']
            return timePos_dict    
        myWin.flip()
    timePos_dict['task_num'] = cfg['task_num']
    timePos_dict['trial_num'] = cfg['trial_num']
    timePos_dict['trial_type'] = cfg['trial_type']
    timePos_dict['target_angle_degrees'] = angle
    timePos_dict['time_s'] = timeArray
    timePos_dict['homex_px'] = startPos[0]
    timePos_dict['homey_px'] = startPos[1] + cfg['active_height']/2
    timePos_dict['targetx_px'] = endPos[0]
    timePos_dict['targety_px'] = endPos[1] + cfg['active_height']/2
    timePos_dict['mousex_px'] = mouseposXArray
    timePos_dict['mousey_px'] = mouseposYArray
    timePos_dict['cursorx_px'] = cursorposXArray
    timePos_dict['cursory_px'] = cursorposYArray
    timePos_dict['terminal_feedback_degrees'] = cfg['terminal_feedback']

    return timePos_dict
    
######################################### ERROR CLAMP TRIAL #####################################
def experiment_error_clamp(angle, distance, cfg={}):
    end_X = distance * math.cos(math.radians(angle))
    end_Y = (distance * math.sin(math.radians(angle))) - cfg['active_height']/2
    ### Creates Window object
    myWin=cfg['win']
    ### Creates Mouse object
    if (cfg['poll_type'] == 'psychopy'):
        myMouse = cfg['mouse']
        ### Gets current CPU Time
        myTime = cfg['time']
    elif (cfg['poll_type'] == 'x11'):
        myMouse = cfg['x11_mouse']
        ### Gets current CPU Time
        myTime = myMouse.Pos()[2]
    
    ### Creates cursor circle Object
    myCircle = cfg['cursor_circle']
    ### Creates a circle object to be used as starting point      
    startCircle = cfg['start_circle']
    ### Creates a Target circle
    endCircle = cfg['end_circle']
    ### Define Parameters here
    startPos=cfg['starting_pos']
    endPos=[end_X, end_Y]   
    ### Instantiating Checking Variables Here
    touchStart=False
    phase_one = False
    phase_two = False
    show_target = False
    show_home = True
    ### These variables record timestamps and mouse positions (Used to calculate mouse velocity)
    prev_timestamp = 0
    prev_X = 0
    prev_Y = 0
    velocity = 0
    ### Instantiating return dictionary and arrays within it
    timePos_dict = {}
    timeArray = []
    mouseposXArray = []
    mouseposYArray = []
    cursorposXArray = []
    cursorposYArray = []
    ### target circle position
    endCircle.setPos(endPos)
    ### starting circle 
    startCircle.setPos(startPos)
    while (core.getTime() - cfg['time']) < 20:
        ### mouse Position
        if (cfg['poll_type'] == 'psychopy'):
            mousePos=myMouse.getPos()
            current_pos = mousePos
            current_timestamp = core.getTime() - myTime
        elif (cfg['poll_type'] == 'x11'):
            mousePos = [myMouse.Pos()[0], myMouse.Pos()[1]]
            current_pos = mousePos
            current_timestamp = myMouse.Pos()[2] - myTime
            
#        print(mousePos) 

        if (show_home == True):
            startCircle.draw()
        if (show_target == True):
            endCircle.draw()
        

        ### Cursor Circle
        
        
        
        rotated_X = current_pos[0]*math.cos(math.radians(cfg['rotation_angle'])) - current_pos[1]*math.sin(math.radians(cfg['rotation_angle']))
        rotated_Y = current_pos[0]*math.sin(math.radians(cfg['rotation_angle'])) + current_pos[1]*math.cos(math.radians(cfg['rotation_angle']))
        vector_proj_array = get_vector_projection(get_vect([prev_X, prev_Y], current_pos), get_vect(startPos, endPos))
        vector_proj = np.ndarray.tolist(vector_proj_array)
        clamped_X_vector = vector_proj[0]
        clamped_Y_vector = vector_proj[1]
        if (touchStart == False):
            active_X = rotated_X
            active_Y = rotated_Y
        else:
            if (active_Y < startPos[1] - 20 and clamped_Y_vector < 0):
                active_X = active_X - clamped_X_vector
                active_Y = active_Y - clamped_Y_vector
            else:
                active_X = active_X + clamped_X_vector
                active_Y = active_Y + clamped_Y_vector
        circle_pos = [active_X, active_Y]
        myCircle.setPos(circle_pos)
        myCircle.draw()
        

        
        ### Adding Values to appropriate Arrays
        timeArray.append(current_timestamp)
        mouseposXArray.append(current_pos[0])
        mouseposYArray.append(current_pos[1] + cfg['active_height']/2)
        cursorposXArray.append(active_X)
        cursorposYArray.append(active_Y + cfg['active_height']/2)
        
        
        if (prev_timestamp != 0):
            change_in_time = current_timestamp - prev_timestamp
            velocity = (np.linalg.norm([current_pos[0] - prev_X, current_pos[1] - prev_Y]))/change_in_time
#            print (velocity)
            
        prev_timestamp = current_timestamp
        prev_X = current_pos[0]
        prev_Y = current_pos[1]
        
    #    if (all(mousePos)==all(startPos)):
        if ((get_dist(circle_pos, startPos) < 10) and velocity < 35 and touchStart == False):
            touchStart=True
            show_target = True
            show_home = False
            phase_one = True
        
        if (touchStart==True and phase_one == True):          
            if ((get_dist(circle_pos, endPos) < 10) and velocity < 35 and cfg['terminal_feedback'] == False):
                phase_two = True
                show_target = False
                show_home = True
            ### Terminal Feedback portion
            if ((get_dist(circle_pos, startPos) >= cfg['terminal_multiplier']*get_dist(startPos, endPos)) and cfg['terminal_feedback'] == True):
                timer = core.getTime()
                while ((core.getTime() - timer) < cfg['terminal_feedback_time']):
                    myCircle.draw()
                    if (cfg['poll_type'] == 'psychopy'):
                        timeArray.append(core.getTime() - myTime)
                        mouseposXArray.append(myMouse.getPos()[0])
                        mouseposYArray.append(myMouse.getPos()[1] + cfg['active_height']/2)
                    elif (cfg['poll_type'] == 'x11'):
                        timeArray.append(myMouse.Pos()[2] - myTime)
                        mouseposXArray.append(myMouse.Pos()[0])
                        mouseposYArray.append(myMouse.Pos()[1] + cfg['active_height']/2)
                    cursorposXArray.append(rotated_X)
                    cursorposYArray.append(rotated_Y + cfg['active_height']/2)
                    myWin.flip()
                    
                timePos_dict['task_num'] = cfg['task_num']
                timePos_dict['trial_num'] = cfg['trial_num']
                timePos_dict['trial_type'] = cfg['trial_type']
                timePos_dict['target_angle_degrees'] = angle
                timePos_dict['homex_px'] = startPos[0]
                timePos_dict['homey_px'] = startPos[1] + cfg['active_height']/2
                timePos_dict['targetx_px'] = endPos[0]
                timePos_dict['targety_px'] = endPos[1] + cfg['active_height']/2
                timePos_dict['time_s'] = timeArray
                timePos_dict['mousex_px'] = mouseposXArray
                timePos_dict['mousey_px'] = mouseposYArray
                timePos_dict['cursorx_px'] = cursorposXArray
                timePos_dict['cursory_px'] = cursorposYArray
                timePos_dict['terminal_feedback_degrees'] = cfg['terminal_feedback']
                return timePos_dict  
        if (phase_two == True and (get_dist(circle_pos, startPos) < 10) and velocity < 35):
            timePos_dict['task_num'] = cfg['task_num']
            timePos_dict['trial_num'] = cfg['trial_num']
            timePos_dict['trial_type'] = cfg['trial_type']
            timePos_dict['target_angle_degrees'] = angle
            timePos_dict['homex_px'] = startPos[0]
            timePos_dict['homey_px'] = startPos[1] + cfg['active_height']/2
            timePos_dict['targetx_px'] = endPos[0]
            timePos_dict['targety_px'] = endPos[1] + cfg['active_height']/2
            timePos_dict['time_s'] = timeArray
            timePos_dict['mousex_px'] = mouseposXArray
            timePos_dict['mousey_px'] = mouseposYArray
            timePos_dict['cursorx_px'] = cursorposXArray
            timePos_dict['cursory_px'] = cursorposYArray
            timePos_dict['terminal_feedback_degrees'] = cfg['terminal_feedback']
            return timePos_dict
        myWin.flip()
    timePos_dict['task_num'] = cfg['task_num']
    timePos_dict['trial_num'] = cfg['trial_num']
    timePos_dict['trial_type'] = cfg['trial_type']
    timePos_dict['target_angle_degrees'] = angle
    timePos_dict['homex_px'] = startPos[0]
    timePos_dict['homey_px'] = startPos[1] + cfg['active_height']/2
    timePos_dict['targetx_px'] = endPos[0]
    timePos_dict['targety_px'] = endPos[1] + cfg['active_height']/2
    timePos_dict['time_s'] = timeArray
    timePos_dict['mousex_px'] = mouseposXArray
    timePos_dict['mousey_px'] = mouseposYArray
    timePos_dict['cursorx_px'] = cursorposXArray
    timePos_dict['cursory_px'] = cursorposYArray
    timePos_dict['terminal_feedback_degrees'] = cfg['terminal_feedback']
    #myWin.close()
    return timePos_dict
    
def create_task(general_cfg = {}):
    task = {}
    ### SET GENERAL SPECS
    task['active_height'] = general_cfg['active_height']
    task['min_distance'] = general_cfg['min_distance']
    task['max_distance'] = general_cfg['max_distance']
    task['min_angle'] = general_cfg['min_angle']
    task['max_angle'] = general_cfg['max_angle']
    task['starting_pos'] = general_cfg['starting_pos']
#    task['x11_mouse'] = general_cfg['x11_mouse']
    task['terminal_feedback_time'] = general_cfg['terminal_feedback_time']
    task['terminal_multiplier'] = general_cfg['terminal_multiplier']
    trial_type = raw_input("What trial type?(cursor/no_cursor/error_clamp): ")
    task['trial_type'] = trial_type
    
    num_trials = raw_input("How many trials do you want to run?: ")
    task['num_trials'] = int(num_trials)
    num_targets = raw_input("How many targets?: ")
    task['num_targets'] = int(num_targets)
    rotation_angle = raw_input("Set rotation angle to (in degrees) set to 0 for no rotation: ")
    task['rotation_angle'] = int(rotation_angle)
    if (task['trial_type'] == 'cursor'):
        lag_input = raw_input("How long of lag (ms)?: ")
        lag_conversion_factor = 37.2495/1000
        task['lag'] = int(int(lag_input)*lag_conversion_factor)
    
    
    terminal_feedback = raw_input("terminal feedback Y/N?: ")
    if (terminal_feedback.lower() == 'y'):
        task['terminal_feedback'] = True
    elif (terminal_feedback.lower() == 'n'):
        task['terminal_feedback'] = False
    return task
#################### PAUSE TASK ####################################
def pause_experiment(cfg={}):
    myWin = cfg['win']
    instruction = cfg['pause_instruction']
    counter_text = visual.TextStim(myWin, text=str(cfg['pausetime']), pos=(0, 40), color=( 1, 1, 1))    
    instruction_text = visual.TextStim(myWin, text=instruction, pos=(0,0), color=( 1, 1, 1))
    end_text = visual.TextStim(myWin, text="Press space to continue", pos=(0,-40), color=( 1, 1, 1))
    while ((core.getTime() - cfg['time']) < cfg['pausetime']):
        counter_text.setText("{:0.0f}".format((cfg['pausetime'] - (core.getTime() - cfg['time']))))
        instruction_text.draw()
        counter_text.draw()
        myWin.flip()
    if (cfg['pause_button_wait'] == True):
        instruction_text.draw()
        counter_text.draw()
        end_text.draw()
        myWin.flip()
        event.waitKeys(keyList=['space'])

def trial_runner(cfg={}):
    myWin=cfg['win']
    if (cfg['trial_type'] == 'pause'):
        instruction = cfg['pause_instruction']
        counter_text = visual.TextStim(myWin, text=str(cfg['pausetime']), pos=(0, 40), color=( 1, 1, 1))    
        instruction_text = visual.TextStim(myWin, text=instruction, pos=(0,0), color=( 1, 1, 1))
        end_text = visual.TextStim(myWin, text="Press space to continue", pos=(0,-40), color=( 1, 1, 1))
        while ((core.getTime() - cfg['time']) < cfg['pausetime']):
            counter_text.setText("{:0.0f}".format((cfg['pausetime'] - (core.getTime() - cfg['time']))))
            instruction_text.draw()
            counter_text.draw()
            myWin.flip()
        if (cfg['pause_button_wait'] == True):
            instruction_text.draw()
            counter_text.draw()
            end_text.draw()
            myWin.flip()
            event.waitKeys(keyList=['space'])
            return None
    end_X = cfg['target_distance'] * math.cos(math.radians(cfg['target_angle']))
    end_Y = (cfg['target_distance'] * math.sin(math.radians(cfg['target_angle']))) - cfg['active_height']/2
    ### Creates Mouse object
    if (cfg['poll_type'] == 'psychopy'):
        myMouse = cfg['mouse']
        ### Gets current CPU Time
        myTime = cfg['time']
    elif (cfg['poll_type'] == 'x11'):
        myMouse = cfg['x11_mouse']
        ### Gets current CPU Time
        myTime = myMouse.Pos()[2]
    ### Creates cursor circle Object
    myCircle = cfg['cursor_circle']
    ### Creates a circle object to be used as starting point      
    startCircle = cfg['start_circle']
    ### Creates a Target circle
    endCircle = cfg['end_circle']
    ### Define Parameters here
    startPos=cfg['starting_pos']
    arrow=cfg['arrow_stim']
    
    endPos=[end_X, end_Y]   
    ### Instantiating Checking Variables Here
    phase_1 = False
    phase_2 = False
    show_target = False
    show_home = True
    show_cursor = True
    show_arrow = False
    nc_check_1 = False
    timerSet = False
    timer_timestamp = 0
    stablize = False
    ### These variables record timestamps and mouse positions (Used to calculate mouse velocity)
    prev_timestamp = 0
    prev_X = 0
    prev_Y = 0
    prev_X_cursor = 0
    prev_Y_cursor = 0
    velocity = 0
    ### Instantiating return dictionary and arrays within it
    timePos_dict = {}
    timeArray = []
    mouseposXArray = []
    mouseposYArray = []
    cursorposXArray = []
    cursorposYArray = []
    ### target circle position
    endCircle.setPos(endPos)
    ### starting circle 
    startCircle.setPos(startPos)
    arrow.setPos(startPos)
    while (core.getTime() - cfg['time']) < 60:
        ### mouse Position
        if (cfg['poll_type'] == 'psychopy'):
            mousePos = myMouse.getPos()
            current_pos = mousePos
            current_timestamp = core.getTime() - myTime
        elif (cfg['poll_type'] == 'x11'):
            mousePos = [myMouse.Pos()[0], myMouse.Pos()[1]]
            current_pos = mousePos
            current_timestamp = myMouse.Pos()[2] - myTime
########################## SPECIAL CURSOR CONFIGURATIONS #####################
        if (prev_timestamp != 0):
            change_in_time = current_timestamp - prev_timestamp
            velocity = (np.linalg.norm([current_pos[0] - prev_X, current_pos[1] - prev_Y]))/change_in_time
        rotated_X = current_pos[0]*math.cos(math.radians(cfg['rotation_angle'])) - current_pos[1]*math.sin(math.radians(cfg['rotation_angle']))
        rotated_Y = current_pos[0]*math.sin(math.radians(cfg['rotation_angle'])) + current_pos[1]*math.cos(math.radians(cfg['rotation_angle']))    
        if (cfg['trial_type'] == 'cursor'):
            if [cfg['rotation_angle'] == 0]:
                circle_pos = mousePos
            else:
                circle_pos = [rotated_X, rotated_Y]
        elif (cfg['trial_type'] == 'no_cursor'):
            circle_pos = mousePos
        elif (cfg['trial_type'] == 'error_clamp'):
            circle_pos = mousePos
            vector_proj_array = get_vector_projection(get_vect([prev_X, prev_Y], current_pos), get_vect(startPos, endPos))
            vector_proj = np.ndarray.tolist(vector_proj_array)
            clamped_X_vector = vector_proj[0]
            clamped_Y_vector = vector_proj[1]
            if (phase_1 == False):
                active_X = current_pos[0]
                active_Y = current_pos[1]
            else:
                if (active_Y < startPos[1] - 20 and clamped_Y_vector < 0):
                    active_X = active_X - clamped_X_vector
                    active_Y = active_Y - clamped_Y_vector
                else:
                    active_X = prev_X_cursor + clamped_X_vector
                    active_Y = prev_Y_cursor + clamped_Y_vector
            circle_pos_clamped = [active_X, active_Y]
########################### SET CURSOR POSITIONS #############################
        if (cfg['trial_type'] == 'error_clamp' and phase_1 == True and stablize == True):
            circle_pos = circle_pos_clamped
        elif (cfg['trial_type'] == 'error_clamp' and phase_1 == True and stablize == False):
            circle_pos = startPos
            stablize = True
        myCircle.setPos(circle_pos)
########################### SPECIAL ARROW CONDITIONS #########################
        if (cfg['trial_type'] == 'no_cursor'):
            arrow.ori = -myRounder(math.degrees(cart2pol([current_pos[0],current_pos[1] + cfg['active_height']/2])[1]), 45)  
################################ SHOW OBJECTS ################################
        if (show_home == True):
            startCircle.draw()
        if (show_target == True):
            endCircle.draw()
        if (show_cursor == True):
            myCircle.draw()
        if (show_arrow == True):
            arrow.draw()
################################ PHASE 1 #####################################
        if (phase_1 == False):
            if (cfg['trial_type'] == 'cursor'):
                if (get_dist(circle_pos, startPos) < 5 and velocity < 35):
                    phase_1 = True
                    show_home = False
                    show_target = True
            elif (cfg['trial_type'] == 'no_cursor'):
                if (get_dist(circle_pos, startPos) < 5 and velocity < 35):
                    phase_1 = True
                    show_target = True
            elif (cfg['trial_type'] == 'error_clamp'):
                if (get_dist(circle_pos, startPos) < 4 and velocity < 35):
                    phase_1 = True
                    show_target = True
                    show_home = False
################################ PHASE 2 #####################################
        if (phase_1 == True and phase_2 == False):
            if (cfg['trial_type'] == 'cursor'):
                if (get_dist(circle_pos, endPos) < 5 and velocity < 35):
                    phase_2 = True
                    show_home = True
                    show_target = False
            if (cfg['trial_type'] == 'no_cursor'):
                ##### STOP WATCH ####
                if (velocity < 30 and timerSet == False and cfg['terminal_feedback'] == False):
                    timer_timestamp = current_timestamp
                    timerSet = True
                stop_time = current_timestamp - timer_timestamp
                if (velocity > 30 and timerSet == True and cfg['terminal_feedback'] == False):
                    timerSet = False
                    stop_time = 0  
                if (get_dist(circle_pos, startPos) > 10 and nc_check_1 == False):
                    show_home = False
                    show_target = True
                    nc_check_1 = True
                    show_cursor = False
                if (get_dist(circle_pos, startPos) > get_dist(startPos, endPos)/2 and stop_time >= 0.75):
                    phase_2 = True
                    show_target = False
                    show_home = True   
            if (cfg['trial_type'] == 'error_clamp'):
                if (get_dist(circle_pos, endPos) < 5 and velocity < 35):
                    phase_2 = True
                    show_home = True
                    show_cursor = False
                    show_target = False
############################ DATA COLLECTION #################################
        prev_timestamp = current_timestamp
        prev_X = current_pos[0]
        prev_Y = current_pos[1]
        prev_X_cursor = circle_pos[0]
        prev_Y_cursor = circle_pos[1]
        timeArray.append(current_timestamp)
        mouseposXArray.append(current_pos[0])
        mouseposYArray.append(current_pos[1] + cfg['active_height']/2)
        cursorposXArray.append(circle_pos[0])
        cursorposYArray.append(circle_pos[1] + cfg['active_height']/2)
        myWin.flip()
################################ PHASE 3 #####################################
        if (cfg['terminal_feedback'] == True and (get_dist(circle_pos, startPos) >= cfg['terminal_multiplier']*get_dist(startPos, endPos) + 5) and phase_1 == True):
                timer = core.getTime()
                while ((core.getTime() - timer) < cfg['terminal_feedback_time']):
                    myCircle.draw()
                    if (cfg['poll_type'] == 'psychopy'):
                        timeArray.append(core.getTime() - myTime)
                        mouseposXArray.append(myMouse.getPos()[0])
                        mouseposYArray.append(myMouse.getPos()[1] + cfg['active_height']/2)
                    elif (cfg['poll_type'] == 'x11'):
                        timeArray.append(myMouse.Pos()[2] - myTime)
                        mouseposXArray.append(myMouse.Pos()[0])
                        mouseposYArray.append(myMouse.Pos()[1] + cfg['active_height']/2)
                    cursorposXArray.append(rotated_X)
                    cursorposYArray.append(rotated_Y + cfg['active_height']/2)
                    myWin.flip()
                timePos_dict['task_num'] = cfg['task_num']
                timePos_dict['task_name'] = cfg['task_name']
                timePos_dict['trial_num'] = cfg['trial_num']
                timePos_dict['trial_type'] = cfg['trial_type']
                timePos_dict['target_angle_degrees'] = cfg['target_angle']
                timePos_dict['homex_px'] = startPos[0]
                timePos_dict['homey_px'] = startPos[1] + cfg['active_height']/2
                timePos_dict['targetx_px'] = endPos[0]
                timePos_dict['targety_px'] = endPos[1] + cfg['active_height']/2
                timePos_dict['time_s'] = timeArray
                timePos_dict['mousex_px'] = mouseposXArray
                timePos_dict['mousey_px'] = mouseposYArray
                timePos_dict['cursorx_px'] = cursorposXArray
                timePos_dict['cursory_px'] = cursorposYArray
                timePos_dict['terminal_feedback_degrees'] = cfg['terminal_feedback']
                timePos_dict['percmax'] = int(cfg['target_distance_ratio']*100)
                return timePos_dict  
        if (phase_1 == True and phase_2 == True):
            
            if (cfg['trial_type'] == 'no_cursor' and get_dist(circle_pos, startPos) <= get_dist(startPos,endPos)/2):
                show_arrow = True
            elif (cfg['trial_type'] == 'no_cursor' and get_dist(circle_pos, startPos) > get_dist(startPos, endPos)/2):
                show_arrow = False
            if (cfg['trial_type'] == 'no_cursor' and get_dist(circle_pos, startPos) > 3*get_dist(startPos, endPos)/20):
                show_cursor = False
                
            if (cfg['trial_type'] == 'cursor'  and get_dist(circle_pos, startPos) < 5 and velocity < 35):
                timePos_dict['task_num'] = cfg['task_num']
                timePos_dict['task_name'] = cfg['task_name']
                timePos_dict['trial_num'] = cfg['trial_num']
                timePos_dict['trial_type'] = cfg['trial_type']
                timePos_dict['target_angle_degrees'] = cfg['target_angle']
                timePos_dict['homex_px'] = startPos[0]
                timePos_dict['homey_px'] = startPos[1] + cfg['active_height']/2
                timePos_dict['targetx_px'] = endPos[0]
                timePos_dict['targety_px'] = endPos[1] + cfg['active_height']/2
                timePos_dict['time_s'] = timeArray
                timePos_dict['mousex_px'] = mouseposXArray
                timePos_dict['mousey_px'] = mouseposYArray
                timePos_dict['cursorx_px'] = cursorposXArray
                timePos_dict['cursory_px'] = cursorposYArray
                timePos_dict['terminal_feedback_degrees'] = cfg['terminal_feedback']
                timePos_dict['percmax'] = int(cfg['target_distance_ratio']*100)            
                return timePos_dict
                
            elif ((cfg['trial_type'] == 'no_cursor' or cfg['trial_type'] == 'error_clamp') and get_dist(circle_pos, startPos) <= 3*get_dist(startPos, endPos)/20):
                show_cursor = True
                if (get_dist(circle_pos, startPos) < 5):
                    timePos_dict['task_num'] = cfg['task_num']
                    timePos_dict['task_name'] = cfg['task_name']
                    timePos_dict['trial_num'] = cfg['trial_num']
                    timePos_dict['trial_type'] = cfg['trial_type']
                    timePos_dict['target_angle_degrees'] = cfg['target_angle']
                    timePos_dict['homex_px'] = startPos[0]
                    timePos_dict['homey_px'] = startPos[1] + cfg['active_height']/2
                    timePos_dict['targetx_px'] = endPos[0]
                    timePos_dict['targety_px'] = endPos[1] + cfg['active_height']/2
                    timePos_dict['time_s'] = timeArray
                    timePos_dict['mousex_px'] = mouseposXArray
                    timePos_dict['mousey_px'] = mouseposYArray
                    timePos_dict['cursorx_px'] = cursorposXArray
                    timePos_dict['cursory_px'] = cursorposYArray
                    timePos_dict['terminal_feedback_degrees'] = cfg['terminal_feedback']
                    timePos_dict['percmax'] = int(cfg['target_distance_ratio']*100)
                    return timePos_dict
################################## CREATE EXPERIMENT ###############
# This function utilizes the above function to create a list of tasks
# to be used to generate a full experiment
def create_experiment(general_cfg = {}):
    experiment= []
    add_task = raw_input("Would you like to create an experiment?(Y/N): ")
    task_poll_type = raw_input("Set polling method?(x11/psychopy): ")
    while (add_task.lower() == 'y'):
        new_task = create_task(general_cfg)
        new_task['poll_type'] = task_poll_type.lower()
        experiment.append(new_task)
        add_task = raw_input("Would you like to create another task?(Y/N): ")
    return experiment

########################### RUN EXPERIMENT #############################

def run_experiment(fulls, experiment = []):
    end_exp = pd.DataFrame({})
    running = copy.deepcopy(experiment)
#    screen_width = root.winfo_screenwidth()
#    screen_height = root.winfo_screenheight()
#    
#    trimmed_width = int((float(2)/float(3))*float(screen_width))
#    trimmed_height = int((float(2)/float(3))*float(screen_height))
#    active_width = trimmed_width
#    if (trimmed_width < 2*trimmed_height):
#        active_height = trimmed_width/2
#    else:
#        active_height = trimmed_height/2
    Win = visual.Window([active_width, (active_height*3)/2], colorSpace='rgb', fullscr=fulls, name='MousePosition', color=(-1, -1, -1), units='pix')    
    ### Configure visual feedback settings here
    myCircle = visual.Circle(win=Win,
                             radius=12,
                             edges=32,
                             units='pix',
                             fillColor=[0, 0, 0],
                             lineColor=[0, 0, 0])
    startCircle = visual.Circle(win=Win,
                                radius=12,
                                lineWidth=2,
                                edges=32,
                                units='pix',
                                fillColor=[-1, -1, -1],
                                 lineColor=[0, 0, 0])
    endCircle = visual.Circle(win=Win,
                              radius=12,
                              lineWidth=2,
                              edges=32,
                              units='pix',
                              fillColor=[-1, -1, -1],
                              lineColor=[0, 0, 0])
    
    Mouse = event.Mouse(win=Win, visible=False)
    for i in range (0, len(experiment)):
        running[i]['x11_mouse'] = myMouse()
        running[i]['cursor_circle'] = myCircle
        running[i]['start_circle'] = startCircle
        running[i]['end_circle'] = endCircle
        running[i]['mouse'] = Mouse
        running[i]['win'] = Win
        running[i]['task_num'] = i + 1
        targetList = angle_split(running[i]['min_angle'], running[i]['max_angle'], running[i]['num_targets'])
        fulltargetList = tuple(targetList)
        if (running[i]['trial_type'] != 'pause'):
            targetList = angle_split(running[i]['min_angle'], running[i]['max_angle'], running[i]['num_targets'])
        if (running[i]['trial_type'] == 'cursor'):
            for trial_num in range (0, running[i]['num_trials']):
                running[i]['trial_num'] = trial_num + 1
                if (len(targetList) == 0):
                    targetList = list(fulltargetList)
                chosen_target = random.choice(targetList)
                running[i]['target_angle'] = chosen_target
                targetList.remove(chosen_target)
                running[i]['target_distance'] = running[i]['max_distance']*running[i]['target_distance_ratio']
                running[i]['time'] = core.getTime()
                exp = experiment_cursor(running[i]['target_angle'], running[i]['target_distance'], running[i])
                df_exp = pd.DataFrame(exp, columns=['task_num', 'trial_type', 'trial_num', 'terminal_feedback_boolean','target_angle_degrees','homex_px','homey_px','targetx_px','targety_px', 'time_s', 'mousex_px', 'mousey_px', 'cursorx_px', 'cursory_px'])
                end_exp = pd.concat([end_exp, df_exp])
        elif (running[i]['trial_type'] == 'no_cursor'):
            for trial_num in range (0, running[i]['num_trials']):
                running[i]['trial_num'] = trial_num + 1
                if (len(targetList) == 0):
                    targetList = list(fulltargetList)
                chosen_target = random.choice(targetList)
                running[i]['target_angle'] = chosen_target
                targetList.remove(chosen_target)
                running[i]['target_distance'] = running[i]['max_distance']*running[i]['target_distance_ratio']
                running[i]['time'] = core.getTime()
                exp = experiment_no_cursor(running[i]['target_angle'], running[i]['target_distance'], running[i])
                df_exp = pd.DataFrame(exp, columns=['task_num', 'trial_type','trial_num', 'terminal_feedback_boolean','target_angle_degrees','homex_px','homey_px','targetx_px','targety_px', 'time_s', 'mousex_px', 'mousey_px', 'cursorx_px', 'cursory_px'])
                end_exp = pd.concat([end_exp, df_exp])
        elif (running[i]['trial_type'] == 'error_clamp'):
            for trial_num in range (0, running[i]['num_trials']):
                running[i]['trial_num'] = trial_num + 1
                if (len(targetList) == 0):
                    targetList = list(fulltargetList)
                chosen_target = random.choice(targetList)
                running[i]['target_angle'] = chosen_target
                targetList.remove(chosen_target)
                running[i]['target_distance'] = running[i]['max_distance']*running[i]['target_distance_ratio']
                running[i]['time'] = core.getTime()
                exp = experiment_error_clamp(running[i]['target_angle'], running[i]['target_distance'], running[i])
                df_exp = pd.DataFrame(exp, columns=['task_num', 'trial_type', 'trial_num', 'terminal_feedback_boolean','target_angle_degrees','homex_px','homey_px','targetx_px','targety_px', 'time_s', 'mousex_px', 'mousey_px', 'cursorx_px', 'cursory_px'])
                end_exp = pd.concat([end_exp, df_exp])
        elif (running[i]['trial_type'] == 'pause'):
            running[i]['time'] = core.getTime()
            pause_experiment(running[i])
    running[i]['win'].close()
    return end_exp
############################# RUN EXPERIMENT V2 ###############################
def run_experiment_2(fulls, experiment = []):
    end_exp = pd.DataFrame({})
    running = copy.deepcopy(experiment)
    cfg = {}
    addWorkSpaceLimits(cfg)
    Win = visual.Window([cfg['active_width'], (cfg['active_height']*3)/2], colorSpace='rgb', fullscr=fulls, name='MousePosition', color=(-1, -1, -1), units='pix')    
    ### Configure visual feedback settings here
    myCircle = visual.Circle(win=Win,
                             radius=12,
                             edges=32,
                             units='pix',
                             fillColor=[0, 0, 0],
                             lineColor=[0, 0, 0])
    startCircle = visual.Circle(win=Win,
                                radius=12,
                                lineWidth=2,
                                edges=32,
                                units='pix',
                                fillColor=[-1, -1, -1],
                                 lineColor=[0, 0, 0])
    endCircle = visual.Circle(win=Win,
                              radius=12,
                              lineWidth=2,
                              edges=32,
                              units='pix',
                              fillColor=[-1, -1, -1],
                              lineColor=[0, 0, 0]) 
    arrowVert = [(-1, 1),(-1,-1),(1,0)]
    arrow = visual.ShapeStim(win=Win,
                             vertices=arrowVert,
                             fillColor=[0, 0, 0],
                             size=7,
                             lineColor=[0,0,0])
    Mouse = event.Mouse(win=Win, visible=False)
    for i in range (0, len(experiment)):
        running[i]['x11_mouse'] = myMouse()
        running[i]['cursor_circle'] = myCircle
        running[i]['start_circle'] = startCircle
        running[i]['end_circle'] = endCircle
        running[i]['mouse'] = Mouse
        running[i]['win'] = Win
        running[i]['arrow_stim'] = arrow
        running[i]['task_num'] = i + 1
        running[i]['max_distance'] = cfg['active_height']
        targetList = angle_split(running[i]['min_angle'], running[i]['max_angle'], running[i]['num_targets'])
        fulltargetList = tuple(targetList)
        if (running[i]['trial_type'] != 'pause'):
            targetList = angle_split(running[i]['min_angle'], running[i]['max_angle'], running[i]['num_targets'])          
            for trial_num in range (0, running[i]['num_trials']):
                running[i]['trial_num'] = trial_num + 1
                if (len(targetList) == 0):
                    targetList = list(fulltargetList)
                chosen_target = random.choice(targetList)
                running[i]['target_angle'] = chosen_target
                targetList.remove(chosen_target)
                running[i]['target_distance'] = int(running[i]['max_distance']*running[i]['target_distance_ratio'])
                running[i]['time'] = core.getTime()
                exp = trial_runner(running[i])
                df_exp = pd.DataFrame(exp, columns=['task_num','task_name', 'trial_type', 'trial_num', 'terminal_feedback_boolean','target_angle_degrees','percmax','homex_px','homey_px','targetx_px','targety_px', 'time_s', 'mousex_px', 'mousey_px', 'cursorx_px', 'cursory_px'])
                end_exp = pd.concat([end_exp, df_exp])
        if (running[i]['trial_type'] == 'pause'):
            running[i]['time'] = core.getTime()
            exp = trial_runner(running[i])
    running[i]['win'].close()
    end_exp.drop(end_exp.index[0])
    return end_exp