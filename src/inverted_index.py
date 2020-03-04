import numpy as np
import os
import sys
import nltk
import pickle
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from collections import OrderedDict


class InvertedIndex:
    dictionary = {}
    """ class InvertedIndex is a class dealing with building index, saving it to file and loading it

    Args:
        dictionary_file: the name of the dictionary.
        postings_file: the name of the postings
    """

    def __init__(self, dictionary_file, postings_file):
        self.dictionary_file = dictionary_file
        self.postings_file = postings_file
        self.total_doc = set()
        self.dictionary = {}
        self.postings = {}
        self.file_handle = None

    """ build index from documents stored in the input directory,
        then output the dictionary file and postings file

    Args: 
        in_dir: working path
    """
    def build_index(self, in_dir):

        print('indexing...')
        if (not os.path.exists(in_dir)):
            print("wrong file path!")
            sys.exit(2)
        files = os.listdir(in_dir)
        porter_stemmer = PorterStemmer()
        stop_words = set(stopwords.words('english'))

        for i, file in enumerate(files):
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
                        # if token in stop_words:
                        #     continue
                        # stemmer.lower
                        clean_token = porter_stemmer.stem(token).lower()
                        # if not clean_token.isalnum():
                        #     continue
                        if clean_token in self.dictionary:
                            self.postings[clean_token][0].add(doc_id)
                        else:
                            self.dictionary[clean_token] = 0
                            self.postings[clean_token] = [{doc_id}]
        # add skip pointer
        for key, value in self.postings.items():
            length = len(self.postings[key][0])
            pointers = self.CreateSkipPointers(length)
            self.postings[key].append(pointers)

        print('build index successfully!')

    """ save dictionary and postings given fom build_index() to file
    """

    def SavetoFile(self):
        print('saving to file...')

        dict_file = open(self.dictionary_file, 'wb+')
        post_file = open(self.postings_file, 'wb+')
        pos = 0
        for key, value in self.postings.items():
            # save the offset of dictionary
            pos = post_file.tell()
            self.dictionary[key] = pos

            # sort the posting list
            tmp = np.sort(np.array(list(self.postings[key][0]), dtype = np.int32))
            self.postings[key][0] = tmp

            # save postings and skip pointers
            np.save(post_file, tmp, allow_pickle=True)
            np.save(post_file, self.postings[key][1], allow_pickle=True)

        # save total_doc and dictionary
        pickle.dump(self.total_doc, dict_file)
        pickle.dump(self.dictionary, dict_file)
        print('save to file successfully!')
        return

    """ load dictionary from file

    Returns:
        total_doc: total doc_id
        dictionary: all word list
    """

    def LoadDict(self):
        print('loading dictionary...')
        with open(self.dictionary_file, 'rb') as f:
            self.total_doc = pickle.load(f)
            self.dictionary = pickle.load(f)

        self.file_hande = open(self.postings_file, 'rb')

        print('load dictionary successfully!')
        return self.total_doc, self.dictionary
    
    """ load postings from file

    Args: 
        term: word to be searched

    Returns:
        (postings, pointers): doc_id and skip pointers of given term
    """

    def LoadPostings(self, term):
        if not self.file_handle:
            self.file_handle = open(self.postings_file, 'rb')

        print('loading postings...')
        self.file_handle.seek(self.dictionary[term])
        postings = np.load(self.file_handle, allow_pickle=True)
        pointers = np.load(self.file_handle, allow_pickle=True)
        print('load postings successfully!')
        return (postings, pointers)

    """ create skip pointers

    Args: 
        length: length of postings

    Returns:
        pointers: array of skip pointers
    """

    def CreateSkipPointers(self, length):
        if length <= 1:
            return np.zeros((0,), dtype=np.int32)

        num = int(np.sqrt(length))
        strip = int((length - 1) / num)
        pointers = np.zeros((num + 1, ), dtype = np.int32)
        for i in range(1, num + 1):
            pointers[i] = pointers[i - 1] + strip
        return pointers

    """ load multiple postings lists from file

    Args:
        terms: the list of terms need to be loaded

    Returns:
        postings_lists: the postings lists correspond to the terms
    """

    def LoadTerms(self, terms):
        if not self.file_handle:
            self.file_handle = open(self.postings_file, 'rb')

        ret = {}
        for term in terms:
            if term in self.dictionary:
                self.file_handle.seek(self.dictionary[term])
                postings = np.load(self.file_handle, allow_pickle=True)
                pointers = np.load(self.file_handle, allow_pickle=True)
            else:
                postings = np.zeros((0, ))
                pointers = np.zeros((0, ))
            ret[term] = (postings, pointers)

        return ret

if __name__ == '__main__':
    # test the example: that
    inverted_index = InvertedIndex('dictionary.txt', 'postings.txt')
    #inverted_index.build_index('../../reuters/training')
    # inverted_index.build_index(
    #    '/Users/wangyifan/Google Drive/reuters/training')
    # inverted_index.SavetoFile()
    print("test the example: her")
    #print(inverted_index.postings['her'])
    total_doc, dictionary = inverted_index.LoadDict()
    postings = inverted_index.LoadPostings('relief')
    print(postings)
    #1, 11459, 11911, 13462

    # postings_lists = inverted_index.LoadTerms(['bill', 'Gates', 'vista', 'XP', 'mac'])
    # for term, postings in postings_lists.items():
    #     print(term, ": ", postings)

