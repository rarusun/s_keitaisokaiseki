import queue
import math
import time
import os
import pickle

from lattice import Lattice
from trie import Trie 

class Tokenizer:
    def __init__(self):
        #use mecab-ipadic
        matrix_file_name = '../mecab-ipadic-2.7.0-20070801/matrix.def'
        dictionary_file_head = '../mecab-ipadic-2.7.0-20070801/'
         
        dict_file_list = []
        for file_n in os.listdir('../mecab-ipadic-2.7.0-20070801/'):
            if '.csv' in file_n:
                dict_file_list.append(file_n)

        matrix_dict = {}
        id_dict = {}
        vocabulary = []
        with open(matrix_file_name, 'r') as r_f:
            for line in r_f:
                s_elems = line.strip().split()
                elems = [int(e) for e in s_elems]
                if len(elems) < 3:
                    continue
                if elems[0] in matrix_dict.keys():
                    matrix_dict[elems[0]][elems[1]] = elems[2]
                else:
                    matrix_dict[elems[0]] = {elems[1]:elems[2]} 
        self.matrix_dict = matrix_dict

        for dictionary_file_name in dict_file_list:
            with open(dictionary_file_head+dictionary_file_name, 'r', encoding='eucjp') as r_f:
                for line in r_f:
                    elems = line.strip().split(',')
                    if '' == elems[0]:
                        continue
                    ids = [int(e) for e in elems[1:4]]
                    ids.append(','.join([elems[0] + '\t'] + elems[4:]))
                    if elems[0] in id_dict.keys():
                        id_dict[elems[0]].append(ids)
                    else:
                        id_dict[elems[0]] = [ids]

                    vocabulary.append(elems[0])
        self.id_dict = id_dict

        vocabulary = set(vocabulary)
        vocabulary = sorted(vocabulary)

        vocab_dictionary = {}
        for i, word in enumerate(vocabulary):
            vocab_dictionary[word] = i+1


        dictionary = Trie(0, ord('z'), vocabulary, vocab_dictionary)
        dictionary.set_base_check(vocabulary, vocab_dictionary)
        with open('data/trie_base.pickle', 'rb') as base_f, open('data/trie_check.pickle', 'rb') as check_f:
            base_dict = pickle.load(base_f)
            check_dict = pickle.load(check_f)
            dictionary.load_base_check(base_dict, check_dict)
        self.dictionary = dictionary

    def tokenize(self, sentence):
        #sentence = ''
        lattice = Lattice(sentence, self.id_dict, self.matrix_dict)

        cand_box = []
        for i in range(0, len(sentence)):
            candidate_words = self.dictionary.common_prefix_search(sentence[i:])
            cand_box += candidate_words
            has_single_word = False
            for word in candidate_words:
                # "ご飯何にしようか。" have bug
                # base's array confused some words, but now not effect search.
                if word != sentence[i:i+len(word)]:
                    continue
                lattice.insert(i, i+len(word), False)
                if (not has_single_word and len(word) == 1):
                    has_single_word = True

            if(not has_single_word):
                lattice.insert(i, i+1, True)

        results = lattice.viterbi()
        return results
