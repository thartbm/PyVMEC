# functions that prepare data for analysis by students
# add later, triggered by a button in the GUI, which shows a pop-up with options for pre-processing the data
################# Gather data names ##################
import csv
from os import path
from json import load
with open ("/home/julius/Desktop/PyVMEC/experiments/Test.json", "rb") as f:
    exp_test = load(f)
def data_name_list(participant_list = [], experiment = {}):
    data_list_participant = []
    data_list_task = []
    data_list = []
    for h in range(0, len(participant_list)):
        data_list_participant = []
        for i in range(0, len(experiment['experiment'])):
            data_list_task = []
            task_name = experiment['experiment'][i]['task_name']
            for j in range(0, experiment['experiment'][i]['num_trials']):
                data_list_task.append(path.join("data", experiment['settings']['experiment_folder'], participant_list[h], task_name + "_" + str(j) + ".csv"))
            data_list_participant.append(data_list_task)
        data_list.append(data_list_participant)
    return data_list
data_dir = data_name_list(["finished", "unfinished"], exp_test)
print data_dir
process_cfg = {"include_trial": True}

def data_process(participant_list = [], data_dir = [], cfg = {}):
    fields = []
    fields.append()
    for i in range (0, len(data_dir)):       
        for j in range (0, len(data_dir[i])):
            for k in range (0, len(data_dir[j][k])):
            with open(data_dir[i][j][k], "rb") as csvfile:
                csv_reader = csv.reader(csvfile)
                
            
            
    