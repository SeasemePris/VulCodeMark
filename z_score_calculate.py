import os
import pandas as pd
import numpy
from collections import Counter, defaultdict
import re
import math
from get_file_stat import *


def calculate_z_score(syn_2_doc, syn_2_doc_target, target_num, total_num):
    assert len(syn_2_doc.keys()) >= len(syn_2_doc_target.keys())
    syn_z_score = defaultdict(float)

    p_0 = target_num / total_num
    for element in syn_2_doc_target.keys():
        p_hat = syn_2_doc_target[element] / syn_2_doc[element]
        z_score = (p_hat - p_0) / math.sqrt(p_0 * (1 - p_0) / syn_2_doc[element])
        syn_z_score[element] = z_score

    return syn_z_score


def get_vital_syn_elem(syn_z_score, K):
    converted_z_score_dict = sorted(syn_z_score.items(), key=lambda x: x[1], reverse=True)
    sorted_z_score_dict = dict(converted_z_score_dict)
    candi_vital_syn_elem = list(sorted_z_score_dict.keys())[:K]

    return candi_vital_syn_elem


def get_idx_4_vital_syn_elem(candi_vital_syn_elem, all_file_list):
    # Build a dictioanry of candidate syntactic elements -> idx

    vital_syn_elem_idx_list = []

    for file in all_file_list:
        syn_elem_idx = defaultdict(list)
        all_syn_ele = file['attribute'][0].split(';')
        for i, v in enumerate(all_syn_ele):
            if v in candi_vital_syn_elem:
                syn_elem_idx[v].append(i)
        vital_syn_elem_idx_list.append(syn_elem_idx)

    return vital_syn_elem_idx_list


def get_sem_pair(all_file_list):
    sem_pair_list = []

    for file in all_file_list:
        pair_dict = defaultdict(list)

        if "nextToken" in file.keys():
            nodes = file['nextToken'][0].split(',')
            for i in range(len(nodes) - 1):
                pair = (int(nodes[i]), int(nodes[i + 1]))
                pair_dict['nextToken'].append(pair)

        if "computeFrom" in file.keys():
            for pair in file['computeFrom']:
                pair_elem = pair.split(',')
                new_pair = (int(pair_elem[0]), int(pair_elem[1]))
                pair_dict['computeFrom'].append(new_pair)

        if "guardedBy" in file.keys():
            for pair in file["guardedBy"]:
                pair_elem = pair.split(',')
                gb_new_pair = (int(pair_elem[0]), int(pair_elem[1]))
                pair_dict["guardedBy"].append(gb_new_pair)

        if "guardedByNegation" in file.keys():
            for pair in file["guardedByNegation"]:
                pair_elem = pair.split(',')
                gbn_new_pair = (int(pair_elem[0]), int(pair_elem[1]))
                pair_dict["guardedByNegation"].append(gbn_new_pair)

        if "lastLexicalUse" in file.keys():
            for pair in file["lastLexicalUse"]:
                pair_elem = pair.split(',')
                llu_new_pair = (int(pair_elem[0]), int(pair_elem[1]))
                pair_dict["lastLexicalUse"].append(llu_new_pair)

        if "jump" in file.keys():
            for pair in file["jump"]:
                pair_elem = pair.split(',')
                jp_new_pair = (int(pair_elem[0]), int(pair_elem[1]))
                pair_dict["jump"].append(jp_new_pair)

        sem_pair_list.append(pair_dict)

    return sem_pair_list

def get_syn_element_idx_dict(all_file_list):
    # get the syntactic element types for each idx

    idx_dict_list = []

    for file in all_file_list:
        idx_syn_type = defaultdict(str)
        all_syn_ele = file['attribute'][0].split(';')
        for i, v in enumerate(all_syn_ele):
            idx_syn_type[i] = v

        idx_dict_list.append(idx_syn_type)

    return idx_dict_list


def get_all_pairs(all_file_list):
    all_pairs = []  # record all the father-child relations in AST into a list, "father":[child-1, child-2,...]

    for file in all_file_list:
        pairs_list = defaultdict(list)
        for pair in file['children']:
            pair_elem = pair.split(',')
            father = int(pair_elem[0])
            child = int(pair_elem[1])
            pairs_list[father].append(child)
        all_pairs.append(pairs_list)

    return all_pairs


def judge_pair_sem_list(sem_pair_sublist, pair):
    sem_in_list = []  # if the pair matches the semantic relations, store the relation in the list

    for key in sem_pair_sublist.keys():
        if pair in sem_pair_sublist[key]:
            sem_in_list.append(key)
        else:
            continue

    return sem_in_list


def weighted_score_calculation(vital_syn_elem_idx_list, all_pairs, sem_pair_list, idx_dict_list,
                               syn_z_score, sem_z_score):
    all_subgra_scores = []
    all_sub_ast_nodes = []
    valid_idx = []

    for i, vital_syn_dict in enumerate(vital_syn_elem_idx_list):  # each file (for)

        nodes = []
        file_sub_graph_z_score = []

        if len(vital_syn_dict) != 0:  # if the file containing the vital syntactic elements
            for key in vital_syn_dict.keys():

                for elem in vital_syn_dict[key]:  # the father node; # each subgraph starts with one vital node

                    father = []
                    child = []
                    ast_nodes = []

                    syn_score = []
                    sem_score = []

                    depth_count = 1
                    father.append(elem)

                    children = all_relations[i][elem]
                    if len(children) != 0:
                        child.append(children)
                    else:
                        continue

                    while depth_count <= 3:
                        for j, fath in enumerate(father):
                            # print("The father is {}".format(fath))
                            if len(child[j]) <= 3 and len(
                                    child[j]) != 0:  # guarantee that the width of subgraph is less than 3
                                current_pairs = [(fath, son) for son in child[j]]
                            else:
                                continue
                            for pair in current_pairs:
                                relations_list = judge_pair_sem_list(all_sems[i], pair)
                                if len(relations_list) != 0:
                                    sem_z_scores = [sem_z_score_dict[relation] for relation in relations_list]
                                    sem_score.extend(sem_z_scores)
                                else:
                                    sem_score.append(0.0)
                            father_syn = idx_2_syn[i][fath]
                            father_syn_z_score = z_score_dict[father_syn]
                            syn_score.append(father_syn_z_score)
                            # print(syn_score)
                            children_syn = [idx_2_syn[i][son] for son in child[j]]
                            children_syn_z_score = [z_score_dict[syn_ele] for syn_ele in children_syn]
                            syn_score.extend(children_syn_z_score)
                            # print(syn_score)
                            # print(current_pairs)
                            # print(child)
                            ast_nodes.extend(current_pairs)
                            # print(ast_nodes)

                        father.clear()
                        for kid_list in child:
                            father.extend(kid_list)

                        child.clear()
                        for fath in father:
                            children = all_relations[i][fath]
                            child.append(children)
                        depth_count += 1
                        # print(depth_count)

                    nodes.append(ast_nodes)
                    sub_graph_z_score_for_now = 0.4 * sum(syn_score) + 0.6 * sum(sem_score)
                    file_sub_graph_z_score.append(sub_graph_z_score_for_now)
            valid_idx.append(i)
        else:
            continue

        all_subgra_scores.append(file_sub_graph_z_score)
        all_sub_ast_nodes.append(nodes)

    return all_subgra_scores, all_sub_ast_nodes, valid_idx