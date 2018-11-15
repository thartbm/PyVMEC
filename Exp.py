# with functions that run a trial sequence as passed to it, and stores the data appropriately
from psychopy.visual import Window, Circle, ShapeStim, TextStim, ImageStim
from psychopy import event, core
from psychopy.visual import shape
from os import path, listdir
from json import dump
import pyautogui
#import pygame as pg
#from pygame import QUIT, quit, KEYDOWN, K_SPACE, K_ESCAPE
#from pygame import event as pev
from numpy import sqrt, arctan2, cos, sin, linalg, dot, ndarray, array, diff, mean
import math
from pandas import concat, DataFrame
from random import choice, seed, shuffle
from Tkinter import Tk
from copy import deepcopy
import sys
import screeninfo


try:
    from ctypes import *
except:
    pass
from time import time


root = Tk()
def addWorkSpaceLimits(screen, cfg = {}):
    s = screeninfo.get_monitors()
    if (len(s) == 1 and screen == 0):
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
    elif(len(s) > 1 and screen == 0):
        screen_width = int(str(s[0]).strip('monitor(').partition('x')[0])
        screen_height = int(str(s[0]).strip('monitor(').partition('x')[2].partition('+')[0])
        cfg['main_screen_dimensions'] = [int(str(s[1]).strip('monitor(').partition('x')[0]), int(str(s[1]).strip('monitor(').partition('x')[2].partition('+')[0])]

    else:
        screen_width = int(str(s[1]).strip('monitor(').partition('x')[0])
        screen_height = int(str(s[1]).strip('monitor(').partition('x')[2].partition('+')[0])
        cfg['main_screen_dimensions'] = [int(str(s[0]).strip('monitor(').partition('x')[0]), int(str(s[0]).strip('monitor(').partition('x')[2].partition('+')[0])]

    trimmed_width = int((float(2)/float(3))*float(screen_width))
    trimmed_height = int((float(2)/float(3))*float(screen_height))
    if (trimmed_height*2 < trimmed_width):
        trimmed_width = trimmed_height*2
    else:
        trimmed_height = trimmed_width/2
    cfg['active_width'] = trimmed_width
    cfg['active_height'] = trimmed_height
    cfg['circle_radius'] = trimmed_height*0.025
    cfg['icon_diameter'] = trimmed_height*0.075
    cfg['screen_dimensions'] = [screen_width, screen_height]
    cfg['winType'] = 'pyglet'
    return cfg

try:
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
except:
    print ('not using xLib')
    pass
def moveMouse(x,y):
    myMouse.setPos([x,y])
    myWin.winHandle._mouse_x = x  # hack to change pyglet window
    myWin.winHandle._mouse_y = y
    
def myRounder(x, base):
    return int(base * round(float(x)/base))

def vector_rotate(node, center, angle):
    vector_X = center[0] + (node[0] - center[0])*math.cos(math.radians(angle)) - (node[1] - center[1])*math.sin(math.radians(angle))
    vector_Y = center[1] + (node[0] - center[0])*math.sin(math.radians(angle)) + (node[1] - center[1])*math.cos(math.radians(angle))
    return [vector_X, vector_Y]
                

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
        if (given_task == "error_clamp"):
            return 2
        if (given_task == "pause"):
            return 3
    elif (function == False):
        if (given_task == 0):
            return "cursor"
        if (given_task == 1):
            return "no_cursor"
        if (given_task == 2):
            return "error_clamp"
        if (given_task == 3):
            return "pause"
def rotation_num(rotation_type, function):
    if (function == True):
        if (rotation_type == 'abrupt'):
            return 0
        elif (rotation_type == 'gradual'):
            return 1
    if (function == False):
        if (rotation_type == 0):
            return 'abrupt'
        if (rotation_type == 1):
            return 'gradual'
def setParticipantSeed(participant):
    
    seed(sum([ord(c) for c in participant]))

def shuffleTargets4task(targets, blocks):
    taskTargets = []
    
    for block in range(blocks):
      shuffle(targets)
      taskTargets = taskTargets + targets  
    return(taskTargets)
    
def rotation_direction_num(rotation_direction, function):
    if (function == True):
        if (rotation_direction == 'Counter-clockwise'):
            return 0
        elif (rotation_direction == 'Clockwise'):
            return 1
    if (function == False):
        if (rotation_direction == 0):
            return 'Counter-clockwise'
        if (rotation_direction == 1):
            return 'Clockwise'


def cart2pol(coord=[]):
    rho = sqrt(coord[0]**2 + coord[1]**2)
    phi = arctan2(coord[1], coord[0])
    return [rho, phi]

def pol2cart(rho, phi):
    x = rho * cos(phi)
    y = rho * sin(phi)
    return(x, y)

def get_dist(select_pos, target_pos):
    vector = [target_pos[0] - select_pos[0], target_pos[1] - select_pos[1]]
    return linalg.norm(vector)
def get_vect(select_pos, target_pos):
    vector = [target_pos[0] - select_pos[0], target_pos[1] - select_pos[1]]
    return vector

def get_uvect(vector):
    uvect = vector/linalg.norm(vector)
    return uvect
def get_vector_projection(moving_vect, static_vect):
    static_uvect = get_uvect(static_vect)
    scalar_proj = dot(moving_vect, static_uvect)
    return scalar_proj*static_uvect
    
def vector_projection(moving_vect, static_vect):
    static_uvect = get_uvect(static_vect)
    scalar_proj = dot(moving_vect, static_uvect)/(linalg.norm(static_vect))
    return list(scalar_proj*static_uvect)
    
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

#################### PAUSE TASK ####################################
def pause_experiment(cfg={}):
    myWin = cfg['win']
    instruction = cfg['pause_instruction']
    counter_text = TextStim(myWin, text=str(cfg['pausetime']), pos=(0, 40), color=( 1, 1, 1))
    instruction_text = TextStim(myWin, text=instruction, pos=(0,0), color=( 1, 1, 1))
    end_text = TextStim(myWin, text="Press space to continue", pos=(0,-40), color=( 1, 1, 1))
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
    try:
        myWin=cfg['win']
        if (cfg['trial_type'] == 'pause'):
            instruction = cfg['pause_instruction']
            counter_text = TextStim(myWin, text=str(cfg['pausetime']), flipVert=cfg['flip_text'], pos=(0, 40*cfg['flipscreen']), color=( 1, 1, 1))
            instruction_text = TextStim(myWin, text=instruction, pos=(0,0), flipVert=cfg['flip_text'], color=( 1, 1, 1))
            end_text = TextStim(myWin, text="Press space to continue", pos=(0,-40*cfg['flipscreen']), flipVert=cfg['flip_text'], color=( 1, 1, 1))
#            pyautogui.moveTo(root.winfo_screenwidth() - 50, root.winfo_screenheight() - 50)
            pyautogui.click()
            while ((core.getTime() - cfg['time']) < cfg['pausetime']):
                counter_text.setText("{:0.0f}".format((cfg['pausetime'] - (core.getTime() - cfg['time']))))
                instruction_text.draw()
                if (cfg['pausetime'] != 0):
                    counter_text.draw()
                myWin.flip()
            if (cfg['pause_button_wait'] == True):
                instruction_text.draw()
                if (cfg['pausetime'] != 0):
                    counter_text.draw()
                end_text.draw()
                myWin.flip()
                event.waitKeys(keyList=['space'])
                #### IF USING PYGAME ####
    #            pev.clear()
    #            while True:
    #                event = pev.wait()
    #                if event.type == QUIT:
    #                    quit()
    #                    sys.exit()
    #                elif event.type == KEYDOWN:
    #                    if event.key == K_SPACE:
    #                        return None
            return None

        end_X = cfg['target_distance'] * math.cos(math.radians(cfg['target_angle']))
        end_Y = ((cfg['target_distance'] * math.sin(math.radians(cfg['target_angle']))) - cfg['active_height']/2)*cfg['flipscreen']
        ### Creates Mouse object
        if (cfg['poll_type'] == 'psychopy'):
            myMouse = cfg['mouse']
            ### Gets current CPU Time
            myTime = cfg['time']
        elif (cfg['poll_type'] == 'x11'):
            myMouse = cfg['x11_mouse']
            ### Gets current CPU Time
            myTime = myMouse.Pos()[2]
        if (cfg['custom_stim_enable'] == False):
            ### Creates cursor circle Object
            myCircle = cfg['cursor_circle']
            testCircle = cfg['test_circle']
            ### Creates a Target circle
            endCircle = cfg['end_circle']
        elif (cfg['custom_stim_enable'] == True):
            rng = choice(cfg['custom_stim'])
            print rng
            myCircle = rng[0]
            endCircle = rng[1]
        ### Creates a circle object to be used as starting point
        startCircle = cfg['start_circle']
        
        ### Define Parameters here
        startPos=cfg['starting_pos']
        arrow=cfg['arrow_stim']
        arrowFill=cfg['arrowFill_stim']

        endPos=[end_X, end_Y]
        ### Instantiating Checking Variables Here
        phase_1 = False
        phase_2 = False
        show_target = False
        show_home = True
        show_cursor = True
        show_arrow = False
        show_arrowFill = False
        nc_check_1 = False
        timerSet = False
        timer_timestamp = 0
        stabilize = False
        screen_edge = (root.winfo_screenwidth()/2) - (cfg['screen_on']*cfg['screen_dimensions'][0])
        ### These variables record timestamps and mouse positions (Used to calculate mouse velocity)
        prev_timestamp = 0
        prev_X = 0
        prev_Y = 0
        prev_X_cursor = 0
        prev_Y_cursor = 0
        velocity = 0
        pixels_per_sample = 0
        pos_buffer = 0
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
        arrowFill.setPos(startPos)
        ### Rotation direction
    except Exception as e:
        print "error in Block 1"
        print e
    if cfg['rotation_angle_direction'] == 'Counter-clockwise':
        rot_dir = 1
    elif cfg['rotation_angle_direction'] == 'Clockwise':
        rot_dir = -1
    while (core.getTime() - cfg['time']) < 120:
        try:
            ### ESCAPE ### USING PYGAME ####
    #        event = pev.wait()
    #        if event.type == KEYDOWN:
    #            if event.key == K_ESCAPE:
    #                myWin.close()
    #                return 'escaped'
            ### ESCAPE ### USING PYGLET ####
            try:
                if event.getKeys(keyList=['escape']):
                    myWin.close()
                    return 'escaped'
                ### mouse Position
                if (cfg['poll_type'] == 'psychopy'):
                    mousePos = [myMouse.getPos()[0], myMouse.getPos()[1]*cfg['flipscreen']]
                    current_pos = mousePos
                    current_timestamp = core.getTime() - myTime
                elif (cfg['poll_type'] == 'x11'):
                    mousePos = [myMouse.Pos()[0], myMouse.Pos()[1]*cfg['flipscreen']]
                    current_pos = mousePos
                    current_timestamp = myMouse.Pos()[2] - myTime
        ########################## SPECIAL CURSOR CONFIGURATIONS #####################
                if (prev_timestamp != 0):
                    change_in_time = current_timestamp - prev_timestamp
                    velocity = (linalg.norm([current_pos[0] - prev_X, current_pos[1] - prev_Y]))/change_in_time
                    pixels_per_sample = velocity*change_in_time
                rotated_X, rotated_Y = vector_rotate(mousePos, [0 + (cfg['screen_on']*(cfg['screen_dimensions'][0]/2)), -cfg['active_height']/2], cfg['current_rotation_angle'])
                if (cfg['trial_type'] == 'cursor'):
                    if (cfg['rotation_angle'] == 0):
                        circle_pos = mousePos
                    else:
                        circle_pos = [rotated_X, rotated_Y]

                elif (cfg['trial_type'] == 'no_cursor'):
                    if (cfg['rotation_angle'] == 0):
                        circle_pos = mousePos
                    else:
                        circle_pos = [rotated_X, rotated_Y]
                elif (cfg['trial_type'] == 'error_clamp'):
                    circle_pos = mousePos
                    vector_proj_array = get_vector_projection(get_vect([prev_X, prev_Y], current_pos), get_vect(startPos, endPos))
                    vector_proj = ndarray.tolist(vector_proj_array)
                    cursor_direction_vector = vector_projection(get_vect(startPos, mousePos), get_vect(startPos, endPos))
                    clamped_X_vector = vector_proj[0]
                    clamped_Y_vector = vector_proj[1]
                    if (phase_1 == False):
                        active_X = circle_pos[0]
                        active_Y = circle_pos[1]
                    else:
                        if (active_Y < startPos[1] - 20 and clamped_Y_vector < 0):
                            active_X = active_X - clamped_X_vector
                            active_Y = active_Y - clamped_Y_vector
                        else:
                            active_X = prev_X_cursor + clamped_X_vector
                            active_Y = prev_Y_cursor + clamped_Y_vector
                    circle_pos_clamped = [startPos[0] + cursor_direction_vector[0], startPos[1] + cursor_direction_vector[1]]
            except:
                pass
    ########################### SET CURSOR POSITIONS #############################
            try:
                try:
                    if (cfg['trial_type'] == 'error_clamp' and phase_1 == True and phase_2 == False and stabilize == True):
                        circle_pos = circle_pos_clamped
                    if (cfg['trial_type'] == 'error_clamp' and phase_1 == True and phase_2 == True and stabilize == True):
                        circle_pos = [circle_pos[0] - cfg['screen_on']*(cfg['screen_dimensions'][0]/2), circle_pos[1]]
                    elif (cfg['trial_type'] == 'error_clamp' and phase_1 == True and stabilize == False):
                        circle_pos = startPos
                        stabilize = True
                    if cfg['trial_type'] != 'error_clamp' or (cfg['trial_type'] == 'error_clamp' and phase_1 == False):
                        circle_pos = [circle_pos[0] - cfg['screen_on']*(cfg['screen_dimensions'][0]/2), circle_pos[1]]
                    if (cfg['screen_on'] == 1 and mousePos[0] <= -screen_edge):
                        circle_pos[0] = (-((root.winfo_screenwidth - cfg['screen_dimensions'][0])/2)) + 50
                    myCircle.setPos(circle_pos)
#                    testCircle.setPos([circle_pos[0] +cfg['screen_dimensions'][0]/2, circle_pos[1]])
           ########################### SPECIAL ARROW CONDITIONS #########################
                    if (cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True) or (cfg['trial_type'] == 'error_clamp')):
                        arrow.ori = -myRounder(math.degrees(cart2pol([current_pos[0] - cfg['screen_on']*(cfg['screen_dimensions'][0]/2),current_pos[1] + cfg['active_height']/2])[1]), 45)
                        arrowFill.ori = -myRounder(math.degrees(cart2pol([current_pos[0] - cfg['screen_on']*(cfg['screen_dimensions'][0]/2),current_pos[1] + cfg['active_height']/2])[1]), 45)
                except:
                    pass
        ################################ SHOW OBJECTS ################################
                try:
                    if (pos_buffer == 0):
                        pos_buffer = pos_buffer + 1
                    if (show_home == True):
                        startCircle.draw()
                    if (show_target == True):
                        endCircle.draw()
                    if (show_arrow == True):
                        arrow.draw()
                        arrowFill.draw()
                    if (show_cursor == True):
                        myCircle.draw()
#                        testCircle.draw()
                except:
                    pass
            except:
                pass
        except:
            pass
################################ PHASE 1 #####################################
        try:
            if (phase_1 == False):
                if (cfg['trial_type'] == 'cursor'):
                    if (get_dist(circle_pos, startPos) < cfg['circle_radius'] and velocity < 35):
                        phase_1 = True
                        show_home = False
                        show_target = True
                        if (cfg['terminal_feedback'] == True):
                            show_cursor = False
                elif (cfg['trial_type'] == 'no_cursor'):
                    if (get_dist(circle_pos, startPos) < cfg['circle_radius'] and velocity < 35):
                        phase_1 = True
                        show_target = True
                        show_home = False
                        show_cursor = False
                elif (cfg['trial_type'] == 'error_clamp'):
                    if (get_dist(circle_pos, startPos) < cfg['circle_radius'] and velocity < 35):
                        phase_1 = True
                        show_target = True
                        show_home = False
    ################################ PHASE 2 #####################################
            if (phase_1 == True and phase_2 == False):
                if (cfg['trial_type'] == 'cursor'):
                    if (get_dist(circle_pos, endPos) < cfg['circle_radius'] and velocity < 35 and cfg['terminal_feedback'] == False):
                        phase_2 = True
                        show_home = True
                        show_target = False
                    if (cfg['terminal_feedback'] == True and (get_dist(circle_pos, startPos) >= cfg['terminal_multiplier']*get_dist(startPos, endPos)) and phase_1 == True):
                        timer = core.getTime()
                        phase_2 = True
                        show_home = True
                        show_target = False
                        end_point = circle_pos
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
                if (cfg['trial_type'] == 'no_cursor'):
                    ##### STOP WATCH ####
#                    if (pixels_per_sample <= 1 and timerSet == False):
#                        timer_timestamp = current_timestamp
#                        timerSet = True
#                    stop_time = current_timestamp - timer_timestamp
                    
                    if (pixels_per_sample > 1 and timerSet == True):
                        timerSet = False
                        stop_time = 0
                    if (get_dist(circle_pos, startPos) > cfg['circle_radius'] and nc_check_1 == False):       
                        nc_check_1 = True
                        
                    if (get_dist(circle_pos, startPos) > get_dist(startPos, endPos)/2):
                        if current_timestamp > .5:
                            idx = (array(timeArray) > (current_timestamp - .5)).nonzero()[0]
                            avgspeed = mean(sqrt(diff(array(mouseposXArray)[idx])**2 + diff(array(mouseposYArray)[idx])**2) / diff(array(timeArray)[idx]))
                            if avgspeed < 3:
                                phase_2 = True
                                show_target = False
                                show_home = True
                                end_point = circle_pos
                if (cfg['trial_type'] == 'error_clamp'):
                    if (get_dist(circle_pos, endPos) < cfg['circle_radius'] and velocity < 35):
                        end_point = circle_pos
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
#            print 'mouse position: ', mousePos, 'circle position: ', circle_pos, 'screen_edge', -screen_edge
            if (phase_1 == True and phase_2 == True and cfg['return_movement'] == False):
                pass
            else:
                if phase_1 == True:
                    timeArray.append(current_timestamp)
                    mouseposXArray.append(current_pos[0] - (cfg['screen_on']*(cfg['screen_dimensions'][0]/2)))
                    mouseposYArray.append(current_pos[1]*cfg['flipscreen'] + cfg['active_height']/2)
                    cursorposXArray.append(circle_pos[0])
                    cursorposYArray.append(circle_pos[1]*cfg['flipscreen'] + cfg['active_height']/2)
            myWin.flip()
    ################################ PHASE 3 #####################################

            if (phase_1 == True and phase_2 == True):

#                if ((cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True) or (cfg['trial_type'] == 'error_clamp')) and get_dist(circle_pos, startPos) <= get_dist(startPos,endPos)/2):
#                    show_arrow = True
#                    show_arrowFill = True
#                
#                if ((cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True) or (cfg['trial_type'] == 'error_clamp')) and get_dist(circle_pos, startPos) > get_dist(startPos, endPos)/2):
#                    show_arrow = False
#                    show_arrowFill = False
                if ((cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True) or (cfg['trial_type'] == 'error_clamp')) and get_dist(circle_pos, end_point) >= get_dist(startPos,endPos)/10):
                    show_arrow = True
                    show_arrowFill = True 
                    
                if ((cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True) or (cfg['trial_type'] == 'error_clamp')) and get_dist(circle_pos, startPos) > 3*get_dist(startPos, endPos)/20):
                    show_cursor = False
                if ((cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True) or (cfg['trial_type'] == 'error_clamp')) and get_dist(circle_pos, startPos) <= 3*get_dist(startPos, endPos)/20):
                    show_cursor = True
                if (cfg['trial_type'] == 'cursor'  and get_dist(circle_pos, startPos) < cfg['circle_radius'] and velocity < 35 and cfg['terminal_feedback'] == False):
                    timePos_dict['task_num'] = cfg['task_num']
                    timePos_dict['task_name'] = cfg['task_name']
                    timePos_dict['trial_num'] = cfg['trial_num']
                    timePos_dict['trial_type'] = cfg['trial_type']
                    timePos_dict['targetangle_deg'] = cfg['target_angle']
                    timePos_dict['rotation_angle'] = rot_dir*cfg['current_rotation_angle']
                    timePos_dict['homex_px'] = startPos[0]
                    timePos_dict['homey_px'] = startPos[1]*cfg['flipscreen'] + cfg['active_height']/2
                    timePos_dict['targetx_px'] = endPos[0]
                    timePos_dict['targety_px'] = endPos[1]*cfg['flipscreen'] + cfg['active_height']/2
                    timePos_dict['time_s'] = timeArray
                    timePos_dict['mousex_px'] = mouseposXArray
                    timePos_dict['mousey_px'] = mouseposYArray
                    timePos_dict['cursorx_px'] = cursorposXArray 
                    timePos_dict['cursory_px'] = cursorposYArray
                    timePos_dict['terminalfeedback_bool'] = cfg['terminal_feedback']
                    timePos_dict['targetdistance_percmax'] = int(cfg['target_distance_ratio']*100)
                    
                    return timePos_dict

                elif ((cfg['trial_type'] == 'no_cursor' or cfg['trial_type'] == 'error_clamp' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True)) and get_dist(circle_pos, startPos) <= 3*get_dist(startPos, endPos)/20):
                    show_cursor = True
                    if (get_dist(circle_pos, startPos) < cfg['circle_radius']):
                        timePos_dict['task_num'] = cfg['task_num']
                        timePos_dict['task_name'] = cfg['task_name']
                        timePos_dict['trial_num'] = cfg['trial_num']
                        timePos_dict['trial_type'] = cfg['trial_type']
                        timePos_dict['targetangle_deg'] = cfg['target_angle']
                        timePos_dict['rotation_angle'] = rot_dir*cfg['current_rotation_angle']
                        timePos_dict['homex_px'] = startPos[0]
                        timePos_dict['homey_px'] = startPos[1] + cfg['active_height']/2
                        timePos_dict['targetx_px'] = endPos[0]
                        timePos_dict['targety_px'] = endPos[1] + cfg['active_height']/2
                        timePos_dict['time_s'] = timeArray
                        timePos_dict['mousex_px'] = mouseposXArray
                        timePos_dict['mousey_px'] = mouseposYArray
                        timePos_dict['cursorx_px'] = cursorposXArray
                        timePos_dict['cursory_px'] = cursorposYArray
                        timePos_dict['terminalfeedback_bool'] = cfg['terminal_feedback']
                        timePos_dict['targetdistance_percmax'] = int(cfg['target_distance_ratio']*100)
               
                        return timePos_dict
        except:
            pass

############################# RUN EXPERIMENT V2 ###############################
def run_experiment_2(fulls, participant, experiment = {}):
    end_exp = DataFrame({})
    task_save = DataFrame({})
    running = deepcopy(experiment['experiment'])
    settings = deepcopy(experiment['settings'])
    participant_state = deepcopy(experiment['participant'][participant]['state'])
    cfg = {}
    #### Generate seed ####
    participant_seed = participant + settings['experiment_folder']
    
    if experiment['settings']['flipscreen'] == True:
        view_scale = [1, -1]
    else:
        view_scale = [1, 1]
    try:
        addWorkSpaceLimits(experiment['settings']['screen'], cfg)
    except:
        print "Exception adding workspace limits"
    try:
        Win = Window(cfg['screen_dimensions'],
                     winType=cfg['winType'],
                     colorSpace='rgb',
                     fullscr=fulls,
                     name='MousePosition',
                     color=(-1, -1, -1),
                     units='pix',
                     screen=experiment['settings']['screen'],
                     viewScale=view_scale)
#        Win._setCurrent()
    except:
        print "Exception creating Window"
    ### Configure visual feedback settings here
    try:
        arrowFillVert = [(-1 , 1), (-1, -1),(-0.5, 0)]
        arrowFill = ShapeStim(win=Win,
                                     vertices=arrowFillVert,
                                     fillColor=[-1,-1,-1],
                                     size=cfg['circle_radius']*0.6,
                                     lineColor=[-1,-1,-1])
        arrowVert = [(-1, 1),(-1,-1),(1.2,0)]
        arrow = ShapeStim(win=Win,
                                 vertices=arrowVert,
                                 fillColor=[0, 0, 0],
                                 size=cfg['circle_radius']*0.6,
                                 lineColor=[0,0,0])
        if settings['custom_stim_enable'] == True:
            custom_stim_holder = []
            icon_directory = listdir(settings['custom_stim_file'])   
            icon_directory[:] = [png for png in icon_directory if ".png" in png]
            icon_directory_nums = [i.replace('cursor_','') for i in icon_directory]
            icon_directory_nums[:] = [i.replace('target_','') for i in icon_directory_nums]
            indexes = [i.replace('.png','') for i in icon_directory_nums]
            indexes = [int(i) for i in indexes]
            indexes = list(set(indexes))
            for i in indexes:
                try:
                    custom_target = ImageStim(win=Win, units='pix', image=(path.join(settings['custom_stim_file'], 'target_' + str(i) + '.png')))
                    target_x, target_y = list(custom_target.size)   
                    if target_x <= target_y:
                        target_AR = [float(target_x)/float(target_x), float(target_y)/float(target_x)]
                    else:
                        target_AR = [float(target_x)/float(target_y), float(target_y)/float(target_y)]
                    target_size = [z*cfg['icon_diameter']for z in target_AR]
                    custom_target.setSize(target_size)
                except:
                    custom_target = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])
                try:   
                    custom_cursor = ImageStim(win=Win, units='pix', image=(path.join(settings['custom_stim_file'], 'cursor_' + str(i) + '.png')))
                    cursor_x, cursor_y = list(custom_cursor.size)
                    if cursor_x < cursor_y:
                        cursor_AR = [float(cursor_x)/float(cursor_x), float(cursor_y)/float(cursor_x)]
                    else:
                        cursor_AR = [float(cursor_x)/float(cursor_y), float(cursor_y)/float(cursor_y)]
                    cursor_size = [z*cfg['icon_diameter'] for z in cursor_AR]
                    custom_cursor.setSize(cursor_size)
                except:
                    custom_cursor = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])                                
                custom_stim_holder.append([custom_cursor, custom_target])
        if settings['custom_cursor_enable'] == False:
            myCircle = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])
            testCircle = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[-1, 0, 1],
                                     lineColor=[0, 0, 0])
        else:
            try:
                myCircle = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2, image=settings['custom_cursor_file'])
            except:
                myCircle = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])
        if settings['custom_home_enable'] == False:
            startCircle = Circle(win=Win,
                                        radius=cfg['circle_radius'],
                                        lineWidth=2,
                                        edges=32,
                                        units='pix',
                                        fillColor=[-1, -1, -1],
                                         lineColor=[0, 0, 0])
        else:
            try:
                startCircle = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2, image=settings['custom_home_file'])
            except:
                startCircle = Circle(win=Win,
                                        radius=cfg['circle_radius'],
                                        lineWidth=2,
                                        edges=32,
                                        units='pix',
                                        fillColor=[-1, -1, -1],
                                         lineColor=[0, 0, 0])
        if settings['custom_target_enable'] == False:
            endCircle = Circle(win=Win,
                                      radius=cfg['circle_radius'],
                                      lineWidth=2,
                                      edges=32,
                                      units='pix',
                                      fillColor=[-1, -1, -1],
                                      lineColor=[0, 0, 0])
        else:
            try:
                endCircle = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2, image=settings['custom_target_file'])
            except:
                endCircle = Circle(win=Win,
                                      radius=cfg['circle_radius'],
                                      lineWidth=2,
                                      edges=32,
                                      units='pix',
                                      fillColor=[-1, -1, -1],
                                      lineColor=[0, 0, 0])
        Mouse = event.Mouse(win=Win, visible=False)
        screen_info_monitors = screeninfo.get_monitors()
    except Exception as e:
        print e
        print str(e)
    for i in range (0, len(running)):
        if experiment['settings']['flipscreen'] == True:
            running[i]['flipscreen'] = 1
            running[i]['flip_text'] = True
        else:
            running[i]['flipscreen'] = 1
            running[i]['flip_text'] = False
        try:
            running[i]['x11_mouse'] = myMouse()
        except:
            running[i]['poll_type'] = 'psychopy'
        if settings['custom_stim_enable'] == True:
            running[i]['custom_stim'] = custom_stim_holder
        if (len(screen_info_monitors) > 1 and settings['screen'] == 1):
            running[i]['screen_on'] = 1
            running[i]['screen_dimensions'] = cfg['main_screen_dimensions']
        elif (len(screen_info_monitors) > 1 and settings['screen'] == 0):
            running[i]['screen_on'] = -1
            running[i]['screen_dimensions'] = cfg['main_screen_dimensions']
        else:
            running[i]['screen_on'] = 0
            running[i]['screen_dimensions'] = cfg['screen_dimensions']
        running[i]['custom_stim_enable'] = settings['custom_stim_enable']
        running[i]['return_movement'] = experiment['settings']['return_movement']
        running[i]['cursor_circle'] = myCircle
        running[i]['test_circle'] = testCircle
        running[i]['start_circle'] = startCircle
        running[i]['end_circle'] = endCircle
        running[i]['mouse'] = Mouse
        running[i]['win'] = Win
        running[i]['circle_radius'] = cfg['circle_radius']
        running[i]['arrow_stim'] = arrow
        running[i]['arrowFill_stim'] = arrowFill
        running[i]['task_num'] = i + 1
        running[i]['max_distance'] = cfg['active_height']
        running[i]['min_distance'] = cfg['active_height']/2
        running[i]['active_height'] = cfg['active_height']
        running[i]['starting_pos'] = (0, (-cfg['active_height']/2)*running[i]['flipscreen'])
        running[i]['current_rotation_angle'] = 0
        if running[i]['num_targets'] > 1:
            targetList = angle_split(running[i]['min_angle'], running[i]['max_angle'], running[i]['num_targets'])
        elif running[i]['num_targets'] == 1:
            targetList = [running[i]['min_angle']]
        #### FIRST SEED FOR TARGET ANGLES ####
        setParticipantSeed(participant_seed + str(i))
        fulltargetList = shuffleTargets4task(targetList, blocks=int(running[i]['num_trials']/running[i]['num_targets']))
        if (running[i]['trial_type'] != 'pause'):
#            if running[i]['num_targets'] > 1:
#                targetList = angle_split(running[i]['min_angle'], running[i]['max_angle'], running[i]['num_targets'])
#            elif running[i]['num_targets'] == 1:
#                targetList = [running[i]['min_angle']]
            for trial_num in range (0, int(running[i]['num_trials'])):
                running[i]['trial_num'] = trial_num + 1
                if (len(targetList) == 0):
                    targetList = list(fulltargetList)
                if (running[i]['rotation_change_type'] == 'gradual' and running[i]['current_rotation_angle'] != running[i]['rotation_angle'] and trial_num > 0):
                    running[i]['current_rotation_angle'] = running[i]['current_rotation_angle'] + running[i]['rotation_direction']
                if (running[i]['rotation_change_type'] == 'gradual' and running[i]['current_rotation_angle'] == running[i]['rotation_angle'] and trial_num > 0):
                    running[i]['current_rotation_angle'] = running[i]['rotation_angle']
                elif (running[i]['rotation_change_type'] == 'abrupt'):
                    running[i]['current_rotation_angle'] = running[i]['rotation_angle']
#                print running[i]['rotation_change_type'], running[i]['current_rotation_angle'], running[i]['rotation_angle'], 'trial_num: ', trial_num, running[i]['num_trials']
                try:
                    chosen_target = fulltargetList[trial_num]
                except:
                    print "Exception randomizing target"
                running[i]['target_angle'] = chosen_target    
                running[i]['target_distance'] = int(running[i]['max_distance']*running[i]['target_distance_ratio'])
                running[i]['time'] = core.getTime()
#                try:
                exp = trial_runner(running[i])
           
#                except:
#                    print "Exception in running trial_runner function"
                if exp == 'escaped':
                    running[i]['win'].close()
                    experiment['participant'][participant]['angles'] = targetList
                    experiment['participant'][participant]['state'] = [i, trial_num]
                    return DataFrame({})
                else:           
                    df_exp = DataFrame(exp, columns=['task_num','task_name', 'trial_type', 'trial_num', 'terminalfeedback_bool','rotation_angle','targetangle_deg','targetdistance_percmax','homex_px','homey_px','targetx_px','targety_px', 'time_s', 'mousex_px', 'mousey_px', 'cursorx_px', 'cursory_px'])
                    df_exp.to_csv(path_or_buf = path.join("data", settings['experiment_folder'], participant, running[i]['task_name'] + "_" + str(trial_num) + ".csv"), index=False)
                    task_save = concat([task_save, df_exp])
                    end_exp = concat([end_exp, df_exp])
                    experiment['participant'][participant]['angles'] = targetList
                    experiment['participant'][participant]['state'] = [i, trial_num]
#                    targetList.remove(chosen_target)
                    with open(path.join("experiments", settings['experiment_folder'] + ".json"), "wb") as f:
                        dump(experiment, f)
                        f.close()
        elif (running[i]['trial_type'] == 'pause'):
            running[i]['time'] = core.getTime()
            exp = trial_runner(running[i])
        if (running[i]['trial_type'] != 'pause'):
            task_save.to_csv(path_or_buf = path.join("data", settings['experiment_folder'], participant, running[i]['task_name'] + "_Complete" + ".csv"), index=False)
        task_save = DataFrame({})
    running[i]['win'].close()
    return end_exp

def continue_experiment(fulls, participant, experiment = {}):
    end_exp = DataFrame({})
    task_save = DataFrame({})
    running = deepcopy(experiment['experiment'])
    settings = deepcopy(experiment['settings'])
    participant_state = deepcopy(experiment['participant'][participant]['state'])
    cfg = {}
    participant_seed = participant + settings['experiment_folder']  
    continued = 1
    if experiment['settings']['flipscreen'] == True:
        view_scale = [1, -1]
    else:
        view_scale = [1, 1]
    try:
        addWorkSpaceLimits(experiment['settings']['screen'], cfg)
    except:
        print "Exception adding workspace limits"
    try:
        Win = Window(cfg['screen_dimensions'],
                     winType=cfg['winType'],
                     colorSpace='rgb',
                     fullscr=fulls,
                     name='MousePosition',
                     color=(-1, -1, -1),
                     units='pix',
                     screen=experiment['settings']['screen'],
                     viewScale=view_scale)
    except:
        print "Exception creating Window"
    ### Configure visual feedback settings here
    try:
        arrowFillVert = [(-1 , 1), (-1, -1),(-0.5, 0)]
        arrowFill = ShapeStim(win=Win,
                                     vertices=arrowFillVert,
                                     fillColor=[-1,-1,-1],
                                     size=cfg['circle_radius']*0.6,
                                     lineColor=[-1,-1,-1])
        arrowVert = [(-1, 1),(-1,-1),(1.2,0)]
        arrow = ShapeStim(win=Win,
                                 vertices=arrowVert,
                                 fillColor=[0, 0, 0],
                                 size=cfg['circle_radius']*0.6,
                                 lineColor=[0,0,0])
        if settings['custom_stim_enable'] == True:
            custom_stim_holder = []
            icon_directory = listdir(settings['custom_stim_file'])
            icon_directory[:] = [png for png in icon_directory if ".png" in png]
            icon_directory_nums = [i.replace('cursor_','') for i in icon_directory]
            icon_directory_nums[:] = [i.replace('target_','') for i in icon_directory_nums]
            indexes = [i.replace('.png','') for i in icon_directory_nums]
            indexes = [int(i) for i in indexes]
            indexes = list(set(indexes))
            for i in indexes:
                try:
                    custom_target = ImageStim(win=Win, units='pix', image=(path.join(settings['custom_stim_file'], 'target_' + str(i) + '.png')))
                    
                    target_x, target_y = list(custom_target.size)
                    
                    if target_x <= target_y:
                        target_AR = [float(target_x)/float(target_x), float(target_y)/float(target_x)]
                    else:
                        target_AR = [float(target_x)/float(target_y), float(target_y)/float(target_y)]
                    target_size = [z*cfg['icon_diameter']for z in target_AR]
                    custom_target.setSize(target_size)
                except:
                    custom_target = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])
                try:   
                    custom_cursor = ImageStim(win=Win, units='pix', image=(path.join(settings['custom_stim_file'], 'cursor_' + str(i) + '.png')))
                    cursor_x, cursor_y = list(custom_cursor.size)
                    if cursor_x < cursor_y:
                        cursor_AR = [float(cursor_x)/float(cursor_x), float(cursor_y)/float(cursor_x)]
                    else:
                        cursor_AR = [float(cursor_x)/float(cursor_y), float(cursor_y)/float(cursor_y)]
                    cursor_size = [z*cfg['icon_diameter'] for z in cursor_AR]
                    custom_cursor.setSize(cursor_size)
                except:
                    custom_cursor = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])
                                     
                custom_stim_holder.append([custom_cursor, custom_target])
        if settings['custom_cursor_enable'] == False:
            myCircle = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])
            testCircle = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[-1, 0, 1],
                                     lineColor=[0, 0, 0])
        else:
            try:
                myCircle = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2, image=settings['custom_cursor_file'])
            except:
                myCircle = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])
        if settings['custom_home_enable'] == False:
            startCircle = Circle(win=Win,
                                        radius=cfg['circle_radius'],
                                        lineWidth=2,
                                        edges=32,
                                        units='pix',
                                        fillColor=[-1, -1, -1],
                                         lineColor=[0, 0, 0])
        else:
            try:
                startCircle = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2, image=settings['custom_home_file'])
            except:
                startCircle = Circle(win=Win,
                                        radius=cfg['circle_radius'],
                                        lineWidth=2,
                                        edges=32,
                                        units='pix',
                                        fillColor=[-1, -1, -1],
                                         lineColor=[0, 0, 0])
        if settings['custom_target_enable'] == False:
            endCircle = Circle(win=Win,
                                      radius=cfg['circle_radius'],
                                      lineWidth=2,
                                      edges=32,
                                      units='pix',
                                      fillColor=[-1, -1, -1],
                                      lineColor=[0, 0, 0])
        else:
            try:
                endCircle = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2, image=settings['custom_target_file'])
            except:
                endCircle = Circle(win=Win,
                                      radius=cfg['circle_radius'],
                                      lineWidth=2,
                                      edges=32,
                                      units='pix',
                                      fillColor=[-1, -1, -1],
                                      lineColor=[0, 0, 0])
        Mouse = event.Mouse(win=Win, visible=False)
        screen_info_monitors = screeninfo.get_monitors()
        
    except Exception as e:
        print e
        print str(e)
    for i in range (participant_state[0], len(running)):
        if experiment['settings']['flipscreen'] == True:
            running[i]['flipscreen'] = 1
            running[i]['flip_text'] = True
        else:
            running[i]['flipscreen'] = 1
            running[i]['flip_text'] = False
        try:
            running[i]['x11_mouse'] = myMouse()
        except:
            running[i]['poll_type'] = 'psychopy'
        if settings['custom_stim_enable'] == True:
            running[i]['custom_stim'] = custom_stim_holder
        if (len(screen_info_monitors) > 1 and settings['screen'] == 1):
            running[i]['screen_on'] = 1
            running[i]['screen_dimensions'] = cfg['main_screen_dimensions']
        elif (len(screen_info_monitors) > 1 and settings['screen'] == 0):
            running[i]['screen_on'] = -1
            running[i]['screen_dimensions'] = cfg['main_screen_dimensions']
        else:
            running[i]['screen_on'] = 0
            running[i]['screen_dimensions'] = cfg['screen_dimensions']
        running[i]['custom_stim_enable'] = settings['custom_stim_enable']
        running[i]['screen_dimensions'] = cfg['screen_dimensions']
        running[i]['return_movement'] = experiment['settings']['return_movement']
        running[i]['cursor_circle'] = myCircle
        running[i]['test_circle'] = testCircle
        running[i]['start_circle'] = startCircle
        running[i]['end_circle'] = endCircle
        running[i]['mouse'] = Mouse
        running[i]['win'] = Win
        running[i]['circle_radius'] = cfg['circle_radius']
        running[i]['arrow_stim'] = arrow
        running[i]['arrowFill_stim'] = arrowFill
        running[i]['task_num'] = i + 1
        running[i]['max_distance'] = cfg['active_height']
        running[i]['min_distance'] = cfg['active_height']/2
        running[i]['active_height'] = cfg['active_height']
        running[i]['starting_pos'] = (0, (-cfg['active_height']/2)*running[i]['flipscreen'])
        running[i]['current_rotation_angle'] = participant_state[1]
        if running[i]['num_targets'] > 1:
            targetList = angle_split(running[i]['min_angle'], running[i]['max_angle'], running[i]['num_targets'])
        elif running[i]['num_targets'] == 1:
            targetList = [running[i]['min_angle']]
        setParticipantSeed(participant_seed + str(i))
        fulltargetList = shuffleTargets4task(targetList, blocks=int(running[i]['num_trials']/running[i]['num_targets']))
        if (running[i]['trial_type'] != 'pause'):
            for trial_num in range ((participant_state[1])*continued, int(running[i]['num_trials'])):
                continued = 0
                running[i]['trial_num'] = trial_num + 1
                if (len(targetList) == 0):
                    targetList = list(fulltargetList)
                if (running[i]['rotation_change_type'] == 'gradual' and running[i]['current_rotation_angle'] != running[i]['rotation_angle'] and trial_num > 0):
                    running[i]['current_rotation_angle'] = running[i]['current_rotation_angle'] + 1
                elif (running[i]['rotation_change_type'] == 'gradual' and running[i]['current_rotation_angle'] == running[i]['rotation_angle'] and trial_num > 0):
                    running[i]['current_rotation_angle'] = running[i]['rotation_angle']
                elif (running[i]['rotation_change_type'] == 'abrupt'):
                    running[i]['current_rotation_angle'] = running[i]['rotation_angle']
#                print running[i]['current_rotation_angle'], running[i]['rotation_angle']
#                print running[i]['rotation_change_type'], running[i]['current_rotation_angle'], running[i]['rotation_angle'], 'trial_num: ', trial_num, running[i]['num_trials']
                try:
                    chosen_target = fulltargetList[trial_num]
                except:
                    print "Exception randomizing target"
                running[i]['target_angle'] = chosen_target               
                running[i]['target_distance'] = int(running[i]['max_distance']*running[i]['target_distance_ratio'])
                running[i]['time'] = core.getTime()
#                try:
                exp = trial_runner(running[i])
                
#                except:
#                    print "Exception in running trial_runner function"
                if exp == 'escaped':
                    running[i]['win'].close()
                    experiment['participant'][participant]['angles'] = targetList
                    experiment['participant'][participant]['state'] = [i, trial_num]
                    return end_exp
                else:           
                    df_exp = DataFrame(exp, columns=['task_num','task_name', 'trial_type', 'trial_num', 'terminalfeedback_bool','rotation_angle','targetangle_deg','targetdistance_percmax','homex_px','homey_px','targetx_px','targety_px', 'time_s', 'mousex_px', 'mousey_px', 'cursorx_px', 'cursory_px'])
                    df_exp.to_csv(path_or_buf = path.join("data", settings['experiment_folder'], participant, running[i]['task_name'] + "_" + str(trial_num) + ".csv"), index=False)
                    end_exp = concat([end_exp, df_exp])
                    experiment['participant'][participant]['angles'] = targetList
                    experiment['participant'][participant]['state'] = [i, trial_num]
#                    targetList.remove(chosen_target)
                    with open(path.join("experiments", settings['experiment_folder'] + ".json"), "wb") as f:
                        dump(experiment, f)
                        f.close()
        elif (running[i]['trial_type'] == 'pause'):
            running[i]['time'] = core.getTime()
            exp = trial_runner(running[i])
    running[i]['win'].close()
    return end_exp
##### CONTINUE EXPERIMENT RUN V2 ###########
def continue_experiment_2(fulls, participant, experiment = {}, state = []):
    end_exp = DataFrame({})
    task_save = DataFrame({})
    running = deepcopy(experiment['experiment'])
    settings = deepcopy(experiment['settings'])
    participant_state = deepcopy(experiment['participant'][participant]['state'])
    cfg = {}
    #### Generate seed ####
    participant_seed = (sum([ord(c) for c in settings['experiment_folder']]) + (sum([ord(c) for c in participant]) * 9999))
    if experiment['settings']['flipscreen'] == True:
        view_scale = [1, -1]
    else:
        view_scale = [1, 1]
    try:
        addWorkSpaceLimits(experiment['settings']['screen'], cfg)
    except:
        print "Exception adding workspace limits"
    try:
        Win = Window(cfg['screen_dimensions'],
                     winType=cfg['winType'],
                     colorSpace='rgb',
                     fullscr=fulls,
                     name='MousePosition',
                     color=(-1, -1, -1),
                     units='pix',
                     screen=experiment['settings']['screen'],
                     viewScale=view_scale)
#        Win._setCurrent()
    except:
        print "Exception creating Window"
    ### Configure visual feedback settings here
    try:
        arrowFillVert = [(-1 , 1), (-1, -1),(-0.5, 0)]
        arrowFill = ShapeStim(win=Win,
                                     vertices=arrowFillVert,
                                     fillColor=[-1,-1,-1],
                                     size=cfg['circle_radius']*0.6,
                                     lineColor=[-1,-1,-1])
        arrowVert = [(-1, 1),(-1,-1),(1.2,0)]
        arrow = ShapeStim(win=Win,
                                 vertices=arrowVert,
                                 fillColor=[0, 0, 0],
                                 size=cfg['circle_radius']*0.6,
                                 lineColor=[0,0,0])
        if settings['custom_stim_enable'] == True:
            custom_stim_holder = []
            icon_directory = listdir(settings['custom_stim_file'])
            for i in range(1, len(icon_directory)/2 + 1):
                try:
                    custom_target = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2.5, image=(path.join(settings['custom_stim_file'], 'target_' + str(i) + '.png')))
                except:
                    custom_target = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])
                try:   
                    custom_cursor = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2.5, image=(path.join(settings['custom_stim_file'], 'cursor_' + str(i) + '.png')))
                except:
                    custom_cursor = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])
                                     
                custom_stim_holder.append([custom_cursor, custom_target])
        if settings['custom_cursor_enable'] == False:
            myCircle = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])
            testCircle = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[-1, 0, 1],
                                     lineColor=[0, 0, 0])
        else:
            try:
                myCircle = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2, image=settings['custom_cursor_file'])
            except:
                myCircle = Circle(win=Win,
                                     radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])
        if settings['custom_home_enable'] == False:
            startCircle = Circle(win=Win,
                                        radius=cfg['circle_radius'],
                                        lineWidth=2,
                                        edges=32,
                                        units='pix',
                                        fillColor=[-1, -1, -1],
                                         lineColor=[0, 0, 0])
        else:
            try:
                startCircle = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2, image=settings['custom_home_file'])
            except:
                startCircle = Circle(win=Win,
                                        radius=cfg['circle_radius'],
                                        lineWidth=2,
                                        edges=32,
                                        units='pix',
                                        fillColor=[-1, -1, -1],
                                         lineColor=[0, 0, 0])
        if settings['custom_target_enable'] == False:
            endCircle = Circle(win=Win,
                                      radius=cfg['circle_radius'],
                                      lineWidth=2,
                                      edges=32,
                                      units='pix',
                                      fillColor=[-1, -1, -1],
                                      lineColor=[0, 0, 0])
        else:
            try:
                endCircle = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2, image=settings['custom_target_file'])
            except:
                endCircle = Circle(win=Win,
                                      radius=cfg['circle_radius'],
                                      lineWidth=2,
                                      edges=32,
                                      units='pix',
                                      fillColor=[-1, -1, -1],
                                      lineColor=[0, 0, 0])
        Mouse = event.Mouse(win=Win, visible=False)
        screen_info_monitors = screeninfo.get_monitors()
#        pyautogui.moveTo(10, 10)
    except Exception as e:
        print e
        print str(e)
    for i in range (0, len(running)):
        if experiment['settings']['flipscreen'] == True:
            running[i]['flipscreen'] = 1
            running[i]['flip_text'] = True
        else:
            running[i]['flipscreen'] = 1
            running[i]['flip_text'] = False
        try:
            running[i]['x11_mouse'] = myMouse()
        except:
            running[i]['poll_type'] = 'psychopy'
        if settings['custom_stim_enable'] == True:
            running[i]['custom_stim'] = custom_stim_holder
        if (len(screen_info_monitors) > 1 and settings['screen'] == 1):
            running[i]['screen_on'] = 1
            running[i]['screen_dimensions'] = cfg['main_screen_dimensions']
        elif (len(screen_info_monitors) > 1 and settings['screen'] == 0):
            running[i]['screen_on'] = -1
            running[i]['screen_dimensions'] = cfg['main_screen_dimensions']
        else:
            running[i]['screen_on'] = 0
            running[i]['screen_dimensions'] = cfg['screen_dimensions']
        running[i]['custom_stim_enable'] = settings['custom_stim_enable']
        running[i]['return_movement'] = experiment['settings']['return_movement']
        running[i]['cursor_circle'] = myCircle
        running[i]['test_circle'] = testCircle
        running[i]['start_circle'] = startCircle
        running[i]['end_circle'] = endCircle
        running[i]['mouse'] = Mouse
        running[i]['win'] = Win
        running[i]['circle_radius'] = cfg['circle_radius']
        running[i]['arrow_stim'] = arrow
        running[i]['arrowFill_stim'] = arrowFill
        running[i]['task_num'] = i + 1
        running[i]['max_distance'] = cfg['active_height']
        running[i]['min_distance'] = cfg['active_height']/2
        running[i]['active_height'] = cfg['active_height']
        running[i]['starting_pos'] = (0, (-cfg['active_height']/2)*running[i]['flipscreen'])
        running[i]['current_rotation_angle'] = 0
        if running[i]['num_targets'] > 1:
            targetList = angle_split(running[i]['min_angle'], running[i]['max_angle'], running[i]['num_targets'])
        elif running[i]['num_targets'] == 1:
            targetList = [running[i]['min_angle']]
        fulltargetList = tuple(targetList)
        #### FIRST SEED FOR TARGET ANGLES ####
        seed(participant_seed)
        shuffle(targetList)
        if (running[i]['trial_type'] != 'pause'):
#            if running[i]['num_targets'] > 1:
#                targetList = angle_split(running[i]['min_angle'], running[i]['max_angle'], running[i]['num_targets'])
#            elif running[i]['num_targets'] == 1:
#                targetList = [running[i]['min_angle']]
            for trial_num in range (0, int(running[i]['num_trials'])):
                running[i]['trial_num'] = trial_num + 1
                if (len(targetList) == 0):
                    targetList = list(fulltargetList)
                if (running[i]['rotation_change_type'] == 'gradual' and running[i]['current_rotation_angle'] != running[i]['rotation_angle'] and trial_num > 0):
                    running[i]['current_rotation_angle'] = running[i]['current_rotation_angle'] + 1
                if (running[i]['rotation_change_type'] == 'gradual' and running[i]['current_rotation_angle'] == running[i]['rotation_angle'] and trial_num > 0):
                    running[i]['current_rotation_angle'] = running[i]['rotation_angle']
                elif (running[i]['rotation_change_type'] == 'abrupt'):
                    running[i]['current_rotation_angle'] = running[i]['rotation_angle']
#                print running[i]['rotation_change_type'], running[i]['current_rotation_angle'], running[i]['rotation_angle'], 'trial_num: ', trial_num, running[i]['num_trials']
                try:
                    chosen_target = targetList[trial_num%len(targetList)]
                except:
                    print "Exception randomizing target"
                running[i]['target_angle'] = chosen_target
                
                running[i]['target_distance'] = int(running[i]['max_distance']*running[i]['target_distance_ratio'])
                running[i]['time'] = core.getTime()
#                try:
                exp = trial_runner(running[i])
           
#                except:
#                    print "Exception in running trial_runner function"
                if exp == 'escaped':
                    running[i]['win'].close()
                    return DataFrame({})
                else:           
                    df_exp = DataFrame(exp, columns=['task_num','task_name', 'trial_type', 'trial_num', 'terminalfeedback_bool','rotation_angle','targetangle_deg','targetdistance_percmax','homex_px','homey_px','targetx_px','targety_px', 'time_s', 'mousex_px', 'mousey_px', 'cursorx_px', 'cursory_px'])
                    df_exp.to_csv(path_or_buf = path.join("data", settings['experiment_folder'], participant, running[i]['task_name'] + "_" + str(trial_num) + ".csv"), index=False)
                    task_save = concat([task_save, df_exp])
                    end_exp = concat([end_exp, df_exp])
                    experiment['participant'][participant]['angles'] = targetList
                    experiment['participant'][participant]['state'] = [i, trial_num]
#                    targetList.remove(chosen_target)
                    with open(path.join("experiments", settings['experiment_folder'] + ".json"), "wb") as f:
                        dump(experiment, f)
                        f.close()
        elif (running[i]['trial_type'] == 'pause'):
            running[i]['time'] = core.getTime()
            exp = trial_runner(running[i])
        if (running[i]['trial_type'] != 'pause'):
            task_save.to_csv(path_or_buf = path.join("data", settings['experiment_folder'], participant, running[i]['task_name'] + "_Complete" + ".csv"), index=False)
        task_save = DataFrame({})
    running[i]['win'].close()
    return end_exp