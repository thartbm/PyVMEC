# functions that prepare data for analysis by students
# add later, triggered by a button in the GUI, which shows a pop-up with options for pre-processing the data
################# Gather data names ##################
import csv
import Exp as exp
from math import degrees
from os import path
from json import load
from numpy import array, float, mean, unique, delete, std, nan, ma, nanmean, nanstd
from copy import deepcopy
#with open ("/home/julius/Desktop/PyVMEC/experiments/preprocessing.json", "rb") as f:
#    exp_test = load(f)
#plist = ['me-mi', 'JULIUS_1', 'marius_a', 'm2', 'JULIUS_2', 'FOUR me']
#tlist = ['aligned','rotated','reversal','errorclamps']
#cfg_test = {"dependent_variable": "cursor error", "trial":True, "block":True, "target":True, "output_style":"single file", "outliers": True, "outlier_scale": 2}
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
            task_name = task_list[i]
            for j in range(0, experiment['experiment'][i]['num_trials']):
                data_list_task.append(path.join("data", experiment['settings']['experiment_folder'], participant_list[h], task_name + "_" + str(j) + ".csv"))
            data_list_participant.append(data_list_task)
        data_list.append(data_list_participant)
    return data_list
#p_list = ["finished", "unfinished"]
#t_list = ['first', 'second']
#data_dir = data_name_list(p_list, t_list, exp_test)
#print data_dir
#process_cfg = {"include_trial": True}

def data_process(participant_list = [], data_dir = [], cfg = {}):
    output_fields = ['task', 'trial','rotation_angle_deg', 'target_angle_deg']
    output_rows = []
    for i in range (0, len(data_dir)):   
        output_fields.append(participant_list[i])
        pc = 0
        for j in range (0, len(data_dir[i])):           
            for k in range (0, len(data_dir[i][j])):
#                fields = []
                rows = []
                input_row = []
                with open(data_dir[i][j][k], "rb") as csvfile:
                    csv_reader = csv.reader(csvfile)
#                    fields = csv_reader.next()
#                    print ("\nField names are:" + ','.join(field for field in fields))
                    for row in csv_reader:
                        rows.append(row)
                for row in rows[1:]:
                    if i == 0:
                        if float(exp.get_dist([0,0], [float(row[15:16][0]), float(row[16:17][0])]))/float(exp.get_dist([0,0], [float(row[11:12][0]), float(row[12:13][0])])) >= float(1)/float(3):
                            input_row.append(row[1:2][0])
                            input_row.append(row[3:4][0])
                            input_row.append(row[5:6][0])
                            input_row.append(row[6:7][0])
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
    return [output_fields, output_rows]
#test_directory_list = data_name_list(plist, tlist, exp_test)
#print test_directory_list


def process_participants(participant_list = [], task_list = [], experiment = {}, cfg = {}):
    directory_matrix = data_name_list(participant_list, task_list, experiment)
    participant_matrix = []
    output_matrix = []
    field_matrix = []
    fields_trial = ['task', 'trial','rotation_angle_deg']
    fields_block = ['task', 'block','rotation_angle_deg']
    fields_target = ['task', 'target','rotation_angle_deg']
    dependent_variable = 0
    ############ CREATE PARTICIPANT MATRIX ###############
    for participant in (directory_matrix):
        dv_participant = []
        for task in participant:
            dv_task = []
            for trial in task:
                rows = []
                dv_trial = []
                with open(trial, "rb") as csvfile:
                    csv_reader = csv.reader(csvfile)
                    for row in csv_reader:
                        rows.append(row)
                del(rows[0])
                for idx in rows:
                    if exp.get_dist([0,0], [float(idx[15]), float(idx[16])])/exp.get_dist([0,0],[float(idx[10]), float(idx[11])]) >= (float(1)/float(3)):
                        cursor_error = degrees(exp.cart2pol([float(idx[15]), float(idx[16])])[1]) - float(idx[6])
                        reach_deviation = degrees(exp.cart2pol([float(idx[13]), float(idx[14])])[1]) - float(idx[6])
                        if cfg['dependent_variable'] == 'cursor error':
                            dependent_variable = cursor_error
                        elif cfg['dependent_variable'] == 'reach deviation':
                            dependent_variable = reach_deviation
                        dv_trial.extend([idx[1], idx[3], idx[5], idx[6], dependent_variable])
                        break
                dv_task.append(dv_trial)
            dv_participant.extend(dv_task)
        participant_matrix.append(deepcopy(dv_participant))
    ############ PARTICIPANT MATRIX CREATED ################
    
    ############ REMOVE OUTLIERS ###################
    if cfg['outliers'] == True:
        participant_matrix_tmp = []
        for participant in participant_matrix:
            jump_to = 0
            participant_array = array(participant)
            for task in task_list:
                task_index = (array(participant)[:,0] == task).nonzero()[0]
                task_array = (array(participant)[:,4][task_index])
                task_mean = mean(task_array.astype(float))
                task_std = std(task_array.astype(float))
#                print task_mean, task_std, task_array
#                outlier_index = array((task_array.astype(float) > (task_mean + cfg['outlier_scale'] * task_std)) | (task_array.astype(float) < (task_mean - cfg['outlier_scale'] * task_std))).nonzero()[0] + jump_to
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
            data_matrix = array(data)[:,[0,1,2,4]].tolist()
        else:
            dv_column = []
            for row in data:
                dv_column.append(row[4])
            for idx_1, row in enumerate(data_matrix):
                data_matrix[idx_1].append(dv_column[idx_1])
    output_matrix.append(deepcopy(data_matrix))
    
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
                block_mean = nanmean(array(participant_data)[:,4][block_index[block]].astype(float))
                block_row.extend([task, block, rotation_angle, block_mean])             
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
    output_matrix.append(deepcopy(data_matrix))
    
    
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
                target_mean = nanmean(array(participant_data)[:,4][target_index].astype(float))
                target_row.extend([task, target, rotation_angle, target_mean])
                task_row_target.append(target_row)
            jump_value = jump_value + len(task_index)
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
    output_matrix.append(data_matrix)
    ##### OUTPUT MATRIX FORM ###############################################
    #[participants by trial, participants by block, participants by target]#
    ########################################################################self.participant_list
    field_matrix.append(fields_trial)
    field_matrix.append(fields_block)
    field_matrix.append(fields_target)
    return field_matrix, output_matrix