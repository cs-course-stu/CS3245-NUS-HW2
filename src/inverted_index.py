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
        self.total_doc = set([])
        # self.dictionary = {}
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
        i = 0
        stop_words = set(stopwords.words('english'))
        for file in files:
            if i >= 500:
                break
            if not os.path.isdir(file):
                f = open(in_dir+"/"+file)
                doc_id = file
                self.total_doc.add(file)
                iter_f = iter(f)
                for line in iter_f:
                    # tokenize
                    tokens = [word for sent in nltk.sent_tokenize(
                        line) for word in nltk.word_tokenize(sent)]
                    for token in tokens:
                        # remove stopwords
                        if token not in stop_words:
                            # stemmer.lower
                            porter_stemmer = PorterStemmer()
                            clean_token = porter_stemmer.stem(token).lower()
                            if clean_token.isalnum():
                                if clean_token in self.dictionary:
                                    self.postings[clean_token][0].add(int(doc_id))
                                else:
                                    self.dictionary[clean_token] = ""
                                    self.postings[clean_token] = [
                                        {int(doc_id)}, set()]
            i = i+1
        # add skip pointer
        for key, value in self.postings.items():
            tmp = int(0)
            length = len(self.postings[key][0])
            for i in range(int(np.sqrt(length))):
                tmp = tmp + int((length-1)/(int(np.sqrt(length))))
                if tmp != 0:
                    self.postings[key][1].add(int(tmp))
        print('build index successfully!')

    """ save dictionary and postings given fom build_index() to file

    Args: 
        total_doc: total doc_id
        dictionary: all word list
        postings: set of doc_id
    """

    def SavetoFile(self):
        print('saving to file...')
        # sort
        self.dictionary["  "] = sorted(self.total_doc)
        self.postings = OrderedDict(sorted(self.postings.items(), key=lambda item: item[0]))
        self.dictionary = OrderedDict(
            sorted(self.dictionary.items(), key=lambda item: item[0]))
        dict_file = open(self.dictionary_file, 'wb+')
        post_file = open(self.postings_file, 'wb+')
        # file->while( sort posting -> save posting and skip point -> tell -> save to offset of dictionary )-> dump dictionary
        pos = 0
        for key, value in self.postings.items():
            # sort the posting list
            tmp = np.sort(np.array(list(self.postings[key][0])))
            self.postings[key][0] = tmp
            # sort the skip pointer list
            tmp = np.sort(np.array(list(self.postings[key][1])))
            self.postings[key][1] = tmp
            pos = post_file.tell()
            self.dictionary[key] = pos
            np.save(post_file, self.postings[key], allow_pickle=True)
        pickle.dump(self.dictionary, dict_file)
        print('save to file successfully!')
        return

    """ load dictionary and postings from file

    Args: 
        dictionary_file: the file path of the dictionary.
        postings_file: the file path of the postings

    Returns:
        total_doc: total doc_id
        dictionary: all word list
        postings: set of doc_id
    """

    def LoadFile(self):
        print('loading file...')
        dictionary = pickle.load(
            open(self.dictionary_file, 'rb'))
        postings = open(self.postings_file, 'rb')
        total_doc = self.dictionary['  ']
        postings.seek(int(self.dictionary['that']))
        postings = pickle.load(postings)
        print('load file successfully!')
        return total_doc, self.dictionary, postings

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
        self.dictionary = pickle.load(
            open(self.dictionary_file, 'rb'))
        total_doc = self.dictionary['  ']
        print('load dictionary successfully!')
        return total_doc, self.dictionary
    
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
        postings = open(self.postings_file, 'rb')
        postings.seek(int(self.dictionary[term]))
        postings = np.load(postings, allow_pickle=True)
        print('load postings successfully!')
        return postings

if __name__ == '__main__':
    # test the example: that
    inverted_index = InvertedIndex('dictionary.txt', 'postings.txt')
    inverted_index.build_index(
        '/Users/wangyifan/Google Drive/reuters/training')
    inverted_index.SavetoFile()
    print("test the example: that")
    print(inverted_index.postings['that'])
    total_doc, dictionary = inverted_index.LoadDict()
    postings = inverted_index.LoadPostings('that')
    print(postings)
