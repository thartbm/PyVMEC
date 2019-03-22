# functions that prepare data for analysis by students
# add later, triggered by a button in the GUI, which shows a pop-up with options for pre-processing the data
################# Gather data names ##################
import csv
import Exp as exp
from math import degrees
from os import path
from json import load
from numpy import array, float, mean, unique, delete, std, nan, ma, nanmean, nanstd, warnings, pi, dot, NaN, where, cos, sin, sqrt, arctan2
from copy import deepcopy
from pandas import read_csv
#with open ("/home/julius/Desktop/PyVMEC/experiments/preprocessing.json", "rb") as f:
#    exp_test = load(f)
#plist = ['me-mi', 'JULIUS_1', 'marius_a', 'm2', 'JULIUS_2', 'FOUR me']
#tlist = ['aligned','rotated','reversal','errorclamps']
#cfg_test = {"dependent_variable": "cursor error", "trial":True, "block":True, "target":True, "output_style":"single file", "outliers": True, "outlier_scale": 2}

def rotateTrajectory(X,Y,angle_deg):
    
    # create rotation matrix to rotate the X,Y coordinates
    th = (angle_deg/180.) * pi
    R  = array([[cos(th),-sin(th)],[sin(th),cos(th)]])
    
    # put coordinates in a matrix as well
    coords = array([X,Y])
    
    # rotate the coordinates
    Rcoords = dot(R,coords)
    
    # return the rotated reach
    return Rcoords


def getTrialReachAngleAt(trialdf,dv):
    
    # location (string) determines where the angle of thereach is determines, it is one of:
    # maxvel: maximum velocity (default)
    # endpoint: end of the reach
    # cmX: the last sample before this distance from home, where X is replaced by a numeral
    # ptX: percentage distance to target, where X is a numeral (0-100)
    
    # return a matrix of two numbers:
    # reachangle = matrix(data=NA,nrow=1,ncol=2)
    
    angle = trialdf['targetangle_deg'][0]
    if (dv == 'cursor error'):
        X = trialdf['cursorx_px'] #- trialdf['homex_px'][0]
        Y = trialdf['cursory_px'] #- trialdf['homey_px'][0]
    
    if (dv == 'reach deviation'):
        X = trialdf['mousex_px'] #- trialdf['homex_px'][0]
        Y = trialdf['mousey_px'] #- trialdf['homey_px'][0]
    
    #print([trialdf['homex_px'][0], trialdf['homey_px'][0]]) # home position is NOT STORED correctly... for no-cursor and error-clamp trials
    #dist = sqrt(X**2 + Y**2)
    #print(dist)
    # rotate the trajectory
    # (this avoids problems in the output of atan2 for large angles)
    trajectory = rotateTrajectory(X,Y,-1*angle)
    X = trajectory[0,:]
    Y = trajectory[1,:]
    
    # cutoff at 1/3 from home to target in whatever unit is used
    distance = sqrt(trialdf['targetx_px'][0]**2 + trialdf['targety_px'][0]**2)/3.
    print(distance)
    #print([arctan2(trialdf['targety_px'][0], trialdf['targetx_px'][0])/pi*180, angle])
    
    # get the distance from home:
    dist = sqrt(X**2 + Y**2)
    print(dist)
    ## if there are no selected samples above 3 cm: return NAs
    #if (length(where(dist > distance)) == 0):
    #    return NaN
    #print(where(dist > distance)[0][0])
    # find the first sample, where dist > X
    rown = where(dist > distance)[0][0]
    print([rown,X[rown],Y[rown],(arctan2(Y[rown],X[rown])/pi)*180])
    # calculate the angle at that point for the rotated trajectory
    # this is the angular deviation we are looking for
    return (arctan2(Y[rown],X[rown])/pi)*180



def blocksizer(num_targets):
    if num_targets == 1:
        return 3
    if num_targets == 2:
        return 4
    else:
        return num_targets


def num_blocks(blocksize, task, exp = {}):
    experiment = exp['experiment']
    for i in range(0, len(experiment)):
        if experiment[i]['task_name'] == task:
            num_trials = experiment[i]['num_trials']
            break
    return num_trials/blocksize

def task_to_numtarg(task, exp = {}):
    experiment = exp['experiment']
    for i in range(0, len(experiment)):
        if experiment[i]['task_name'] == task:
            return experiment[i]['num_targets']
            
def task_to_blocksize(task, exp = {}):
    return blocksizer(task_to_numtarg(task, exp))
    
def data_name_list(participant_list = [], task_list = [], experiment = {}):
    data_list_participant = []
    data_list_task = []
    data_list = []
    for h in range(0, len(participant_list)):
        data_list_participant = []
        for i in range(0, len(experiment['experiment'])):
            data_list_task = []
            if experiment['experiment'][i]['task_name'] in task_list:
                task_name = experiment['experiment'][i]['task_name']
                for j in range(0, experiment['experiment'][i]['num_trials']):
                    data_list_task.append(path.join("data", experiment['settings']['experiment_folder'], participant_list[h], task_name + "_" + str(j) + ".csv"))
            data_list_participant.append(data_list_task)
        data_list.append(data_list_participant)
    return data_list

def check_data_exists(data_list = []):
    for participant in data_list:
        for task in participant:
            for trial in task:
                if path.exists(trial):
                    continue
                else:
                    print trial     
    return
    
def check_for_incomplete_data(data_list=[]):
    for idx_particpant, participant in enumerate(data_list):
        for idx_task, task in enumerate(participant):
            for idx_trial, trial in enumerate(task):
                with open(trial, "rb") as csvfile:
                    csv_reader = csv.reader(csvfile)
                    row_count = sum(1 for row in csv_reader)
                    if row_count < 5:
                        return trial
                    else:
                        continue
    return True

def data_process(participant_list = [], data_dir = [], cfg = {}):
    
    output_fields = ['task', 'trial','rotation_angle_deg', 'target_angle_deg']
    output_rows = []
    for i in range (0, len(data_dir)):   # does this loop over participants?
        output_fields.append(participant_list[i]) # seems like it does
        pc = 0
        for j in range (0, len(data_dir[i])): # does this loop over files in the data directory?          
            for k in range (0, len(data_dir[i][j])):
#                fields = []
                rows = []
                input_row = []
                with open(data_dir[i][j][k], "rb") as csvfile:
                    csv_reader = csv.reader(csvfile) # why not read in the COMPLETE file as a pandas data frame?
#                    fields = csv_reader.next()
#                    print ("\nField names are:" + ','.join(field for field in fields))
                    for row in csv_reader:
                        rows.append(row)
                for row in rows[1:]:
                    if i == 0:
                        if float(exp.get_dist([0,0], [float(row[15:16][0]), float(row[16:17][0])]))/float(exp.get_dist([0,0], [float(row[11:12][0]), float(row[12:13][0])])) >= float(1)/float(3): # why use column indices instead of column names? names are more robust to future situations where we add or re-order columns
                            input_row.append(row[1:2][0]) # task?
                            input_row.append(row[3:4][0]) # trial?
                            input_row.append(row[5:6][0]) # rotation_angle_deg?
                            input_row.append(row[6:7][0]) # target_angle_deg?
                            cursor_deviation = degrees(exp.cart2pol([float(row[15:16][0]), float(row[16:17][0])])[1]) - float(row[6:7][0])
                            input_row.append(cursor_deviation)
                            break
                    if i > 0:
                        if float(exp.get_dist([0,0], [float(row[15:16][0]), float(row[16:17][0])]))/float(exp.get_dist([0,0], [float(row[11:12][0]), float(row[12:13][0])])) >= float(1)/float(3):
                            cursor_deviation = degrees(exp.cart2pol([float(row[15:16][0]), float(row[16:17][0])])[1]) - float(row[6:7][0])
                            output_rows[pc].append(cursor_deviation)
                            pc = pc + 1
                            break
                if i == 0:
                    output_rows.append(input_row)
    return [output_fields, output_rows] # why not return a data frame where this is integrated?
#test_directory_list = data_name_list(plist, tlist, exp_test)
#print test_directory_list


# so the pre-processing functionality can't run on it's own... I thought the GUI for that would be included here too
# but this function is getting it's input from somewhere else

# I'd expected this function to only need the experiment name... but the user can select participants and tasks so that makes no sense

def process_participants(participant_list = [], task_list = [], experiment = {}, cfg = {}):
    warnings.filterwarnings('ignore')
    directory_matrix = data_name_list(participant_list, task_list, experiment)
    #print(directory_matrix)
#    check_data_exists(directory_matrix)

    # don't we only allow participants that have complete data?
    # how does the participant list in the pre-processing GUI get populated?
    data_check = check_for_incomplete_data(directory_matrix)
    if data_check == True:
        pass
    else:
        return data_check
    
    # this should all be one data frame? and not a bunch of nested lists...
    participant_matrix = []
    output_matrix = []
    field_matrix = []
    fields_trial = ['task', 'task_type', 'trial','rotation_angle_deg']
    # we create the block and target data frames from the original... if requested
    # I really don't understand why this has to be so complicated
    fields_block = ['task','task_type', 'block',]
    fields_target = ['task','task_type', 'target']
    dependent_variable = 0 # is this used?
    ############ CREATE PARTICIPANT MATRIX ###############
    for participant in (directory_matrix):
        dv_participant = []
        for task in participant:
            dv_task = []
            for trial in task:
                rows = []
                dv_trial = []
                # trial is now actually the relative path to the file...
                trialdf = read_csv(trial)
                
                #with open(trial, "rb") as csvfile:
                #    csv_reader = csv.reader(csvfile)
                #    for row in csv_reader:
                #        rows.append(row)
                #del(rows[0]) # why not use the column header?
                #for idx in rows:
                #    if idx[5] == "":
                #        idx[5] = "0"
                #    if exp.get_dist([0,0], [float(idx[15]), float(idx[16])])/exp.get_dist([0,0],[float(idx[10]), float(idx[11])]) >= (float(1)/float(3)): # this is calculated for every row? 
                                                                                                                                                          # is this guaranteed to always work?
                #        if cfg['dependent_variable'] == 'cursor error':
                #            dependent_variable = degrees(exp.cart2pol([float(idx[15]), float(idx[16])])[1]) - float(idx[6]) # can this get us weird values?
                #        elif cfg['dependent_variable'] == 'reach deviation':
                #            dependent_variable = degrees(exp.cart2pol([float(idx[13]), float(idx[14])])[1]) - float(idx[6])
                #        print(dependent_variable)
                dependent_variable = getTrialReachAngleAt(trialdf,cfg['dependent_variable'])
                dv_trial.extend([trialdf['task_name'][0], trialdf['trial_num'][0], trialdf['rotation_angle'][0], trialdf['targetangle_deg'][0], '%.2f'%(float(dependent_variable)), trialdf['trial_type'][0]])
                dv_task.append(dv_trial)
            dv_participant.extend(dv_task)
        participant_matrix.append(deepcopy(dv_participant))
    
    #print(participant_matrix)
    ############ PARTICIPANT MATRIX CREATED ################
    
    ############ REMOVE OUTLIERS###################
    ############ RO: BY WINDOW #####################
#    if cfg['outliers'] == True:
    if cfg['outliers_win'] == True:
        participant_matrix_tmp_win = []
        for participant in participant_matrix:
            participant_rows_tmp = []
            for row in participant:
                if cfg['dependent_variable'] == 'cursor error':
                    if int(row[2]) >= 0:
                        if (float(row[4]) > ((cfg['window_limit']/2) + float(row[2]))) | (float(row[4]) < ((-cfg['window_limit']/2))):
#                            print "upper bound: " + str((cfg['window_limit']/2) + float(row[2])), "lower bound: " + str((-cfg['window_limit']/2)), "dep_var: " + row[4]
                            row[4] = nan
                    elif int(row[2]) < 0:
                        if (float(row[4]) > ((cfg['window_limit']/2))) | (float(row[4]) < ((-cfg['window_limit']/2) + float(row[2]))):
#                            print "upper bound: " + str(((cfg['window_limit']/2))), "lower bound: " + str(((-cfg['window_limit']/2) + float(row[2]))), "dep_var: " + row[4]
                            row[4] = nan
                elif cfg['dependent_variable'] == 'reach deviation':
                    if int(row[2]) >= 0:
                        if (float(row[4]) > ((cfg['window_limit']/2) )) | (float(row[4]) < ((-cfg['window_limit']/2) - float(row[2]))):
#                            print "upper bound: " + str(((cfg['window_limit']/2))), "lower bound: " + str(((-cfg['window_limit']/2) - float(row[2]))), "dep_var: " + row[4]
                            row[4] = nan
                    elif int(row[2]) < 0:
                        if (float(row[4]) > ((cfg['window_limit']/2) - float(row[2]))) | (float(row[4]) < ((-cfg['window_limit']/2))):
#                            print "upper bound: " + str(((cfg['window_limit']/2) - float(row[2]))), "lower bound: " + str(((-cfg['window_limit']/2))), "dep_var: " + row[4]
                            row[4] = nan
                participant_rows_tmp.append(row)
            participant_matrix_tmp_win.append(participant_rows_tmp)
#                print row
                
#            participant_array = array(participant)
#            window_idx = ((participant_array[:,4].astype(float) > (cfg['window_limit']/2)) | (participant_array[:,4].astype(float) < (-cfg['window_limit']/2))).nonzero()[0]
#            participant_array[:,4][window_idx] = nan
#            participant_matrix_tmp_win.append(participant_array.tolist())
        participant_matrix = participant_matrix_tmp_win


    ############ RO: BY STANDARD DEVIATION ################
    if cfg['outliers'] == True:
        participant_matrix_tmp = []
        for participant in participant_matrix:
            jump_to = 0
            participant_array = array(participant)
            for task in task_list:
                task_index = (array(participant)[:,0] == task).nonzero()[0]
                task_array = (array(participant)[:,4][task_index])
                task_mean = nanmean(task_array.astype(float))
                task_std = nanstd(task_array.astype(float), ddof=1)
                outlier_index = ((task_array.astype(float) > (task_mean + cfg['outlier_scale']*task_std)) | (task_array.astype(float) < (task_mean - cfg['outlier_scale']*task_std))).nonzero()[0] + jump_to
                participant_array[:,4][outlier_index] = nan
                jump_to = jump_to + len(task_index)
            participant_matrix_tmp.append(participant_array.tolist())
        participant_matrix = participant_matrix_tmp
        
        
    ############ OUTPUT BY TRIALS ##################
    data_matrix = []
    for idx_0, data in enumerate(participant_matrix):
        fields_trial.append(participant_list[idx_0])
        if idx_0 == 0:
            data_matrix = array(data)[:,[0,5,1,2,4]].tolist()
        else:
            dv_column = []
            for row in data:
                dv_column.append(row[4])
            for idx_1, row in enumerate(data_matrix):
                data_matrix[idx_1].append(dv_column[idx_1])
    ############ Standard Deviation & Average In Participants #################
    tmp_data = []
    fields_trial.extend(["average", "sd"])
    for row in array(data_matrix):
        participant_average = nanmean(row[4:].astype(float))
        participant_std = nanstd(row[4:].astype(float), ddof=1)
        row = row.tolist()
        row.append('%.2f'%(float(participant_average)))
        row.append('%.2f'%(float(participant_std)))
        tmp_data.append(row)
    output_matrix.append(deepcopy(tmp_data))
    
    ############ OUTPUT BY BLOCKS ##################
            ##### USING PARTICIPANT MATRIX TO PRODUCE BLOCK DATA #########
    data_matrix = []
    participant_matrix_blocked = []
    for participant_data in participant_matrix:
        task_matrix_blocked = []
        for task in task_list:
            task_row = []
            task_index = (array(participant_data)[:, 0] == task).nonzero()[0]
            blocksize = task_to_blocksize(task, experiment)
            block_index = [task_index[x: x + blocksize] for x in xrange(0, len(task_index), blocksize)]
            for block in range(0, num_blocks(blocksize, task, experiment)):
                block_row = []
                rotation_angle = array(participant_data)[:,2][block_index[block]][0]
                task_type = array(participant_data)[:,5][block_index[block]][0]
                block_mean = nanmean(array(participant_data)[:,4][block_index[block]].astype(float))
                block_row.extend([task, task_type, block + 1, '%.2f'%(float(block_mean))])   
                task_row.append(block_row)
            task_matrix_blocked.extend(task_row)
        participant_matrix_blocked.append(deepcopy(task_matrix_blocked))
            ##### CONCATENATE BLOCKED MATRIX ################
    for idx_0, data in enumerate(participant_matrix_blocked):
        fields_block.append(participant_list[idx_0])
        if idx_0 == 0:
            data_matrix = data
        else:
            dv_column = []
            for row in data:
                dv_column.append(row[3])
            for idx_1, row in enumerate(data_matrix):
                data_matrix[idx_1].append(dv_column[idx_1])
    ############ Standard Deviation & Average In Participants #################
    tmp_data = [] # this will be outputted but in 'output_matrix'
    fields_block.extend(["average", "sd"]) # this only adds column names to a list of strings
    for row in array(data_matrix):
        participant_average = nanmean(row[3:].astype(float))
        participant_std = nanstd(row[3:].astype(float), ddof=1)
        row = row.tolist()
        row.append('%.2f'%(float(participant_average)))
        row.append('%.2f'%(float(participant_std)))
        tmp_data.append(row)
    output_matrix.append(deepcopy(tmp_data))
    
    
    ############ OUTPUT BY TARGET #################
    participant_matrix_target = []
    data_matrix = []
    for participant_data in participant_matrix:
        task_matrix_target = []
        jump_value = 0
        for task in task_list:
            task_row_target = []
            task_index = (array(participant_data)[:, 0] == task).nonzero()[0]
#            print task_index
            target_list = unique(array(participant_data)[task_index][:,3])
            for target in target_list:
                target_row = []
                target_index = (array(participant_data)[task_index][:,3] == target).nonzero()[0]
                target_index = target_index + jump_value
#                print target_index
                rotation_angle = array(participant_data)[target_index][:,2][0]
                task_type = array(participant_data)[target_index][:,5][0]
                target_mean = nanmean(array(participant_data)[:,4][target_index].astype(float))
                target_row.extend([task, task_type, target, '%.2f'%(float(target_mean))])
                task_row_target.append(target_row)
            jump_value = jump_value + len(task_index)
            ##### ORDER TARGETS SMALLEST TO GREATEST ANGLE ######
            target_order = []
            for task in task_row_target:
                target_order.append(int(task[2]))
            st_idx = []
            for target in sorted(target_order):
                st_idx.append(target_order.index(target))
            task_row_target_array = array(task_row_target)
            task_row_target_array[:] = task_row_target_array[st_idx]
            task_row_target = task_row_target_array.tolist()
            ##### ADD TO END OF LIST ######
            task_matrix_target.extend(task_row_target)
        participant_matrix_target.append(task_matrix_target)
        
        ##### CONCATENATE TARGET MATRIX ################
    for idx_0, data in enumerate(participant_matrix_target):
        fields_target.append(participant_list[idx_0])
        if idx_0 == 0:
            data_matrix = data
        else:
            dv_column = []
            for row in data:
                dv_column.append(row[3])
            for idx_1, row in enumerate(data_matrix):
                data_matrix[idx_1].append(dv_column[idx_1])
    ############ Standard Deviation & Average In Participants #################
    tmp_data = []
    fields_target.extend(["average", "sd"])
    for row in array(data_matrix):
        participant_average = nanmean(row[4:].astype(float))
        participant_std = nanstd(row[4:].astype(float), ddof=1)
        row = row.tolist()
        row.append('%.2f'%(float(participant_average)))
        row.append('%.2f'%(float(participant_std)))
        tmp_data.append(row)
    output_matrix.append(deepcopy(tmp_data))
    
    ##### OUTPUT MATRIX FORM ###############################################
    #[participants by trial, participants by block, participants by target]#
    ########################################################################self.participant_list
    field_matrix.append(fields_trial)
    field_matrix.append(fields_block)
    field_matrix.append(fields_target)
    return field_matrix, output_matrix, participant_matrix
