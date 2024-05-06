import os
import pandas as pd
import numpy
from collections import Counter, defaultdict
import re
import math


def read_file_to_dict(file):
    with open(file, 'r') as file:
        lines = file.readlines()
        d_dict = defaultdict(list)
        keys = []
        for line in lines:
            line = line.replace("\n", "")
            if line.startswith("-----") and line.endswith("-----"):
                pat = r'-----(.*?)-----'
                key = re.findall(pat, line)[0]
                if len(key) != 0:
                    keys.append(key)
                else:
                    key = "node"
                    keys.append(key)
            else:
                key = keys[-1]
                d_dict[key].append(line)

    return d_dict


def get_csv_from_folder(folder_path):
    all_files = []
    files = os.listdir(folder_path)
    for file in files:
        if not os.path.isdir(file):
            file_path = folder_path + "/" + file
            file_dict = read_file_to_dict(file_path)
            all_files.append(file_dict)

    return all_files


def get_syn_elem_stat(all_file_list, target):
    syn_2_doc = defaultdict(int)
    syn_2_doc_target = defaultdict(int)
    target_num = 0
    total_num = 0

    for file in all_file_list:
        label = file['label'][0]
        syn_ele = set(file['attribute'][0].split(';'))
        for element in syn_ele:
            if len(element) == 0:
                continue
            elif label == target:
                syn_2_doc_target[element] += 1
                syn_2_doc[element] += 1
            else:
                syn_2_doc[element] += 1

        if label == target:
            target_num += 1
            total_num += 1
        else:
            total_num += 1

    return syn_2_doc, syn_2_doc_target, target_num, total_num


def get_sem_elem_stat(all_file_list, target):
    sem_2_doc = defaultdict(int)
    sem_2_doc_target = defaultdict(int)
    target_num = 0
    total_num = 0
    flag = False

    for file in all_file_list:
        label = file['label'][0]
        if label == target:
            target_num += 1
            total_num += 1
            flag = True
        else:
            total_num += 1
            flag = False

        if "nextToken" in file.keys():
            sem_2_doc["nextToken"] += 1
            if flag:
                sem_2_doc_target["nextToken"] += 1

        if "computeFrom" in file.keys():
            sem_2_doc["computeFrom"] += 1
            if flag:
                sem_2_doc_target["computeFrom"] += 1

        if "guardedBy" in file.keys():
            sem_2_doc["guardedBy"] += 1
            if flag:
                sem_2_doc_target["guardedBy"] += 1

        if "guardedByNegation" in file.keys():
            sem_2_doc["guardedByNegation"] += 1
            if flag:
                sem_2_doc_target["guardedByNegation"] += 1

        if "lastLexicalUse" in file.keys():
            sem_2_doc["lastLexicalUse"] += 1
            if flag:
                sem_2_doc_target["lastLexicalUse"] += 1

        if "jump" in file.keys():
            sem_2_doc["jump"] += 1
            if flag:
                sem_2_doc_target["jump"] += 1

    return sem_2_doc, sem_2_doc_target, target_num, total_num


