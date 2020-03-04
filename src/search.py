#!/usr/bin/python3
import re
import nltk
import sys
import getopt
from search_engine import SearchEngine

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # load the dictionary
    #inverted_index = InvertedIndex(dict_file, postings_file)
    #output: results_file output.txt
    # initialize the class
    search_engine = SearchEngine('dictionary.txt', 'postings.txt')
    file_result = open(results_file, 'w')
    with open(queries_file, 'r') as file:
        i =0
        for line in file:
            i=i+1
            result = search_engine.search(line)
            #np.save(file_result, result, allow_pickle=False)
            result = map(str, result)
            #print(type(result))
            str1 = ' '.join(result) + '\n'
            #print(str1)
            file_result.write(str1)
        #print(i)
    return

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
