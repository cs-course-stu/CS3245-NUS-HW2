import numpy as np
import linecache
import re
import nltk
import sys
import getopt
import linecache
import os
import nltk
import pickle
import ast
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from collections import OrderedDict


class InvertedIndex:
    """ class InvertedIndex is a class dealing with building index, saving it to file and loading it

    Args:
        in_dir: working path
        dictionary_file: the file path of the dictionary.
        postings_file: the file path of the postings
    """

    def __init__(self, in_dir, dictionary_file, postings_file):
        self.in_dir = in_dir
        self.dictionary_file = dictionary_file
        self.postings_file = postings_file

    """ build index from documents stored in the input directory,
        then output the dictionary file and postings file

    Args: 
        in_dir: working path

    Returns:
        total_doc: total doc_id
        dictionary: all word list
        postings: set of doc_id
    """

    def build_index(self):

        print('indexing...')
        files = os.listdir(self.in_dir)
        i = 0
        dictionary = {}
        postings = {}
        total_doc = set([])
        stop_words = set(stopwords.words('english'))
        for file in files:
            if i >= 10:
                break
            if not os.path.isdir(file):
                f = open(self.in_dir+"/"+file)
                doc_id = file
                total_doc.add(file)
                iter_f = iter(f)
                for line in iter_f:
                    # tokenize
                    # stemmer.lower
                    tokens = [word for sent in nltk.sent_tokenize(
                        line) for word in nltk.word_tokenize(sent)]
                    #print(tokens)
                    for token in tokens:
                        if token not in stop_words:
                            porter_stemmer = PorterStemmer()
                            clean_token = porter_stemmer.stem(token).lower()
                            if clean_token.isalnum():
                                if clean_token in dictionary:
                                    #if int(doc_id) not in postings[clean_token][0]:
                                    postings[clean_token][0].add(int(doc_id))
                                    # postings[clean_token][0] = np.append(
                                    #     postings[clean_token][0], [int(doc_id)])
                                else:
                                    dictionary[clean_token] = ""
                                    tempset = set([int(doc_id)])
                                    postings[clean_token] = [
                                        set([]), set([])]
                                    postings[clean_token][0] = tempset
                #print(file)
                #print(str)
            i = i+1
        # postings = OrderedDict(sorted(postings.items(), key=lambda item: item[0]))
        # dictionary = OrderedDict(sorted(dictionary.items(), key=lambda item: item[0]))
        for key, value in postings.items():
            # postings[key][0] = np.sort(postings[key][0])
            tmp = int(0)
            length = len(postings[key][0])
            for i in range(int(np.sqrt(length))):
                tmp = tmp + int((length-1)/(int(np.sqrt(length))))
                postings[key][1].add(int(tmp))

        # dictionary['  '] = list(total_doc)
        # print(type(dictionary))
        # print(dictionary['  '])
        return total_doc, dictionary, postings

    """ save dictionary and postings given from build_index() to file

    Args: 
        total_doc: total doc_id
        dictionary: all word list
        postings: set of doc_id
    """

    def SavetoFile(self, total_doc, dictionary, postings):
        # sort
        dictionary["  "] = sorted(total_doc)
        postings = OrderedDict(sorted(postings.items(), key=lambda item: item[0]))
        dictionary = OrderedDict(
            sorted(dictionary.items(), key=lambda item: item[0]))
        dict_file = open(self.dictionary_file, 'wb+')
        post_file = open(self.postings_file, 'wb+')
        # file->while( sort posting -> save posting and skip point -> tell -> save to offset of dictionary )-> dump dictionary
        pos = 0
        for key, value in postings.items():
            tmp = list(postings[key][0])
            tmp.sort()
            #tmp = (str(postings[key]))
            postings[key][0] = tmp
            postings[key][1] = list(postings[key][1])
            pos = post_file.tell()
            dictionary[key] = pos
            pickle.dump(postings[key], post_file)
            #post_file.write(str(tmp))
            #post_file.write(str(list(postings[key][1]))+'\n')
            #post_file.write(str(postings[key])+'\n')
            # pos = post_file.tell()
            # dictionary[key]=pos
            #print(pos)
        # pickle.dump(list(total_doc), dict_file)
        pickle.dump(dictionary, dict_file)
        print(dictionary['year'])
        print(postings['year'])
        # dict_file.write(str(total_doc))
        # dict_file.write(str(dictionary))
        return

    """ load dictionary and postings from file

    Args: 
        in_dir: working path
        dictionary_file: the file path of the dictionary.
        postings_file: the file path of the postings

    Returns:
        total_doc: total doc_id
        dictionary: all word list
        postings: set of doc_id
    """

    def LoadFile(self):
        dictionary = pickle.load(
            open(self.in_dir+"/"+self.dictionary_file, 'rb'))
        postings = open(self.in_dir+"/"+self.postings_file, 'rb')
        total_doc = dictionary['  ']
        #print(total_doc)
        # print(postings[dictionary['year'][1]])
        #print(dictionary[])
        postings.seek(int(dictionary['year']))
        #line = postings.readline()
        # postings_list = eval(line)
        #postings.readline()
        postings = pickle.load(postings)
        print(dictionary['year'])
        print(postings)
        return total_doc, dictionary, postings
if __name__ == '__main__':

    inverted_index = InvertedIndex(
        '/Users/wangyifan/Google Drive/reuters/training', 'dictionary.txt', 'postings.txt')
    total_doc, dictionary, postings = inverted_index.build_index()
    print(dictionary)
    inverted_index.SavetoFile(total_doc, dictionary, postings)
    inverted_index.LoadFile()
        # print(search_engine._parse_expr('bill  OR Gates AND(vista OR XP)AND NOT mac'))


