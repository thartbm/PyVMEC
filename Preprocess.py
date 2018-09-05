# functions that prepare data for analysis by students
# add later, triggered by a button in the GUI, which shows a pop-up with options for pre-processing the data
################# Gather data names ##################
import csv
import Exp as exp
from math import degrees
from os import path
from json import load
#with open ("/home/julius/Desktop/PyVMEC/experiments/Test.json", "rb") as f:
#    exp_test = load(f)
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

def data_process(participant_list = [], data_dir = []):
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
#data = data_process(p_list, data_dir, process_cfg)
#file_name = "processed_data.csv"
#with open(file_name, "wb") as csvfile:
#    csvwriter = csv.writer(csvfile)
#    csvwriter.writerow(data[0])
#    csvwriter.writerows(data[1])
test_cfg = {'block':True, 'angle':True}
def data_process_2(data = [], cfg = {}, experiment = {}):
    fields_b = ['task', 'block']
    fields_a = ['task', 'target_angle_deg']
    fields_t = ['task', 'trial']