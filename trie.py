import queue
import math
import time
import os
import pickle

class MySubDictionary():
    def __init__(self, prefix, suffixes):
        self.prefix = prefix
        self.suffixes = []
        for suffix in suffixes:
            if(len(suffix) == 0):
                self.suffixes.append('#')
            else:
                self.suffixes.append(suffix)

    def append(self, suffix):
        if(len(suffix) == 0):
            self.suffixes.append('#')
        else:
            self.suffixes.append(suffix)
    
class Trie():
    def __init__(self, lower_bound, upper_bound, vocabulary, vocab_dictionary):
        self.vocabulary= vocabulary
        self.sub_dictionaries = {}
        self.base = {}
        self.check = {}
        self.c2id = {'':0}

    def update_slot_start(self, check, slot_start):
        position = slot_start
        while True:
            if position in check:
                position += 1
            else:
                break
        return position

    def get_candidate_for_base(self, candidate_for_base, pre_indexed_chars):
        while True:
            acceptable = True
            use_index = []
            if candidate_for_base in self.check.keys():
                acceptable = False
            else: 
                for char in pre_indexed_chars:
                    if char not in self.c2id.keys():
                        self.c2id[char] = len(self.c2id)
                    char_id = self.c2id[char]
                    #if(candidate_for_base + char_id - self.origin) in self.check.keys():
                    if(candidate_for_base + char_id) in self.check.keys():
                        acceptable = False
                        break
            if(acceptable):
                break
            candidate_for_base += 1
        return candidate_for_base
    
    def add_suffixes(self, candidate_for_base, sub_dictionary, node):
        indexed_chars = set()    
        for suffix in sub_dictionary.suffixes:
            if suffix[0] not in self.c2id.keys():
                self.c2id[suffix[0]] = len(self.c2id)
            char_id = self.c2id[suffix[0]]
            column_of_child_dictionary = self.base[node] + char_id 
            if suffix[0] not in indexed_chars:
                if suffix[0] == '#':
                    if(candidate_for_base in self.base.keys()):
                        print(' ', sub_dictionary.prefix, candidate_for_base)
                        print(' ', self.base)
                        time.sleep(3)
                    if(candidate_for_base in self.check.keys()):
                        print(' ', sub_dictionary.prefix, candidate_for_base)
                        print(' ', self.check)
                        time.sleep(3)


                    self.base[candidate_for_base] = -self.vocab_dictionary[sub_dictionary.prefix]
                    self.check[candidate_for_base] = node
                else:
                    if(column_of_child_dictionary in self.check.keys()):
                        print(column_of_child_dictionary, self.check)
                        time.sleep(3)
                    
                    indexed_chars.add(suffix[0])
                    prefix_of_child_dictionary = sub_dictionary.prefix + suffix[0]
                    self.nodes_to_be_explored.append(column_of_child_dictionary)
                    self.sub_dictionaries[column_of_child_dictionary] = MySubDictionary(prefix_of_child_dictionary, [suffix[1:]])
                    self.check[column_of_child_dictionary] = node
            elif suffix[0] in indexed_chars:
                self.sub_dictionaries[column_of_child_dictionary].append(suffix[1:])

    #make double array's base & check
    def set_base_check(self, vocabulary, vocab_dictionary):
        self.sub_dictionaries[0] = MySubDictionary('', vocabulary)
        self.vocab_dictionary = vocab_dictionary
        #set input's word in root node 
        #queue is for width search, stack is for depth search
        #nodes_to_be_explored = queue.Queue()
        self.nodes_to_be_explored = list()
        #nodes_to_be_explored.put(0)
        self.nodes_to_be_explored.append(0)
        while_i = 0
        slot_start = 1 
        while True:
            if while_i % 100000 == 0:
                print(while_i, len(self.base), slot_start)
            while_i += 1
            #node = nodes_to_be_explored.get()
            node = self.nodes_to_be_explored.pop()
            sub_dictionary = self.sub_dictionaries[node]
            pre_indexed_chars = set()
            for suffix in sub_dictionary.suffixes:
                if not suffix[0] in pre_indexed_chars and suffix[0] != '#':
                    pre_indexed_chars.add(suffix[0])
            pre_indexed_chars = sorted(pre_indexed_chars)
            slot_start = self.update_slot_start(self.check.keys(), slot_start)
           
            candidate_for_base = slot_start 
            candidate_for_base = self.get_candidate_for_base(candidate_for_base, pre_indexed_chars)

            if(node in self.base.keys()):
                print(node)
                time.sleep(3)

            self.base[node] = candidate_for_base
            
            self.add_suffixes(candidate_for_base, sub_dictionary, node) 

            #save
            #if nodes_to_be_explored.empty():
            if len(self.nodes_to_be_explored) == 0:
                with open('data/trie_base.pickle', 'wb') as base_f, open('data/trie_check.pickle', 'wb') as check_f:
                    pickle.dump(self.base, base_f)
                    pickle.dump(self.check, check_f)
                return

    def load_base_check(self, base, check):
        self.base = base
        self.check = check

    def common_prefix_search(self, query):
        present_node = 0 
        prefixes = list()
        for alphabet in query:
            num = self.base[present_node]
            if not self.base[present_node] + self.c2id[alphabet] in self.check:
                return prefixes
            elif self.check[self.base[present_node] + self.c2id[alphabet]] != present_node:
                return prefixes
            else:
                now_num = (self.base[self.base[present_node] + self.c2id[alphabet]]) 
                if now_num in self.base.keys() and self.base[now_num] < 0:
                    prefixes.append(self.vocabulary[-self.base[now_num]-1])
                present_node = self.base[present_node] + self.c2id[alphabet]
        return prefixes

    def search_word_in_sentence(self, sentence):
        candidate_words = list()
        for i in range(len(sentence)):
            search_word = sentence[i:]
            find_words =  self.common_prefix_search(search_word)
            candidate_words += find_words
        return candidate_words

