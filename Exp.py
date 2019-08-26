# with functions that run a trial sequence as passed to it, and stores the data appropriately
from psychopy.visual import Window, Circle, ShapeStim, TextStim, ImageStim
from psychopy import event, core
from psychopy.visual import shape
from os import path, listdir
from json import dump
import pyautogui
import pygame
#from pygame import QUIT, quit, KEYDOWN, K_SPACE, K_ESCAPE
#from pygame import event as pev
from numpy import sqrt, arctan2, cos, sin, linalg, dot, ndarray, array, diff, mean, arange, pi, dot
import csv
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

    # why all this complicated code?
    #if (len(s) == 1 and screen == 0):
    #    screen_width = root.winfo_screenwidth()
    #    screen_height = root.winfo_screenheight()
    #elif(len(s) > 1 and screen == 0):
    #    screen_width = int(str(s[0]).strip('monitor(').partition('x')[0])
    #    screen_height = int(str(s[0]).strip('monitor(').partition('x')[2].partition('+')[0])
    #    cfg['main_screen_dimensions'] = [int(str(s[1]).strip('monitor(').partition('x')[0]), int(str(s[1]).strip('monitor(').partition('x')[2].partition('+')[0])]
    #else:
    #    screen_width = int(str(s[1]).strip('monitor(').partition('x')[0])
    #    screen_height = int(str(s[1]).strip('monitor(').partition('x')[2].partition('+')[0])
    #    cfg['main_screen_dimensions'] = [int(str(s[0]).strip('monitor(').partition('x')[0]), int(str(s[0]).strip('monitor(').partition('x')[2].partition('+')[0])]

    screen_width = s[screen].width
    screen_height = s[screen].height
    cfg['main_screen_dimensions'] = [screen_width, screen_height]
    cfg['main_screen_offset'] = [s[screen].x, s[screen].y]

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

    # where is the home position calculated?
    cfg['home_pos'] = [0, -0.35 * trimmed_height]

    # active height is 1 normalized screen unit: this is what should be stored in the cfg
    # we don't need the active width all that much... it's just 2 normalized screen units
    # circle_radius and icon diameter are maybe not workspace limits

    cfg['screen_dimensions'] = [screen_width, screen_height]
    cfg['winType'] = 'pyglet'


    return cfg

# this try/except:
# 1: has to add the psychopy mouse object in the except statement
# 2: should be in a function to add a mouse object to the overall cfg
# 3: be called once, with no testing of which mouse object to use at any later point

# there is no window object yet? how does this make sense?

#cfg['psyMouse'] = event.Mouse(visible = False, newPos = None, win = cfg['win'])
#
#try:
#    class myMouse:
#        Xlib = CDLL("libX11.so.6")
#        display = Xlib.XOpenDisplay(None)
#        if display == 0: sys.exit(2)
#        w = Xlib.XRootWindow(display, c_int(0))
#        (root_id, child_id) = (c_uint32(), c_uint32())
#        (root_x, root_y, win_x, win_y) = (c_int(), c_int(), c_int(), c_int())
#        mask = c_uint()
#
#        width = cfg['main_screen_dimensions'][0]
#        height = cfg['main_screen_dimensions'][1]
#
#        x_offset = cfg['main_screen_offset'][0]
#        y_offset = cfg['main_screen_offset'][1]
#
#        def Pos(self):
#            ret = self.Xlib.XQueryPointer(self.display, c_uint32(self.w), byref(self.root_id), byref(self.child_id), byref(self.root_x), byref(self.root_y), byref(self.win_x), byref(self.win_y), byref(self.mask))
#            if ret == 0: sys.exit(1)
#            return [self.root_x.value - (self.width/2) - x_offset, -1 * (self.root_y.value - (self.height/2) - y_offset), time()] # c_int can't be used for regular Python math, their values are ints - and we return the current time
#except:
#    # create an identically named object with identical behavior based on PsychoPy?
#    print ('not using xLib')
#
# 	 	class myMouse:
#
# 		    def Pos(self):
# 		    	#print('PsychoPy mouse')
# 		     	[X,Y] = cfg['psyMouse'].getPos()
# 		     	return [X,Y,time()]
#
#cfg['mouse'] = myMouse()





# function not used?
#def moveMouse(x,y):
#    myMouse.setPos([x,y])
#    myWin.winHandle._mouse_x = x  # hack to change pyglet window
#    myWin.winHandle._mouse_y = y

def myRounder(x, base):
    return int(base * round(float(x)/base))

def vector_rotate(node, center, angle):
    vector_X = center[0] + (node[0] - center[0])*math.cos(math.radians(angle)) - (node[1] - center[1])*math.sin(math.radians(angle))
    vector_Y = center[1] + (node[0] - center[0])*math.sin(math.radians(angle)) + (node[1] - center[1])*math.cos(math.radians(angle))
    return [vector_X, vector_Y]


# what is this for???
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

# this doesn't need to be a function as this code should be called only once: at the start of the experiment
def setParticipantSeed(participant):
    seed(sum([ord(c) for c in participant]))


def shuffleTargets4task(targets, blocks):
    taskTargets = []
    for block in range(blocks):
      shuffle(targets)
      taskTargets = taskTargets + targets
    return(taskTargets)


# do we use this?
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

# I could be wrong, but it seems to me that all of the following stuff can be done without (big) libraries/modules
# so we can reduce the annoyance of the many files that need to be copied every time someone uses this in class...

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
    # is this better than just doing pythagoras in 1 line?

def get_vect(select_pos, target_pos):
    vector = [target_pos[0] - select_pos[0], target_pos[1] - select_pos[1]]
    return vector
    # replace with target_pos - select_pos ? # hmmm... doesn't work in Python

def get_uvect(vector): # what is sthis for?
    uvect = vector/linalg.norm(vector)
    return uvect

def get_vector_projection(moving_vect, static_vect):
    static_uvect = get_uvect(static_vect)
    scalar_proj = dot(moving_vect, static_uvect)
    return scalar_proj*static_uvect

def get_clamped_vector(moving_vect, static_vect):
    moving_magnitude = linalg.norm(moving_vect)
    static_uvect = get_uvect(static_vect)
    clamped_vector = moving_magnitude*static_uvect
    return clamped_vector

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


# great function, but it's not used...
#def pause_experiment(cfg={}):
#    print('running pause task as task')
#    myWin = cfg['win']
#    instruction = cfg['pause_instruction']
#    counter_text = TextStim(myWin, text=str(cfg['pausetime']), pos=(0, 40), color=( 1, 1, 1))
#    instruction_text = TextStim(myWin, text=instruction, pos=(0,0), color=( 1, 1, 1))
#    end_text = TextStim(myWin, text="Press space to continue", pos=(0,-40), color=( 1, 1, 1))
#    while ((core.getTime() - cfg['time']) < cfg['pausetime']):
#        counter_text.setText("{:0.0f}".format((cfg['pausetime'] - (core.getTime() - cfg['time']))))
#        instruction_text.draw()
#        counter_text.draw()
#        myWin.flip()
#    if (cfg['pause_button_wait'] == True):
#        instruction_text.draw()
#        if (cfg['pausetime'] > 0):
#            counter_text.draw()
#        end_text.draw()
#        myWin.flip()
#        event.waitKeys(keyList=['space'])


def trial_runner(cfg={}):

    try:
        myWin=cfg['win'] # excellent, all the copies in running[] are not used? oh no... cfg is now running
        if (cfg['trial_type'] == 'pause'): # why does a TRIAL runner have code for a pause TASK?
            # I'm assuming this is not used...
            instruction = cfg['pause_instruction']
            counter_text = TextStim(myWin, text=str(cfg['pausetime']), flipVert=cfg['flip_text'], pos=(0, 40*cfg['flipscreen']), color=( 1, 1, 1))
            instruction_text = TextStim(myWin, text=instruction, pos=(0,0), flipVert=cfg['flip_text'], color=( 1, 1, 1))
            end_text = TextStim(myWin, text="Press space to continue", pos=(0,-40*cfg['flipscreen']), flipVert=cfg['flip_text'], color=( 1, 1, 1))
#            pyautogui.moveTo(root.winfo_screenwidth() - 50, root.winfo_screenheight() - 50)
            #pyautogui.click() # does this need some coordinates?
            #counter_text.setText("{:0.0f}".format((cfg['pausetime'] - (core.getTime() - cfg['time']))))
            while ((core.getTime() - cfg['time']) < cfg['pausetime']):
                counter_text.setText("{:0.0f}".format((cfg['pausetime'] - (core.getTime() - cfg['time']))))
                instruction_text.draw()
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

        end_X = cfg['starting_pos'][0] + (cfg['target_distance'] * math.cos(math.radians(cfg['target_angle'])))
        end_Y = (cfg['starting_pos'][1] + ((cfg['target_distance'] * math.sin(math.radians(cfg['target_angle']))))) * cfg['flipscreen'] #- cfg['active_height']/2)*cfg['flipscreen']
        ### Creates Mouse object

        #print('creating mouse object for EVERY TRIAL (!), and long after the workspace setup is done???')
        # oh wait... it seems that the trial_runner doesn't run a trial, but a whole task
        # still

        #if (cfg['poll_type'] == 'psychopy'):
        #    myMouse = cfg['mouse']
        #    ### Gets current CPU Time
        #    myTime = cfg['time']
        #elif (cfg['poll_type'] == 'x11'):
        #    myMouse = cfg['x11_mouse']
        #    ### Gets current CPU Time....
        #    myTime = myMouse.Pos()[2]

        # WHY?! why are we getting time samples asynchronously from the mouse samples? it makes no sense...
        # only do this when also getting the mouse position at the same time... this completely undoes the only advantage of the X11 system: more accurately timed samples

        # myMouse should not be used:
        # cfg['mouse'] should be used....

        pos = cfg['mouse'].Pos() # now, position and time are sampled at the same time...

        # set distance criterion for reaching target depending on if icons are used or not
        dist_criterion = cfg['circle_radius']
        if (cfg['custom_stim_enable'] == False):
            ### Creates cursor circle Object
            myCircle = cfg['cursor_circle']
            testCircle = cfg['test_circle']
            ### Creates a Target circle
            endCircle = cfg['end_circle']
        elif (cfg['custom_stim_enable'] == True):
            rng = choice(cfg['custom_stim'])
            #print rng
            myCircle = rng[0]
            endCircle = rng[1]
            dist_criterion = 2 * dist_criterion
        ### Creates a circle object to be used as starting point
        startCircle = cfg['start_circle']

        ### Define Parameters here
        startPos = cfg['starting_pos'] # start circle should be at starting pos, but this is never explicitly set nor implicitly assumed in this function (trial_runner which is a task_runner)
        #print('start pos:')
        #print(startPos)
        # which if these two are we using?
        arrow=cfg['arrow_stim']
        arrowFill=cfg['arrowFill_stim']

        endPos=[end_X, end_Y] # doesn't it make more sense to put this right at after calculating end_X and end_Y?

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
        stabilize = False
        screen_edge = (root.winfo_screenwidth()/2) - (cfg['screen_on']*cfg['screen_dimensions'][0])
        # what is 'screen_egde' for?

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
        print "error in Block 1" # what is block 1?
        print e

    if cfg['rotation_angle_direction'] == 'Counter-clockwise': # shouldn't we just take the sign of the rotation?
        rot_dir = 1
    elif cfg['rotation_angle_direction'] == 'Clockwise':
        rot_dir = -1


    # is this while loop creating frames and storing samples until the trial is finished?
    # why is there a limit of 2 minutes here? what happens if someone does not get to the target in 2 minutes? do they go to the next trial... it seems better to me to exit the experiment without saving data, so we can 'continue run' and don't waste lots of disk space
    #print('starting sample/frame loop')
    while (core.getTime() - cfg['time']) < 120:
        try:

            # why is this try statement here? we're immediately moving on to the next one anyway...



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
                #print('getting mouse position:')

                ##print('deciding on mouse object again?')
                #if (cfg['poll_type'] == 'psychopy'):
                #    mousePos = [myMouse.getPos()[0], myMouse.getPos()[1]*cfg['flipscreen']]
                #    current_pos = mousePos
                #    current_timestamp = core.getTime() - myTime
                #elif (cfg['poll_type'] == 'x11'):
                #    # whyyy?
                #    # the mouse object is called 3 separate times to get the X coordinate, the Y coordinate and the time?
                #    # one call is better!
                #    # and it ensures that the time sample is better matched to the position coordinates...
                #    mousePos = [myMouse.Pos()[0], myMouse.Pos()[1]*cfg['flipscreen']] # screen flipping should be done in the mouse object?
                #    current_pos = mousePos
                #    current_timestamp = myMouse.Pos()[2] - myTime

                mousePos = cfg['mouse'].Pos()

                current_pos = [mousePos[0], mousePos[1]]
                current_timestamp = mousePos[2]
                #print(mousePos)
        ########################## SPECIAL CURSOR CONFIGURATIONS #####################
                if (prev_timestamp != 0):
                    change_in_time = current_timestamp - prev_timestamp
                    velocity = (linalg.norm([current_pos[0] - prev_X, current_pos[1] - prev_Y]))/change_in_time # this is not velocity, but distance
                    pixels_per_sample = velocity*change_in_time # this is velocity

                # Julius' previous version (doesn't use start position, but position, cold calculated on every sample)
                #rotated_X, rotated_Y = vector_rotate(mousePos, [0 + (cfg['screen_on']*(cfg['screen_dimensions'][0]/2)), -cfg['active_height']/2], cfg['current_rotation_angle'])

                # Marius' previous version (does use start position, but doesn't work on flipped screens)
                #rotated_X, rotated_Y = vector_rotate(mousePos, startPos, cfg['current_rotation_angle'])

                # trying to implement properly with rotation matrix
                # (although the matrix should be calculated once for a trial, not on every frame...)

                #print(pi)
                theta = (cfg['current_rotation_angle']/180.)*pi
                #print(theta)
                R = array([[cos(theta),-1*sin(theta)],[sin(theta),cos(theta)]])
                #print(R)
                rotpos = dot(R,array([mousePos[0]-startPos[0],mousePos[1]-startPos[1]]))
                rotated_X = rotpos[0]+startPos[0]
                rotated_Y = rotpos[1]+startPos[1]

                #print(rotated_X, rotated_Y)

                if (cfg['trial_type'] == 'cursor'):
                    if (cfg['current_rotation_angle'] == 0):
                        circle_pos = current_pos
                    else:
                        circle_pos = [rotated_X, rotated_Y] # we don't have to if-else this, we can just use the rotated position all the time, right?
                elif (cfg['trial_type'] == 'no_cursor'):
                    if (cfg['current_rotation_angle'] == 0):
                        circle_pos = current_pos
                    else:
                        circle_pos = [rotated_X, rotated_Y] # SAME HERE?
                elif (cfg['trial_type'] == 'error_clamp'):
                    circle_pos = current_pos
                    #vector_proj_array = get_clamped_vector(get_vect(startPos, mousePos), get_vect(startPos, endPos))
                    #vector_proj = ndarray.tolist(vector_proj_array)
                    #rotated_X_clamped, rotated_Y_clamped = vector_rotate([vector_proj[0] + (cfg['screen_on']*(cfg['screen_dimensions'][0]/2)), vector_proj[1] - startPos[1]], startPos, cfg['current_rotation_angle'])

                    home_dist = get_dist(current_pos, startPos)
                    target_dist = get_dist(current_pos, endPos)

                    cursor_angle = cfg['target_angle'] + cfg['current_rotation_angle']
                    #if (target_dist > cfg['target_distance']) :
                    #  cursor_angle = cursor_angle + 180

                    rotated_X_clamped = (math.cos(math.radians(cursor_angle)) * home_dist) + startPos[0]
                    rotated_Y_clamped = ((math.sin(math.radians(cursor_angle)) * home_dist) + startPos[1]) * cfg['flipscreen']

                    # we still have to multiply by flipscreen?


#                    cursor_direction_vector = vector_projection(get_vect(startPos, mousePos), get_vect(startPos, endPos))
#                    clamped_X_vector = vector_proj[0]
#                    clamped_Y_vector = vector_proj[1]
#                    if (phase_1 == False):
#                        active_X = circle_pos[0]
#                        active_Y = circle_pos[1]
#                    else:
##                        if (active_Y < startPos[1] - 20 and clamped_Y_vector < 0):
##                            active_X = active_X - clamped_X_vector
##                            active_Y = active_Y - clamped_Y_vector
##                        else:
##                            active_X = prev_X_cursor + clamped_X_vector
##                            active_Y = prev_Y_cursor + clamped_Y_vector
#                        active_X = vector_proj[0]
#                        active_Y = vector_proj[1]
#                    circle_pos_clamped = [vector_proj[0] + (cfg['screen_on']*(cfg['screen_dimensions'][0]/2)), vector_proj[1] - cfg['active_height']/2]
                    # whyyy?
                    # we are calculating this position when we don't even know if it's needed?
                    # only do this for clamped (&& rotation !=0) trials?
                    circle_pos_clamped = [rotated_X_clamped, rotated_Y_clamped]
                #print('mouse position:')
                #print(mousePos)

            except e:
                print('error in main mouse/cursor position block:')
                print(e)
                pass
    ########################### SET CURSOR POSITIONS #############################
            try:
                try:
                    if (cfg['trial_type'] == 'error_clamp' and phase_1 == True and phase_2 == False and stabilize == True):
                        circle_pos = circle_pos_clamped
                    if (cfg['trial_type'] == 'error_clamp' and phase_1 == True and phase_2 == True and stabilize == True):
                        # wut?
                        # if you are not on the zeroeth screen, we subtract half the window width?
                        # that does not correct for the size in the vitual desktop... and this should be done in the X11 mouse object (but not the PsychoPy mouse object, as PsychoPy does it for you)
                        # circle_pos = [circle_pos[0] - cfg['screen_on']*(cfg['screen_dimensions'][0]/2), circle_pos[1]]
                        circle_pos = [circle_pos[0], circle_pos[1]] # circle pos = circle pos?
                    elif (cfg['trial_type'] == 'error_clamp' and phase_1 == True and stabilize == False):
                        circle_pos = startPos
                        stabilize = True
                    if cfg['trial_type'] != 'error_clamp' or (cfg['trial_type'] == 'error_clamp' and phase_1 == False):
                        #circle_pos = [circle_pos[0] - cfg['screen_on']*(cfg['screen_dimensions'][0]/2), circle_pos[1]]
                        circle_pos = [circle_pos[0], circle_pos[1]]
                    if (cfg['screen_on'] == 1 and mousePos[0] <= -screen_edge):
                        # what is this for?
                        # does this put the cursor in the lower corner at the start of the experiment? whyyyy?
                        circle_pos[0] = circle_pos[0] # (-((root.winfo_screenwidth - cfg['screen_dimensions'][0])/2)) + 50
                    myCircle.setPos(circle_pos)
                    # should we not set the cursor position for the
#                    testCircle.setPos([circle_pos[0] +cfg['screen_dimensions'][0]/2, circle_pos[1]])
           ########################### SPECIAL ARROW CONDITIONS #########################
                    if (cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True) or (cfg['trial_type'] == 'error_clamp')):

                        # everything should be calculated relative to the home position, so that one of the first things to do on every sample is calculated the relative position of stuff
                        # where does current_pos come from... don't we need circle_pos?
                        relPos = [circle_pos[0] - startPos[0], circle_pos[1] - startPos[1]]

                        orientation = -myRounder(math.degrees(cart2pol(relPos)[1]),45)

                        # ori is in degrees, and like a clock: 0 is upward, positive is clockwise
                        arrow.ori = orientation
                        arrowFill.ori = orientation

                        # previous section:
                        #arrow.ori = -myRounder(math.degrees(cart2pol([current_pos[0] - cfg['screen_on']*(cfg['screen_dimensions'][0]/2),current_pos[1] + cfg['active_height']/2])[1]), 45)
                        #arrowFill.ori = -myRounder(math.degrees(cart2pol([current_pos[0] - cfg['screen_on']*(cfg['screen_dimensions'][0]/2),current_pos[1] + cfg['active_height']/2])[1]), 45)

                except:
                    pass # huh? we should do *something* when catching an error... why else do we have try/excepts?
        ################################ SHOW OBJECTS ################################
                try:
                    if (pos_buffer == 0):
                        pos_buffer = pos_buffer + 1
                    if (show_home == True):
                        startCircle.draw() # home position
                    if (show_target == True):
                        endCircle.draw()   # target position
                    if (show_arrow == True):
                        #print('drawing black and gray arrows on top of each other?')
                        arrow.draw()
                        arrowFill.draw()
                    if (show_cursor == True):
                        myCircle.draw()    # cursor?
#                        testCircle.draw()
                except:
                    pass # don't just pass this... what has failed?
            except:
                pass # what has failed?
        except:
            pass # what has failed?
################################ PHASE 1 #####################################
        # phase 1 is getting to the home position (usually over very soon)
        try:
            if (phase_1 == False):
                if (cfg['trial_type'] == 'cursor'):
                    if (get_dist(circle_pos, startPos) < dist_criterion and velocity < 35):
                        phase_1 = True
                        show_home = False
                        show_target = True
                        if (cfg['terminal_feedback'] == True):
                            show_cursor = False
                elif (cfg['trial_type'] == 'no_cursor'):
                    if (get_dist(circle_pos, startPos) < dist_criterion and velocity < 35):
                        phase_1 = True
                        show_target = True
                        show_home = False
                        show_cursor = False
                elif (cfg['trial_type'] == 'error_clamp'):
                    if (get_dist(circle_pos, startPos) < dist_criterion and velocity < 35):
                        phase_1 = True
                        show_target = True
                        show_home = False
                        if (cfg['terminal_feedback'] == True):
                            show_cursor = False
    ################################ PHASE 2 #####################################
        # phase 2 is getting to the target
            if (phase_1 == True and phase_2 == False):
                if (cfg['trial_type'] == 'cursor'):
                    if (get_dist(circle_pos, endPos) < dist_criterion and velocity < 35 and cfg['terminal_feedback'] == False):
                        phase_2 = True
                        show_home = True
                        show_target = False


                    #if (cfg['terminal_feedback'] == True and (get_dist(circle_pos, startPos) >= cfg['terminal_multiplier']*get_dist(startPos, endPos)) and phase_1 == True):
                    if (cfg['terminal_feedback'] == True and (get_dist(circle_pos, startPos) >= cfg['target_distance']) and phase_1 == True):
                        #timer = core.getTime() # this time is not what we need...
                        terminal_start_time = time()
                        phase_2 = True
                        show_home = True
                        show_target = False # why is the target switched of now? owww... because the terminal feedback is handled by it's own loop, not in the main loop... not good
                        #show_target = True  # it should be switched of with the feedback
                        # no, the feedback should be just beyond the target, according to the terminal_multiplier, and this should be shown whenever people reach as far as the target is...
                        # end_point = circle_pos

                        relPos = [circle_pos[0] - startPos[0], circle_pos[1] - startPos[1]]
                        #print(relPos)
                        #print(cart2pol(relPos))
                        terminal_feedback_angle = math.degrees(cart2pol(relPos)[1])
                        terminal_distance = cfg['target_distance'] * cfg['terminal_multiplier']
                        terminal_X = (math.cos(math.radians(terminal_feedback_angle)) * terminal_distance) + startPos[0]
                        terminal_Y = ((math.sin(math.radians(terminal_feedback_angle)) * terminal_distance) + startPos[1]) * cfg['flipscreen'] # cfg['flipscreen'] is actually running[i]['flipscreen'], and *always* 1
                        myCircle.pos = [terminal_X, terminal_Y]
                        # the rest of the experiment should continue working while displaying this... that is... why do we go into another while loop?
                        end_point = circle_pos # this is for determining where a reach ended, and how far people have moved from it (for showing arrow feedback)

                        #print('time:')
                        #print(current_timestamp)
                        #print(terminal_start_time)
                        #print(current_timestamp - terminal_start_time)

                        show_terminal = (current_timestamp - terminal_start_time) < cfg['terminal_feedback_time']
                        #print(show_terminal)

                        while (show_terminal):

                            # show feedback:
                            endCircle.draw()
                            myCircle.draw()
                            myWin.flip()
                            #print('flipped window, still in terminal feedback loop')
                            # collect data:

                            mousePos = cfg['mouse'].Pos()
                            current_pos = [mousePos[0], mousePos[1]]
                            current_timestamp = mousePos[2]
                            #print('got mouse position and time, still in terminal feedback loop')
                            timeArray.append(current_timestamp) # what is myTime?
                            mouseposXArray.append(current_pos[0])
                            mouseposYArray.append(current_pos[1] - startPos[1])
                            cursorposXArray.append(rotated_X)
                            cursorposYArray.append(rotated_Y - startPos[1])
                            #print('stored data in vectors, still in terminal feedback loop')

                            show_terminal = (current_timestamp - terminal_start_time) < cfg['terminal_feedback_time']

                            #print(show_terminal)

                        #print('show terminal loop ended...')
                        #print((current_timestamp - terminal_start_time) < cfg['terminal_feedback_time'])

                if (cfg['trial_type'] == 'no_cursor'):
                    ##### STOP WATCH ####
#                    if (pixels_per_sample <= 1 and timerSet == False):
#                        timer_timestamp = current_timestamp
#                        timerSet = True
#                    stop_time = current_timestamp - timer_timestamp
                    #                    print(cursor_angle)
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
                    if cfg['terminal_feedback'] == False and abs(cfg['current_rotation_angle']) == 0:
                        if (get_dist(circle_pos, endPos) < cfg['circle_radius'] and velocity < 35):
                            end_point = circle_pos
                            phase_2 = True
                            show_home = True
                            show_cursor = False
                            show_target = False
                    elif cfg['terminal_feedback'] == False and abs(cfg['current_rotation_angle']) > 0:
                        if (get_dist(circle_pos, startPos) >= get_dist(startPos, endPos) and velocity < 35):
                            #print('putting end_pos at circle_pos, instead of just beyond the target?') # why is the terminal multiplier not used? that is the only thing it should be used for...
                            end_point = circle_pos
                            phase_2 = True
                            show_home = True
                            show_cursor = False
                            show_target = False
                    #elif (cfg['terminal_feedback'] == True and (get_dist(circle_pos, startPos) >= cfg['terminal_multiplier']*get_dist(startPos, endPos)) and phase_1 == True):
                    # why is the logic for terminal feedback implemented twice?
                    elif (cfg['terminal_feedback'] == True and (get_dist(circle_pos, startPos) >= cfg['target_distance']) and phase_1 == True):
                        timer = core.getTime()
                        phase_2 = True
                        show_home = True
                        show_target = False
                        relPos = [circle_pos[0] - startPos[0], circle_pos[1] - startPos[1]]
                        #print(relPos)
                        #print(cart2pol(relPos))
                        terminal_feedback_angle = math.degrees(cart2pol(relPos)[1])
                        terminal_distance = cfg['target_distance'] * cfg['terminal_multiplier']
                        terminal_X = (math.cos(math.radians(terminal_feedback_angle)) * terminal_distance) + startPos[0]
                        terminal_Y = ((math.sin(math.radians(terminal_feedback_angle)) * terminal_distance) + startPos[1]) * cfg['flipscreen']
                        myCircle.pos = [terminal_X, terminal_Y]
                        end_point = circle_pos



                        #print('time:')
                        #print(current_timestamp)
                        #print(terminal_start_time)
                        #print(current_timestamp - terminal_start_time)

                        show_terminal = (current_timestamp - terminal_start_time) < cfg['terminal_feedback_time']
                        #print(show_terminal)

                        while (show_terminal):

                            # show feedback:
                            endCircle.draw()
                            myCircle.draw()
                            myWin.flip()
                            #print('flipped window, still in terminal feedback loop')
                            # collect data:

                            mousePos = cfg['mouse'].Pos()
                            current_pos = [mousePos[0], mousePos[1]]
                            current_timestamp = mousePos[2]
                            #print('got mouse position and time, still in terminal feedback loop')
                            timeArray.append(current_timestamp) # what is myTime?
                            mouseposXArray.append(current_pos[0])
                            mouseposYArray.append(current_pos[1] - startPos[1])
                            cursorposXArray.append(rotated_X)
                            cursorposYArray.append(rotated_Y - startPos[1])
                            #print('stored data in vectors, still in terminal feedback loop')

                            show_terminal = (current_timestamp - terminal_start_time) < cfg['terminal_feedback_time']

                            #print(show_terminal)

                        #print('show terminal loop ended...')
                        #print((current_timestamp - terminal_start_time) < cfg['terminal_feedback_time'])

                        #while ((core.getTime() - timer) > cfg['terminal_feedback_time']):
                        #    myCircle.draw()
                        #    if (cfg['poll_type'] == 'psychopy'):
                        #        timeArray.append(core.getTime() - myTime)
                        #        mouseposXArray.append(myMouse.getPos()[0])
                        #        mouseposYArray.append(myMouse.getPos()[1] + startPos[1])
                        #    elif (cfg['poll_type'] == 'x11'):
                        #        timeArray.append(myMouse.Pos()[2] - myTime)
                        #        mouseposXArray.append(myMouse.Pos()[0])
                        #        mouseposYArray.append(myMouse.Pos()[1] + startPos[1])
                        #    cursorposXArray.append(rotated_X)
                        #    cursorposYArray.append(rotated_Y + startPos[1])
                        #    #print('one flip statement') #### ??????????
                        #    myWin.flip()

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
                    mouseposXArray.append(current_pos[0]) #- (cfg['screen_on']*(cfg['screen_dimensions'][0]/2)))
                    mouseposYArray.append(current_pos[1]*cfg['flipscreen'] - startPos[1])
                    cursorposXArray.append(circle_pos[0])
                    cursorposYArray.append(circle_pos[1]*cfg['flipscreen'] - startPos[1])
            #print('another flip statement?')
            myWin.flip()
    ################################ PHASE 3 #####################################
        # phase 3 is getting back to the home position
            if (phase_1 == True and phase_2 == True):

#                if ((cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True) or (cfg['trial_type'] == 'error_clamp')) and get_dist(circle_pos, startPos) <= get_dist(startPos,endPos)/2):
#                    show_arrow = True
#                    show_arrowFill = True
#
#                if ((cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True) or (cfg['trial_type'] == 'error_clamp')) and get_dist(circle_pos, startPos) > get_dist(startPos, endPos)/2):
#                    show_arrow = False
#                    show_arrowFill = False
                if ((cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True) or (cfg['trial_type'] == 'error_clamp')) and get_dist(circle_pos, end_point) >= get_dist(startPos,endPos)/10):
                    # where is the angle for the arrow calculated?
                    # why isn't the arrow drawn now?
                    # everything regarding the arrow could be done in this if statement, right?
                    show_arrow = True
                    show_arrowFill = True

                if ((cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True) or (cfg['trial_type'] == 'error_clamp')) and get_dist(circle_pos, startPos) > 3*get_dist(startPos, endPos)/20):
                    show_cursor = False
                if ((cfg['trial_type'] == 'no_cursor' or (cfg['trial_type'] == 'cursor' and cfg['terminal_feedback'] == True) or (cfg['trial_type'] == 'error_clamp')) and get_dist(circle_pos, startPos) <= 3*get_dist(startPos, endPos)/20):
                    show_cursor = True
                if (cfg['trial_type'] == 'cursor'  and get_dist(circle_pos, startPos) < dist_criterion and velocity < 35 and cfg['terminal_feedback'] == False):
                    timePos_dict['task_num'] = cfg['task_num']
                    timePos_dict['task_name'] = cfg['task_name']
                    timePos_dict['trial_num'] = cfg['trial_num']
                    timePos_dict['trial_type'] = cfg['trial_type']
                    timePos_dict['targetangle_deg'] = cfg['target_angle']
                    timePos_dict['rotation_angle'] = rot_dir*cfg['current_rotation_angle']
                    timePos_dict['homex_px'] = startPos[0]
                    timePos_dict['homey_px'] = startPos[1]*cfg['flipscreen'] - startPos[1]
                    timePos_dict['targetx_px'] = endPos[0]
                    timePos_dict['targety_px'] = endPos[1]*cfg['flipscreen'] - startPos[1]
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
                        # back at the home? no not yet... record data, and return it? why not just save it here instead of throwing around all that data from one function to another?
                        timePos_dict['task_num'] = cfg['task_num']
                        timePos_dict['task_name'] = cfg['task_name']
                        timePos_dict['trial_num'] = cfg['trial_num']
                        timePos_dict['trial_type'] = cfg['trial_type']
                        timePos_dict['targetangle_deg'] = cfg['target_angle']
                        timePos_dict['rotation_angle'] = rot_dir*cfg['current_rotation_angle']
                        timePos_dict['homex_px'] = startPos[0]
                        #print('start and end position should already be relative to home position, and stay that way?')
                        timePos_dict['homey_px'] = startPos[1]*cfg['flipscreen'] - startPos[1] #+ cfg['active_height']/2
                        timePos_dict['targetx_px'] = endPos[0]
                        timePos_dict['targety_px'] = endPos[1]*cfg['flipscreen'] - startPos[1] #+ cfg['active_height']/2
                        timePos_dict['time_s'] = timeArray
                        timePos_dict['mousex_px'] = mouseposXArray
                        timePos_dict['mousey_px'] = mouseposYArray
                        timePos_dict['cursorx_px'] = cursorposXArray
                        timePos_dict['cursory_px'] = cursorposYArray
                        timePos_dict['terminalfeedback_bool'] = cfg['terminal_feedback']
                        timePos_dict['targetdistance_percmax'] = int(cfg['target_distance_ratio']*100)

                        return timePos_dict
        except:
            pass # what went wrong if an exception occurred? why are we catching it? what should we do as backup?

def generate_rotation_list(initial, final, trials):
    rotation_list = ndarray.tolist(((((1.0*final)-(1.0*initial))/trials)*arange(trials)) + initial)
    return rotation_list

############################# RUN EXPERIMENT V2 ###############################
def run_experiment_2(fulls, participant, experiment = {}):
    end_exp = DataFrame({})
    task_save = DataFrame({})
    running = deepcopy(experiment['experiment']) # why copy this? set up a window, a mouse object and add those, plus a task-index to your cfg, then simply loop through the tasks, and throw that to a run-task function?
    settings = deepcopy(experiment['settings']) # same here...
#    participant_state = deepcopy(experiment['participant'][participant]['state'])
    cfg = {}
    #### Generate seed ####
    participant_seed = participant + settings['experiment_folder'] # where is this used? seeding the random-number generator *once* is sufficient, and cleaner

    #print experiment['settings']['waitblanking']
    #print 'this should reflect the setting of the wait-blanking option...'


    # the next if/else and two try/except statements should be combined in one function: 'createWorkspace' or something...
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
                     name='MousePosition', # why is it called that?
                     color=(-1, -1, -1),
                     units='pix',
                     screen=experiment['settings']['screen'],
                     viewScale=view_scale,
                     waitBlanking=experiment['settings']['waitblanking'])
#        Win._setCurrent()

        # I would have expected a line like this:
        # cfg['win'] = Window(...) with the cfg being the only location to have the Window object
        # is this Window object created for nothing? It doesn't seem to be stored anywhere? Delete?
        cfg['win'] = Win
    except:
        print "Exception creating Window"

    print 'created window'

    # now set up the mouse object?

    cfg['psyMouse'] = event.Mouse(visible = False, newPos = None, win = cfg['win'])

    # try:
    #     class myMouse:
    #         Xlib = CDLL("libX11.so.6")
    #         display = Xlib.XOpenDisplay(None)
    #         if display == 0: sys.exit(2)
    #         w = Xlib.XRootWindow(display, c_int(0))
    #         (root_id, child_id) = (c_uint32(), c_uint32())
    #         (root_x, root_y, win_x, win_y) = (c_int(), c_int(), c_int(), c_int())
    #         mask = c_uint()
    #
    #         width = cfg['main_screen_dimensions'][0]
    #         height = cfg['main_screen_dimensions'][1]
    #
    #         x_offset = cfg['main_screen_offset'][0]
    #         y_offset = cfg['main_screen_offset'][1]
    #
    #         def Pos(self):
    #             ret = self.Xlib.XQueryPointer(self.display, c_uint32(self.w), byref(self.root_id), byref(self.child_id), byref(self.root_x), byref(self.root_y), byref(self.win_x), byref(self.win_y), byref(self.mask))
    #             if ret == 0: sys.exit(1)
    #             return [self.root_x.value - (self.width/2) - self.x_offset, -1 * (self.root_y.value - (self.height/2) - self.y_offset), time()] # c_int can't be used for regular Python math, their values are ints - and we return the current time
    # except:
    #     # create an identically named object with identical behavior based on PsychoPy?
    #     print ('not using xLib')
        # 
        # class myMouse:
        #
        #     def Pos(self):
        #         #print('PsychoPy mouse')
        #         [X,Y] = cfg['psyMouse'].getPos()
        #         return [X,Y,time()]


    class myMouse:
        def Pos(self):
            #print('PsychoPy mouse')
            [X,Y] = cfg['psyMouse'].getPos()
            return [X,Y,time()]

    cfg['mouse'] = myMouse()

    print 'added mouse object'

    ### Configure visual feedback settings here
    # it would also make sense to put this in a function, so that it's a separate unit
    # I'd also put the creation of image stim objects for the icons in a separate function as well
    try:
        #print('creating two arrows?')
        # is this black arrow used?
        arrowFillVert = [(-1 , 1), (-1, -1),(-0.5, 0)]
        arrowFill = ShapeStim(win=Win,
                                     vertices=arrowFillVert,
                                     fillColor=[-1,-1,-1],
                                     size=cfg['circle_radius']*0.6,
                                     lineColor=[-1,-1,-1])
        # or this gray one? Can we remove one?
        arrowVert = [(-1, 1),(-1,-1),(1.2,0)]
        arrow = ShapeStim(win=Win,
                                 vertices=arrowVert,
                                 fillColor=[0, 0, 0],
                                 size=cfg['circle_radius']*0.6,
                                 lineColor=[0,0,0])

        # there is no 'else' following this... don't we need to do something else?
        if settings['custom_stim_enable'] == True:
            # shouldn't this be in a separate function?
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
                    # what I would do if either the target or cursor can't be handled is:
                    # 1) remove that pair from the set of possible icon-stimuli
                    # 2) after trying all pairs: print a warning to command line that 'some' icons could not be used, removing
                    # 3) run the experiment with only the stimuli that worked
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
        # the following bits of code should never be used anymore... but the experiment doesn't work if I comment them out...
        # from here ... (to: 'to here')

        #print('using obsolete custom cursor/target/home settings?')
        if settings['custom_cursor_enable'] == False: # we only use 'custom_stim_enable'
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
                                    #                    print(cursor_angle) radius=cfg['circle_radius'],
                                     edges=32,
                                     units='pix',
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])
        if settings['custom_home_enable'] == False: # we only use 'custom_stim_enable'
            startCircle = Circle(win=Win,
                                        radius=cfg['circle_radius'],
                                        lineWidth=2,
                                        edges=32,
                                        units='pix',
                                        fillColor=[-1, -1, -1],
                                        lineColor=[0, 0, 0],
                                        pos=cfg['home_pos']) # done
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
                                        lineColor=[0, 0, 0],
                                        pos=cfg['home_pos']) # done
        if settings['custom_target_enable'] == False: # we only use 'custom_stim_enable'
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
        #Mouse = event.Mouse(win=Win, visible=False) # this mouse object should NEVER be used, we should add an object to the cfg before we even get here
        screen_info_monitors = screeninfo.get_monitors() # this info should only be used when setting up the workspace... not here

        # to here

    except Exception as e: # end of "configuring all visual feedback"

        print e
        print str(e)

    print 'created stimulus objects'
    ################ loop through tasks

    for i in range (0, len(running)): # loop through all tasks and copy all setting to new objects? even for experiment-wide settings? why...
        # instead of using 'running[i]['flip_text'] we could just use 'experiment['settings']['flipscreen']' right?
        # and since 'running[i]['flipscreen'] is always 1, it seems not to be useful...
        if experiment['settings']['flipscreen'] == True:
            running[i]['flipscreen'] = 1
            running[i]['flip_text'] = True
        else:
            running[i]['flipscreen'] = 1
            running[i]['flip_text'] = False

        # this should not be done for every task, but ONCE for the whole experiment
        #try:
        #    running[i]['x11_mouse'] = myMouse()
        #except:
        #    running[i]['poll_type'] = 'psychopy' # this is always set to psychopy!
        running[i]['mouse'] = cfg['mouse']

        if settings['custom_stim_enable'] == True:
            running[i]['custom_stim'] = custom_stim_holder


        # whyyyy?
        # this info seems to be useless for any purpose?
        if (len(screen_info_monitors) > 1 and settings['screen'] == 1):
            running[i]['screen_on'] = 1
            running[i]['screen_dimensions'] = cfg['main_screen_dimensions']
        elif (len(screen_info_monitors) > 1 and settings['screen'] == 0):
            running[i]['screen_on'] = -1
            running[i]['screen_dimensions'] = cfg['main_screen_dimensions']
        else:
            running[i]['screen_on'] = 0
            running[i]['screen_dimensions'] = cfg['screen_dimensions']

        # all of this can be solved by using a cfg object that has a task-counter or task-index, that is equal to the i that you use here in this loop...
        running[i]['custom_stim_enable'] = settings['custom_stim_enable']
        running[i]['return_movement'] = experiment['settings']['return_movement']
        running[i]['cursor_circle'] = myCircle
        running[i]['test_circle'] = testCircle
        running[i]['start_circle'] = startCircle
        running[i]['end_circle'] = endCircle
        #print('always using psychopy mouse object?')
        #running[i]['mouse'] = Mouse # this should come from the cfg object, and not be created many times over, also: it will now always be the psychopy mouse object, never the X11 one...
        # also, it's already been set (maybe by Marius)
        #print('making another copy of the Window object?')
        running[i]['win'] = cfg['win'] # copying the window object this way may be the cause of window-closing problems... even if there is just 1 task, you might end up having 2 window objects
        # all those non-reference copies of the Window object should be destroyed explicitly... can be solved by not creating the "running" dictionary, but just passing "cfg" along, as instructed/expected
        # saves memory and code as well
        running[i]['circle_radius'] = cfg['circle_radius']
        running[i]['arrow_stim'] = arrow
        running[i]['arrowFill_stim'] = arrowFill
        #print('storing task_num even when creating a config for separate tasks?')
        running[i]['task_num'] = i + 1
        running[i]['max_distance'] = cfg['active_height']     # why calculate these two at all?
        running[i]['min_distance'] = cfg['active_height']/2   # it will always be 1 normalized screen unit * the target distance set by the experimenter
        running[i]['active_height'] = cfg['active_height']    # and this will also be given in the cfg as the normalized screen unit...
        running[i]['starting_pos'] = cfg['home_pos'] #(0, (-cfg['active_height']/2)*running[i]['flipscreen'])

        running[i]['current_rotation_angle'] = 0
        if running[i]['rotation_change_type'] == 'gradual':
            rotation = generate_rotation_list(running[i]['rotation_angle'], running[i]['final_rotation_angle'], running[i]['num_trials'])
        if running[i]['num_targets'] > 1:
            targetList = angle_split(running[i]['min_angle'], running[i]['max_angle'], running[i]['num_targets'])
        elif running[i]['num_targets'] == 1:
            targetList = [running[i]['min_angle']]


        #### FIRST SEED FOR TARGET ANGLES ####
        #print('seeding random number generator?')
        setParticipantSeed(participant_seed + str(i)) # this should not be done every task or trial, just once per experiment/participant, otherwise stuff is not reproducible

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
#                if (running[i]['rotatipos=cfg['home_pos']on_change_type'] == 'gradual' and running[i]['current_rotation_angle'] != running[i]['rotation_angle'] and trial_num > 0):
#                    running[i]['current_rotation_angle'] = running[i]['current_rotation_angle'] + running[i]['rotation_direction']
#                if (running[i]['rotation_change_type'] == 'gradual' and running[i]['current_rotation_angle'] == running[i]['rotation_angle'] and trial_num > 0):
#                    running[i]['current_rotation_angle'] = running[i]['rotation_angle']

                # deciding the rotation angle this way sounds like a lot of work, in order to store it in a way that is hard to retrieve later on?
                if (running[i]['rotation_change_type'] == 'gradual'):
                    running[i]['current_rotation_angle'] = rotation[trial_num]
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
                exp = trial_runner(running[i]) # but this runs a whole task, not a single trial, right? since we are going from the experiment runner straight to task... is the function misnamed or is the code not organized?

#                except:
#                    print "Exception in running trial_runner function"
                if exp == 'escaped':
                    running[i]['win'].close()
#                    experiment['participant'][participant]['angles'] = targetList
#                    experiment['participant'][participant]['state'] = [i, trial_num]
                    return DataFrame({})
                else:
                    # is this where the data is saved?
                    # would make more sense to me to do that in the trial function, as it is the trial data that is being stored?
                    df_exp = DataFrame(exp, columns=['task_num','task_name', 'trial_type', 'trial_num', 'terminalfeedback_bool','rotation_angle','targetangle_deg','targetdistance_percmax','homex_px','homey_px','targetx_px','targety_px', 'time_s', 'mousex_px', 'mousey_px', 'cursorx_px', 'cursory_px'])
                    df_exp.to_csv(path_or_buf = path.join("data", settings['experiment_folder'], participant, running[i]['task_name'] + "_" + str(trial_num) + ".csv"), index=False)
                    task_save = concat([task_save, df_exp])
                    end_exp = concat([end_exp, df_exp])
#                    experiment['participant'][participant]['angles'] = targetList
#                    experiment['participant'][participant]['state'] = [i, trial_num]
#                    targetList.remove(chosen_target)


                    with open(path.join("experiments", settings['experiment_folder'] + ".json"), "wb") as f:
                        # the experiment settings are stored after every trial?
                        dump(experiment, f)
                        f.close()
        elif (running[i]['trial_type'] == 'pause'):
            running[i]['time'] = core.getTime()
            exp = trial_runner(running[i])
            # why not run a pause task function now?

#        if (running[i]['trial_type'] != 'pause'):
#            task_save.to_csv(path_or_buf = path.join("data", settings['experiment_folder'], participant, running[i]['task_name'] + "_Complete" + ".csv"), index=False)
        task_save = DataFrame({})
    running[i]['win'].close()
    return end_exp



def get_participant_state(participant, experiment = {}):
    tasks_uncut = experiment['experiment']
#    tasks = []
#    num_pause = 0
#    for task in tasks_uncut:
#        if task['trial_type'] != 'pause':running[i]['win'] = Win # copying the window object this way may be the cause of window-closing problems...
#            tasks.append(task)
    for task_num, task in enumerate(tasks_uncut):
        if task['trial_type'] != 'pause':
            for trialnum in range(0, task['num_trials']):
                f_path = path.join("data", experiment['settings']['experiment_folder'], participant, task['task_name'] + "_" + str(trialnum) + ".csv")
                file_check = path.exists(f_path)
                if file_check:
                    continue
                else:
                    return [task_num, trialnum]
        else:
            continue
    return [len(tasks_uncut), tasks_uncut[-1]['num_trials']]



def concat_full(participant, experiment = {}):
    tasks_uncut = experiment['experiment']
    tasks = []
    #### CUT PAUSE TASKS ####
    for task in tasks_uncut:
        if task['trial_type'] != 'pause':
            tasks.append(task)
    directory_list = []
    for task_num, task in enumerate(tasks):
        for i in range(0, task['num_trials']):
            f_path = path.join("data", experiment['settings']['experiment_folder'], participant, task['task_name'] + "_" + str(i) + ".csv")
            directory_list.append(f_path)
    fields = []
    full_data = []
    for idx_data, data in enumerate(directory_list):
        with open(data, "rb") as csvfile:
            rows = []
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                rows.append(row)
            if idx_data == 0:
                fields = rows[0]
            del rows[0]
            full_data.extend(rows)
    full_data_path = path.join("data", experiment['settings']['experiment_folder'], participant, participant + "_COMPLETE.csv")
    with open(full_data_path, "wb") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(full_data)


def continue_experiment(fulls, participant, experiment = {}):
    end_exp = DataFrame({})
    task_save = DataFrame({})
    running = deepcopy(experiment['experiment'])
    settings = deepcopy(experiment['settings'])
    participant_state = get_participant_state(participant, experiment)

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
                     viewScale=view_scale,
                     waitBlanking=experiment['settings']['waitblanking'])
        cfg['win'] = Win
    except:
        print "Exception creating Window"


    # add mouse object... why is the whole setup of the environment not simply the same, regardless of whether this is a new or continued run?


    cfg['psyMouse'] = event.Mouse(visible = False, newPos = None, win = cfg['win'])

    try:
        class myMouse:
            Xlib = CDLL("libX11.so.6")
            display = Xlib.XOpenDisplay(None)
            if display == 0: sys.exit(2)
            w = Xlib.XRootWindow(display, c_int(0))
            (root_id, child_id) = (c_uint32(), c_uint32())
            (root_x, root_y, win_x, win_y) = (c_int(), c_int(), c_int(), c_int())
            mask = c_uint()

            width = cfg['main_screen_dimensions'][0]
            height = cfg['main_screen_dimensions'][1]

            x_offset = cfg['main_screen_offset'][0]
            y_offset = cfg['main_screen_offset'][1]

            def Pos(self):
                ret = self.Xlib.XQueryPointer(self.display, c_uint32(self.w), byref(self.root_id), byref(self.child_id), byref(self.root_x), byref(self.root_y), byref(self.win_x), byref(self.win_y), byref(self.mask))
                if ret == 0: sys.exit(1)
                return [self.root_x.value - (self.width/2) - self.x_offset, -1 * (self.root_y.value - (self.height/2) - self.y_offset), time()] # c_int can't be used for regular Python math, their values are ints - and we return the current time
    except:
        # create an identically named object with identical behavior based on PsychoPy?
        print ('not using xLib')

        class myMouse:

            def Pos(self):
                #print('PsychoPy mouse')
                [X,Y] = cfg['psyMouse'].getPos()
                return [X,Y,time()]

    cfg['mouse'] = myMouse()



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
        print i
        if experiment['settings']['flipscreen'] == True:
            running[i]['flipscreen'] = 1
            running[i]['flip_text'] = True
        else:
            running[i]['flipscreen'] = 1
            running[i]['flip_text'] = False
        #try:
        #    running[i]['x11_mouse'] = myMouse()
        #except:
        #    running[i]['poll_type'] = 'psychopy'
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
        running[i]['mouse'] = cfg['mouse'] # DO WE HAVE THIS RIGHT HERE? now we do...
        running[i]['win'] = Win
        running[i]['circle_radius'] = cfg['circle_radius']
        running[i]['arrow_stim'] = arrow
        running[i]['arrowFill_stim'] = arrowFill
        running[i]['task_num'] = i + 1
        running[i]['max_distance'] = cfg['active_height']
        running[i]['min_distance'] = cfg['active_height']/2
        running[i]['active_height'] = cfg['active_height']
        running[i]['starting_pos'] = (0, (-cfg['active_height']/2)*running[i]['flipscreen'])
        if running[i]['rotation_change_type'] == 'gradual':
            rotation = generate_rotation_list(running[i]['rotation_angle'], running[i]['final_rotation_angle'], running[i]['num_trials'])
#        running[i]['current_rotation_angle'] = participant_state[1]
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
#                if (running[i]['rotation_change_type'] == 'gradual' and running[i]['current_rotation_angle'] != running[i]['rotation_angle'] and trial_num > 0):
#                    running[i]['current_rotation_angle'] = running[i]['current_rotation_angle'] + 1
#                elif (running[i]['rotation_change_type'] == 'gradual' and running[i]['current_rotation_angle'] == running[i]['rotation_angle'] and trial_num > 0):
#                    running[i]['current_rotation_angle'] = running[i]['rotation_angle']
                if (running[i]['rotation_change_type'] == 'gradual'):
                    running[i]['current_rotation_angle'] = rotation[trial_num]
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
#                    experiment['participant'][participant]['angles'] = targetList
#                    experiment['participant'][participant]['state'] = [i, trial_num]
                    return end_exp
                else:
                    df_exp = DataFrame(exp, columns=['task_num','task_name', 'trial_type', 'trial_num', 'terminalfeedback_bool','rotation_angle','targetangle_deg','targetdistance_percmax','homex_px','homey_px','targetx_px','targety_px', 'time_s', 'mousex_px', 'mousey_px', 'cursorx_px', 'cursory_px'])
                    df_exp.to_csv(path_or_buf = path.join("data", settings['experiment_folder'], participant, running[i]['task_name'] + "_" + str(trial_num) + ".csv"), index=False)
                    end_exp = concat([end_exp, df_exp])
#                    experiment['participant'][participant]['angles'] = targetList
#                    experiment['participant'][participant]['state'] = [i, trial_num]
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
#def continue_experiment_2(fulls, participant, experiment = {}, state = []):
#    end_exp = DataFrame({})
#    task_save = DataFrame({})
#    running = deepcopy(experiment['experiment'])
#    settings = deepcopy(experiment['settings'])
#    participant_state = deepcopy(experiment['participant'][participant]['state'])
#    cfg = {}
#    #### Generate seed ####
#    participant_seed = (sum([ord(c) for c in settings['experiment_folder']]) + (sum([ord(c) for c in participant]) * 9999))
#    if experiment['settings']['flipscreen'] == True:
#        view_scale = [1, -1]
#    else:
#        view_scale = [1, 1]
#    try:
#        addWorkSpaceLimits(experiment['settings']['screen'], cfg)
#    except:
#        print "Exception adding workspace limits"
#    try:
#        Win = Window(cfg['screen_dimensions'],
#                     winType=cfg['winType'],
#                     colorSpace='rgb',
#                     fullscr=fulls,
#                     name='MousePosition',
#                     color=(-1, -1, -1),
#                     units='pix',
#                     screen=experiment['settings']['screen'],
#                     viewScale=view_scale)
##        Win._setCurrent()
#    except:
#        print "Exception creating Window"
#    ### Configure visual feedback settings here
#    try:
#        arrowFillVert = [(-1 , 1), (-1, -1),(-0.5, 0)]
#        arrowFill = ShapeStim(win=Win,
#                                     vertices=arrowFillVert,
#                                     fillColor=[-1,-1,-1],
#                                     size=cfg['circle_radius']*0.6,
#                                     lineColor=[-1,-1,-1])
#        arrowVert = [(-1, 1),(-1,-1),(1.2,0)]
#        arrow = ShapeStim(win=Win,
#                                 vertices=arrowVert,
#                                 fillColor=[0, 0, 0],
#                                 size=cfg['circle_radius']*0.6,
#                                 lineColor=[0,0,0])
#        if settings['custom_stim_enable'] == True:
#            custom_stim_holder = []
#            icon_directory = listdir(settings['custom_stim_file'])
#            for i in range(1, len(icon_directory)/2 + 1):
#                try:
#                    custom_target = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2.5, image=(path.join(settings['custom_stim_file'], 'target_' + str(i) + '.png')))
#                except:
#                    custom_target = Circle(win=Win,
#                                     radius=cfg['circle_radius'],
#                                     edges=32,
#                                     units='pix',
#                                     fillColor=[0, 0, 0],
#                                     lineColor=[0, 0, 0])
#                try:
#                    custom_cursor = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2.5, image=(path.join(settings['custom_stim_file'], 'cursor_' + str(i) + '.png')))
#                except:
#                    custom_cursor = Circle(win=Win,
#                                     radius=cfg['circle_radius'],
#                                     edges=32,
#                                     units='pix',
#                                     fillColor=[0, 0, 0],
#                                     lineColor=[0, 0, 0])
#
#                custom_stim_holder.append([custom_cursor, custom_target])
#        if settings['custom_cursor_enable'] == False:
#            myCircle = Circle(win=Win,
#                                     radius=cfg['circle_radius'],
#                                     edges=32,
#                                     units='pix',
#                                     fillColor=[0, 0, 0],
#                                     lineColor=[0, 0, 0])
#            testCircle = Circle(win=Win,
#                                     radius=cfg['circle_radius'],
#                                     edges=32,
#                                     units='pix',
#                                     fillColor=[-1, 0, 1],
#                                     lineColor=[0, 0, 0])
#        else:
#            try:
#                myCircle = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2, image=settings['custom_cursor_file'])
#            except:
#                myCircle = Circle(win=Win,
#                                     radius=cfg['circle_radius'],
#                                     edges=32,
#                                     units='pix',
#                                     fillColor=[0, 0, 0],
#                                     lineColor=[0, 0, 0])
#        if settings['custom_home_enable'] == False:
#            startCircle = Circle(win=Win,
#                                        radius=cfg['circle_radius'],
#                                        lineWidth=2,
#                                        edges=32,
#                                        units='pix',
#                                        fillColor=[-1, -1, -1],
#                                         lineColor=[0, 0, 0])
#        else:
#            try:
#                startCircle = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2, image=settings['custom_home_file'])
#            except:
#                startCircle = Circle(win=Win,
#                                        radius=cfg['circle_radius'],
#                                        lineWidth=2,
#                                        edges=32,
#                                        units='pix',
#                                        fillColor=[-1, -1, -1],
#                                         lineColor=[0, 0, 0])
#        if settings['custom_target_enable'] == False:
#            endCircle = Circle(win=Win,
#                                      radius=cfg['circle_radius'],
#                                      lineWidth=2,
#                                      edges=32,
#                                      units='pix',
#                                      fillColor=[-1, -1, -1],
#                                      lineColor=[0, 0, 0])
#        else:
#            try:
#                endCircle = ImageStim(win=Win, units='pix', size=cfg['circle_radius']*2, image=settings['custom_target_file'])
#            except:
#                endCircle = Circle(win=Win,
#                                      radius=cfg['circle_radius'],
#                                      lineWidth=2,
#                                      edges=32,
#                                      units='pix',
#                                      fillColor=[-1, -1, -1],
#                                      lineColor=[0, 0, 0])
#        Mouse = event.Mouse(win=Win, visible=False)
#        screen_info_monitors = screeninfo.get_monitors()
##        pyautogui.moveTo(10, 10)
#    except Exception as e:
#        print e
#        print str(e)
#    for i in range (0, len(running)):
#        if experiment['settings']['flipscreen'] == True:
#            running[i]['flipscreen'] = 1
#            running[i]['flip_text'] = True
#        else:
#            running[i]['flipscreen'] = 1
#            running[i]['flip_text'] = False
#        try:
#            running[i]['x11_mouse'] = myMouse()
#        except:
#            running[i]['poll_type'] = 'psychopy'
#        if settings['custom_stim_enable'] == True:
#            running[i]['custom_stim'] = custom_stim_holder
#        if (len(screen_info_monitors) > 1 and settings['screen'] == 1):
#            running[i]['screen_on'] = 1
#            running[i]['screen_dimensions'] = cfg['main_screen_dimensions']
#        elif (len(screen_info_monitors) > 1 and settings['screen'] == 0):
#            running[i]['screen_on'] = -1
#            running[i]['screen_dimensions'] = cfg['main_screen_dimensions']
#        else:
#            running[i]['screen_on'] = 0
#            running[i]['screen_dimensions'] = cfg['screen_dimensions']
#        running[i]['custom_stim_enable'] = settings['custom_stim_enable']
#        running[i]['return_movement'] = experiment['settings']['return_movement']
#        running[i]['cursor_circle'] = myCircle
#        running[i]['test_circle'] = testCircle
#        running[i]['start_circle'] = startCircle
#        running[i]['end_circle'] = endCircle
#        running[i]['mouse'] = Mouse
#        running[i]['win'] = Win
#        running[i]['circle_radius'] = cfg['circle_radius']
#        running[i]['arrow_stim'] = arrow
#        running[i]['arrowFill_stim'] = arrowFill
#        running[i]['task_num'] = i + 1
#        running[i]['max_distance'] = cfg['active_height']
#        running[i]['min_distance'] = cfg['active_height']/2
#        running[i]['active_height'] = cfg['active_height']
#        running[i]['starting_pos'] = (0, (-cfg['active_height']/2)*running[i]['flipscreen'])
#        running[i]['current_rotation_angle'] = 0
#        if running[i]['num_targets'] > 1:
#            targetList = angle_split(running[i]['min_angle'], running[i]['max_angle'], running[i]['num_targets'])
#        elif running[i]['num_targets'] == 1:
#            targetList = [running[i]['min_angle']]
#        fulltargetList = tuple(targetList)
#        #### FIRST SEED FOR TARGET ANGLES ####
#        seed(participant_seed)
#        shuffle(targetList)
#        if (running[i]['trial_type'] != 'pause'):
##            if running[i]['num_targets'] > 1:
##                targetList = angle_split(running[i]['min_angle'], running[i]['max_angle'], running[i]['num_targets'])
##            elif running[i]['num_targets'] == 1:
##                targetList = [running[i]['min_angle']]
#            for trial_num in range (0, int(running[i]['num_trials'])):
#                running[i]['trial_num'] = trial_num + 1
#                if (len(targetList) == 0):
#                    targetList = list(fulltargetList)
#                if (running[i]['rotation_change_type'] == 'gradual' and running[i]['current_rotation_angle'] != running[i]['rotation_angle'] and trial_num > 0):
#                    running[i]['current_rotation_angle'] = running[i]['current_rotation_angle'] + 1
#                if (running[i]['rotation_change_type'] == 'gradual' and running[i]['current_rotation_angle'] == running[i]['rotation_angle'] and trial_num > 0):
#                    running[i]['current_rotation_angle'] = running[i]['rotation_angle']
#                elif (running[i]['rotation_change_type'] == 'abrupt'):
#                    running[i]['current_rotation_angle'] = running[i]['rotation_angle']
##                print running[i]['rotation_change_type'], running[i]['current_rotation_angle'], running[i]['rotation_angle'], 'trial_num: ', trial_num, running[i]['num_trials']
#                try:
#                    chosen_target = targetList[trial_num%len(targetList)]
#                except:
#                    print "Exception randomizing target"
#                running[i]['target_angle'] = chosen_target
#
#                running[i]['target_distance'] = int(running[i]['max_distance']*running[i]['target_distance_ratio'])
#                running[i]['time'] = core.getTime()
##                try:
#                exp = trial_runner(running[i])
#
##                except:
##                    print "Exception in running trial_runner function"
#                if exp == 'escaped':
#                    running[i]['win'].close()
#                    return DataFrame({})
#                else:
#                    df_exp = DataFrame(exp, columns=['task_num','task_name', 'trial_type', 'trial_num', 'terminalfeedback_bool','rotation_angle','targetangle_deg','targetdistance_percmax','homex_px','homey_px','targetx_px','targety_px', 'time_s', 'mousex_px', 'mousey_px', 'cursorx_px', 'cursory_px'])
#                    df_exp.to_csv(path_or_buf = path.join("data", settings['experiment_folder'], participant, running[i]['task_name'] + "_" + str(trial_num) + ".csv"), index=False)
#                    task_save = concat([task_save, df_exp])
#                    end_exp = concat([end_exp, df_exp])
#                    experiment['participant'][participant]['angles'] = targetList
#                    experiment['participant'][participant]['state'] = [i, trial_num]
##                    targetList.remove(chosen_target)
#                    with open(path.join("experiments", settings['experiment_folder'] + ".json"), "wb") as f:
#                        dump(experiment, f)
#                        f.close()
#        elif (running[i]['trial_type'] == 'pause'):
#            running[i]['time'] = core.getTime()
#            exp = trial_runner(running[i])
#        if (running[i]['trial_type'] != 'pause'):
#            task_save.to_csv(path_or_buf = path.join("data", settings['experiment_folder'], participant, running[i]['task_name'] + "_Complete" + ".csv"), index=False)
#        task_save = DataFrame({})
#    running[i]['win'].close()
#    return end_exp
