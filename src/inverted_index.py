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
    dictionary = {}
    """ class InvertedIndex is a class dealing with building index, saving it to file and loading it

    Args:
        dictionary_file: the file path of the dictionary.
        postings_file: the file path of the postings
    """

    def __init__(self, dictionary_file, postings_file):
        self.dictionary_file = dictionary_file
        self.postings_file = postings_file
        self.total_doc = set()
        self.dictionary = {}
        self.postings = {}

    """ build index from documents stored in the input directory,
        then output the dictionary file and postings file

    Args: 
        in_dir: working path

    Returns:
        total_doc: total doc_id
        dictionary: all word list
        postings: set of doc_id
    """
    def build_index(self, in_dir):

        print('indexing...')
        files = os.listdir(in_dir)
        porter_stemmer = PorterStemmer()
        stop_words = set(stopwords.words('english'))

        for i, file in enumerate(files):
            if i >= 500:
                break
            if not os.path.isdir(file):
                doc_id = int(file)
                self.total_doc.add(doc_id)

                f = open(in_dir+"/"+file)
                for line in iter(f):
                    # tokenize
                    tokens = [word for sent in nltk.sent_tokenize(
                        line) for word in nltk.word_tokenize(sent)]
                    for token in tokens:
                        # remove stopwords
                        if token in stop_words:
                            continue

                        # stemmer.lower
                        clean_token = porter_stemmer.stem(token).lower()
                        if not clean_token.isalnum():
                            continue

                        if clean_token in self.dictionary:
                            self.postings[clean_token][0].add(doc_id)
                        else:
                            self.dictionary[clean_token] = 0
                            self.postings[clean_token] = [{doc_id}]

        # add skip pointer
        for key, value in self.postings.items():
            length = len(self.postings[key][0])
            num = int(np.sqrt(length))
            strip = int(length / num)

            last = strip
            pointers = np.zeros((num, ), dtype = np.int32)
            for i in range(0, num):
                pointers[i] = last
                last += strip

            self.postings[key].append(pointers)

        print('build index successfully!')

    """ save dictionary and postings given fom build_index() to file

    Args: 
        total_doc: total doc_id
        dictionary: all word list
        postings: set of doc_id
    """

    def SavetoFile(self):
        print('saving to file...')

        dict_file = open(self.dictionary_file, 'wb+')
        post_file = open(self.postings_file, 'wb+')
        # file->while( sort posting -> save posting and skip point -> tell -> save to offset of dictionary )-> dump dictionary
        pos = 0
        for key, value in self.postings.items():
            pos = post_file.tell()
            self.dictionary[key] = pos

            # sort the posting list
            tmp = np.sort(np.array(list(self.postings[key][0]), dtype = np.int32))
            #np.save(post_file, tmp, allow_pickle=True)
            self.postings[key][0] = tmp
            np.save(post_file, self.postings[key], allow_pickle=True)

        pickle.dump(self.total_doc, dict_file)
        pickle.dump(self.dictionary, dict_file)
        print('save to file successfully!')
        return

    """ load dictionary from file

    Args: 
        dictionary_file: the file path of the dictionary.
        postings_file: the file path of the postings

    Returns:
        total_doc: total doc_id
        dictionary: all word list
    """

    def LoadDict(self):
        print('loading dictionary...')
        with open(self.dictionary_file, 'rb') as f:
            self.total_doc = pickle.load(f)
            self.dictionary = pickle.load(f)

        print('load dictionary successfully!')
        return self.total_doc, self.dictionary
    
    """ load postings from file

    Args: 
        dictionary_file: the file path of the dictionary.
        postings_file: the file path of the postings
        term: word to be searched

    Returns:
        postings: set of doc_id
    """
    
    def LoadPostings(self, term):
        print('loading postings...')
        with open(self.postings_file, 'rb') as f:
            f.seek(self.dictionary[term])
            postings = np.load(f, allow_pickle=True)
        print('load postings successfully!')
        return postings


    def Create_Skip_pointer(self, array):
        skip_pointer = []
        length = len(array)
        num = int(np.sqrt(length))
        strip = int(length / num)
        last = strip
        pointers = np.zeros((num, ), dtype=np.int32)
        for i in range(0, num):
                pointers[i] = last
                last += strip

        #self.postings[key].append(pointers)
        return pointers

if __name__ == '__main__':
    # test the example: that
    inverted_index = InvertedIndex('dictionary.txt', 'postings.txt')
    #inverted_index.build_index('../../reuters/training')
    inverted_index.build_index(
        '/Users/wangyifan/Google Drive/reuters/training')
    inverted_index.SavetoFile()
    print("test the example: that")
    print(inverted_index.postings['that'])
    total_doc, dictionary = inverted_index.LoadDict()
    postings = inverted_index.LoadPostings('that')
    print(postings)
    skip_pointer = inverted_index.Create_Skip_pointer([1201,  1808,  1839,  5690,  7765,  7937,  8186,  8746,  9295,
                                        9667, 10455, 10804, 12507, 14055])
    print(skip_pointer[2])
