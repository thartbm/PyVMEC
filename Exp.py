# with functions that run a trial sequence as passed to it, and stores the data appropriately
from psychopy import event, visual, core
#import pygame as pg
from pygame import QUIT, quit, KEYDOWN, K_SPACE, K_ESCAPE
from pygame import event as pev
from numpy import sqrt, arctan2, cos, sin, linalg, dot, ndarray
import math
from pandas import concat, DataFrame
from random import choice
from Tkinter import Tk
from copy import deepcopy
import sys

try:
    from ctypes import *
except:
    pass
from time import time


root = Tk()
def addWorkSpaceLimits(cfg = {}):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    trimmed_width = int((float(2)/float(3))*float(screen_width))
    trimmed_height = int((float(2)/float(3))*float(screen_height))
    if (trimmed_height*2 < trimmed_width):
        trimmed_width = trimmed_height*2
    else:
        trimmed_height = trimmed_width/2   
    cfg['active_width'] = trimmed_width
    cfg['active_height'] = trimmed_height
    cfg['circle_radius'] = trimmed_height*0.025
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
    pass
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
    ### These variables record timestamps and mouse positions (Used to calculate mouse velocity)
    prev_timestamp = 0
    prev_X = 0
    prev_Y = 0
    prev_X_cursor = 0
    prev_Y_cursor = 0
    velocity = 0
    pixels_per_sample = 0
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
    if cfg['rotation_angle_direction'] == 'Counter-clockwise':
        rot_dir = 1
    elif cfg['rotation_angle_direction'] == 'Clockwise':
        rot_dir = -1
#    pev.clear()
    while (core.getTime() - cfg['time']) < 60:
        ### ESCAPE ### USING PYGAME ####
#        event = pev.wait()
#        if event.type == KEYDOWN:
#            if event.key == K_ESCAPE:
#                myWin.close()
#                return 'escaped'
        ### ESCAPE ### USING PYGLET ####
        if event.getKeys(keyList=['escape']):
            myWin.close()
            return 'escaped'
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
            velocity = (linalg.norm([current_pos[0] - prev_X, current_pos[1] - prev_Y]))/change_in_time           
            pixels_per_sample = velocity*change_in_time
        rotated_X = current_pos[0]*math.cos(math.radians(rot_dir*cfg['current_rotation_angle'])) - current_pos[1]*math.sin(math.radians(rot_dir*cfg['current_rotation_angle']))
        rotated_Y = current_pos[0]*math.sin(math.radians(rot_dir*cfg['current_rotation_angle'])) + current_pos[1]*math.cos(math.radians(rot_dir*cfg['current_rotation_angle']))    
        if (cfg['trial_type'] == 'cursor'):
            if (cfg['rotation_angle'] == 0):
                circle_pos = mousePos
            else:
                circle_pos = [rotated_X, rotated_Y]
        elif (cfg['trial_type'] == 'no_cursor'):
            circle_pos = mousePos
        elif (cfg['trial_type'] == 'error_clamp'):
            circle_pos = startPos
            vector_proj_array = get_vector_projection(get_vect([prev_X, prev_Y], current_pos), get_vect(startPos, endPos))
            vector_proj = ndarray.tolist(vector_proj_array)
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
            circle_pos_clamped = [active_X, active_Y]
########################### SET CURSOR POSITIONS #############################
        if (cfg['trial_type'] == 'error_clamp' and phase_1 == True and stabilize == True):
            circle_pos = circle_pos_clamped
        elif (cfg['trial_type'] == 'error_clamp' and phase_1 == True and stabilize == False):
            circle_pos = startPos
            stabilize = True
        myCircle.setPos(circle_pos)
########################### SPECIAL ARROW CONDITIONS #########################
        if (cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True)):
            arrow.ori = -myRounder(math.degrees(cart2pol([current_pos[0],current_pos[1] + cfg['active_height']/2])[1]), 45)  
            arrowFill.ori = -myRounder(math.degrees(cart2pol([current_pos[0],current_pos[1] + cfg['active_height']/2])[1]), 45)
################################ SHOW OBJECTS ################################
        if (show_home == True):
            startCircle.draw()
        if (show_target == True):
            endCircle.draw()
        if (show_arrow == True):
            arrow.draw()
            arrowFill.draw()
        if (show_cursor == True):
            myCircle.draw()
            
################################ PHASE 1 #####################################
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
                if (pixels_per_sample <= 1 and timerSet == False):
                    timer_timestamp = current_timestamp
                    timerSet = True
                stop_time = current_timestamp - timer_timestamp
                if (pixels_per_sample > 1 and timerSet == True):
                    timerSet = False
                    stop_time = 0  
                if (get_dist(circle_pos, startPos) > cfg['circle_radius'] and nc_check_1 == False):
                    show_home = False
                    show_target = True
                    nc_check_1 = True
                    show_cursor = False
                if (get_dist(circle_pos, startPos) > get_dist(startPos, endPos)/2 and stop_time >= 0.75):
                    phase_2 = True
                    show_target = False
                    show_home = True   
            if (cfg['trial_type'] == 'error_clamp'):
                if (get_dist(circle_pos, endPos) < cfg['circle_radius'] and velocity < 35):
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
        
        if (phase_1 == True and phase_2 == True):
            
            if ((cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True)) and get_dist(circle_pos, startPos) <= get_dist(startPos,endPos)/2):
                show_arrow = True
                show_arrowFill = True
            elif ((cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True)) and get_dist(circle_pos, startPos) > get_dist(startPos, endPos)/2):
                show_arrow = False
                show_arrowFill = False
            if ((cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True)) and get_dist(circle_pos, startPos) > 3*get_dist(startPos, endPos)/20):
                show_cursor = False
                
            if (cfg['trial_type'] == 'cursor'  and get_dist(circle_pos, startPos) < cfg['circle_radius'] and velocity < 35 and cfg['terminal_feedback'] == False):
                timePos_dict['task_num'] = cfg['task_num']
                timePos_dict['task_name'] = cfg['task_name']
                timePos_dict['trial_num'] = cfg['trial_num']
                timePos_dict['trial_type'] = cfg['trial_type']
                timePos_dict['targetangle_deg'] = cfg['target_angle']
                timePos_dict['rotation_angle'] = rot_dir*cfg['rotation_angle']
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
                
            elif ((cfg['trial_type'] == 'no_cursor' or cfg['trial_type'] == 'error_clamp' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True)) and get_dist(circle_pos, startPos) <= 3*get_dist(startPos, endPos)/20):
                show_cursor = True
                if (get_dist(circle_pos, startPos) < cfg['circle_radius']):
                    timePos_dict['task_num'] = cfg['task_num']
                    timePos_dict['task_name'] = cfg['task_name']
                    timePos_dict['trial_num'] = cfg['trial_num']
                    timePos_dict['trial_type'] = cfg['trial_type']
                    timePos_dict['targetangle_deg'] = cfg['target_angle']
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

############################# RUN EXPERIMENT V2 ###############################
def run_experiment_2(fulls, experiment = []):
    end_exp = DataFrame({})
    running = deepcopy(experiment)
    cfg = {}
    addWorkSpaceLimits(cfg)
    Win = visual.Window(cfg['screen_dimensions'], winType=cfg['winType'], colorSpace='rgb', fullscr=fulls, name='MousePosition', color=(-1, -1, -1), units='pix')
    ### Configure visual feedback settings here
    arrowFillVert = [(-1 , 1), (-1, -1),(-0.5, 0)]
    arrowFill = visual.ShapeStim(win=Win,
                                 vertices=arrowFillVert,
                                 fillColor=[-1,-1,-1],
                                 size=cfg['circle_radius']*0.6,
                                 lineColor=[-1,-1,-1])
    arrowVert = [(-1, 1),(-1,-1),(1.2,0)]
    arrow = visual.ShapeStim(win=Win,
                             vertices=arrowVert,
                             fillColor=[0, 0, 0],
                             size=cfg['circle_radius']*0.6,
                             lineColor=[0,0,0])
    
    myCircle = visual.Circle(win=Win,
                             radius=cfg['circle_radius'],
                             edges=32,
                             units='pix',
                             fillColor=[0, 0, 0],
                             lineColor=[0, 0, 0])
    startCircle = visual.Circle(win=Win,
                                radius=cfg['circle_radius'],
                                lineWidth=2,
                                edges=32,
                                units='pix',
                                fillColor=[-1, -1, -1],
                                 lineColor=[0, 0, 0])
    endCircle = visual.Circle(win=Win,
                              radius=cfg['circle_radius'],
                              lineWidth=2,
                              edges=32,
                              units='pix',
                              fillColor=[-1, -1, -1],
                              lineColor=[0, 0, 0]) 

    
    Mouse = event.Mouse(win=Win, visible=False)
    for i in range (0, len(experiment)):
        try:
            running[i]['x11_mouse'] = myMouse()
        except:
            running[i]['poll_type'] = 'psychopy'
        running[i]['cursor_circle'] = myCircle
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
        running[i]['starting_pos'] = (0, -cfg['active_height']/2)
        running[i]['current_rotation_angle'] = 0
        targetList = angle_split(running[i]['min_angle'], running[i]['max_angle'], running[i]['num_targets'])
        fulltargetList = tuple(targetList)
        if (running[i]['trial_type'] != 'pause'):
            targetList = angle_split(running[i]['min_angle'], running[i]['max_angle'], running[i]['num_targets'])          
            for trial_num in range (0, int(running[i]['num_trials'])):
                running[i]['trial_num'] = trial_num + 1
                if (len(targetList) == 0):
                    targetList = list(fulltargetList)
                if (running[i]['rotation_change_type'] == 'gradual' and running[i]['current_rotation_angle'] != 'rotation_angle' and trial_num > 0):
                    running[i]['current_rotation_angle'] = running[i]['current_rotation_angle'] + 1
                elif (running[i]['rotation_change_type'] == 'abrupt'):
                    running[i]['current_rotation_angle'] = running[i]['rotation_angle']
#                print running[i]['rotation_change_type'], running[i]['current_rotation_angle'], running[i]['rotation_angle'], 'trial_num: ', trial_num, running[i]['num_trials']
                chosen_target = choice(targetList)
                running[i]['target_angle'] = chosen_target
                targetList.remove(chosen_target)
                running[i]['target_distance'] = int(running[i]['max_distance']*running[i]['target_distance_ratio'])
                running[i]['time'] = core.getTime()
                exp = trial_runner(running[i])
                if exp == 'escaped':
                    return end_exp
                else:
                    df_exp = DataFrame(exp, columns=['task_num','task_name', 'trial_type', 'trial_num', 'terminalfeedback_bool','rotation_angle','targetangle_deg','targetdistance_percmax','homex_px','homey_px','targetx_px','targety_px', 'time_s', 'mousex_px', 'mousey_px', 'cursorx_px', 'cursory_px'])              
                    end_exp = concat([end_exp, df_exp])
        elif (running[i]['trial_type'] == 'pause'):
            running[i]['time'] = core.getTime()
            exp = trial_runner(running[i])
    running[i]['win'].close()
    return end_exp
