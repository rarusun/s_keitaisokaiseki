import queue
import math
import time
import os
import pickle

class Node():
    def __init__(self, surface, length, cost, left_node_num, position, not_in_dict, pos_num, information):
        self.min_cost = math.inf
        self.surface = surface
        self.length = length
        self.cost = cost
        self.left_node_num = left_node_num
        self.position = position
        self.not_in_dict = not_in_dict
        self.pos_num = pos_num
        self.information = information

class Lattice():
    def __init__(self, sentence, id_dict, matrix_dict):
        self.sentence = sentence
        self.sentence_length = len(sentence)
        
        self.nodes = []
        self.end_nodes = {}
        self.end_nodes[0] = [0]
        self.nodes.append(Node('<BOS>', 0, 0, None, 0, False, 0, '<BOS>'))
        self.begin_nodes = {}
        self.begin_nodes[self.sentence_length] = [1]
        self.nodes.append(Node('<EOS>', 0, 0, None, 1, False, 0, '<EOS>'))

        self.id_dict = id_dict
        self.cost_manager = CostManager(id_dict, matrix_dict)


    def insert(self, begin, end, not_in_dict):
        word = self.sentence[begin:end]

        if word in self.id_dict.keys():
            dict_num = len(self.id_dict[word])
        else:
            dict_num = 1
        
        for num in range(dict_num):
            if(not_in_dict):
                node = Node(word, end-begin, None, None, len(self.nodes), not_in_dict, num, word)
            else:
                node = Node(word, end-begin, None, None, len(self.nodes), not_in_dict, num, self.id_dict[word][num][-1])
            self.nodes.append(node)

            if begin in self.begin_nodes.keys():
                self.begin_nodes[begin].append(node.position)
            else:
                self.begin_nodes[begin] = [node.position]
            
            if end in self.end_nodes.keys():
                self.end_nodes[end].append(node.position)
            else:
                self.end_nodes[end] = [node.position]

    def viterbi(self):
        #forward
        for i in range(0, self.sentence_length+1):
            for r_i, r_node_num in enumerate(self.begin_nodes[i]):
                r_node = self.nodes[r_node_num]
                r_word = r_node.surface
                self.nodes[r_node_num].cost = math.inf
                for l_i, l_node_num in enumerate(self.end_nodes[i]):
                    l_node = self.nodes[l_node_num]
                    cost = l_node.cost + self.cost_manager.get_transition_cost(l_node, r_node) + self.cost_manager.get_emission_cost(r_node)
                    if(cost < self.nodes[r_node_num].cost):
                        self.nodes[r_node_num].cost = cost
                        self.nodes[r_node_num].left_node_num = l_node_num 
        #backward
        results = []
        bn_l = self.sentence_length
        bn_i = 0
        node_num = self.begin_nodes[bn_l][bn_i]
        while True:
            node = self.nodes[node_num]
            results.append(node.information)
            node_num = node.left_node_num
            if(node.surface == '<BOS>'):
                break
        results.reverse()
        return results


class CostManager():
    def __init__(self, id_dict, matrix_dict):
        self.matrix_dict = matrix_dict
        self.id_dict = id_dict

    def get_emission_cost(self, node):
        if node.not_in_dict:
            return 100000
        elif node.length == 0:
            cost = 0
        else:
            cost = self.id_dict[node.surface][node.pos_num][2]
        return cost

    def get_transition_cost(self, lnode, rnode):
        if lnode.not_in_dict:
            return 100000
        elif lnode.length == 0:
            lid = 0
        else:
            lid = self.id_dict[lnode.surface][lnode.pos_num][0]
            
        if rnode.not_in_dict:
            return 100000
        elif rnode.length == 0:
            rid = 0
        else:
            rid = self.id_dict[rnode.surface][rnode.pos_num][0]
        return self.matrix_dict[lid][rid]

