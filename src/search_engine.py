#!/usr/bin/python3

import sys
import math
import array
import numpy as np
from inverted_index import InvertedIndex

class SearchEngine:
    """ SearchEngine is a class dealing with real-time querying

    Args:
        dictionary_file: the file path of the dictionary.
        postings_file: the file path of the postings
    """
    
    precedence = { 'NOT': 0, 'AND': 1, 'OR': 2, '(': 4, ')': 5 }
    def __init__(self, dictionary_file, postings_file):
        self.dictionary_file = dictionary_file
        self.postings_file = postings_file

        self.index = InvertedIndex(dictionary_file, postings_file)
        self.doc_set, self.dictionary = self.index.LoadDict()
        self.total_postings = np.array(list(self.doc_set), dtype = np.int32)

    """ search and return docIds according to the boolean expression

    Args: 
        expr: the boolean expression

    Returns:
        docIds: the list of docIds which match the query in increasing order
    """
    def search(self, expr):
        # get the tokens from the expr
        terms, tokens = self._parse_expr(expr)
        #print(terms)
        #print(tokens)
        # get the posting lists from the InvertedIndex class
        # postings = self.index.LoadTerms(terms)
        postings_lists = self.index.LoadTerms(terms)

        # execute the boolean operations in the expr by group
        group_no = 0
        last_type = False
        exec_stack = []

        tokens.append('')
        for token in tokens:
            if token == "NOT":
                if type(exec_stack[-1]) == str:
                    group_no += 1
                    self._exec_group(group_no, exec_stack, postings_lists)
                exec_stack[-1][1] = not exec_stack[-1][1]
                last_type = False
                continue

            cur_type = token == 'AND' or token == 'OR'
            same = token == exec_stack[-1] == token if exec_stack else False
            
            if last_type and not same:
                group_no += 1
                # print('inter %d: '%(group_no), end='')
                self._exec_group(group_no, exec_stack, postings_lists)

            if cur_type:
                exec_stack.append(token)
            else:
                exec_stack.append([token, False, 0])
                
            last_type = cur_type

        # return the list of docIds
        return self._get_postings(exec_stack[0], postings_lists)[0]

    """ exec a group of boolean operations

    Args:
        group_no: the no. of the group
        exec_stack: the stack holds operations and terms
        postings_lists: the dictionary with terms to posting lists mapping
    """
    def _exec_group(self, group_no, exec_stack, postings_lists):
        assert exec_stack, 'empty execution stack'

        terms = []
        term_num = 1
        op = exec_stack[-1]
        while exec_stack and term_num:
            last = exec_stack[-1]
            if type(last) == str:
                term_num += 1
            else:
                term_num -= 1
                #if last[1]:
                    # print('~', end='')
                # print("'%s'"%last[0], end='')
                #if term_num:
                    # print(' %s '%op, end='')
                terms.append(last)
                
            exec_stack.pop()
        # print('')
            
        # change the execution order
        # print("before: ", terms)
        self._optimize_merge(terms, postings_lists)
        # print("after: ", terms)

        # merge the posting lists
        result = self._merge_group(op, terms, postings_lists)

        # add the intermediate term
        exec_stack.append(['  %d'%group_no, False, 0])
        postings_lists['  %d'%group_no] = result

    """ optimize the merging process based on merging cost

    Agrs:
        terms: the terms need to be merged
        postings_lists: the dictionary with terms to posting lists mapping

    Returns:
        terms: the list in optimized merging order
    """
    def _optimize_merge(self, terms, postings_lists):
        total_size = self.total_postings.size

        for i, term in enumerate(terms):
            term[2] = len(postings_lists[term[0]][0])
            if term[1]:
                term[2] = total_size - term[2]

        terms.sort(key=lambda key: key[2])

        return terms

    """ merge the terms based on the order of the terms in the list

    Args:
        op: the type of merging operation
        terms: the list of terms to be merged
        postings_lists: the dictionary with terms to posting lists mapping

    Returns:
        result: return the merged list of the terms
    """
    def _merge_group(self, op, terms, postings_lists):
        total_docIds = self.total_postings

        result_set = self._get_postings(terms[0], postings_lists)
        for i in range(1, len(terms)):
            right_set = self._get_postings(terms[i], postings_lists)
            # print("left_set: ", result_set)
            # print("right_set: ", right_set)
            result_set = self._merge_postings(result_set, op, right_set)
            # print("result_set: ", result_set)

        return result_set

    """ merge the two sets passed in based on the op type

    Args:
        op: the type of merging operation
        set1: the set on the left hand side to be merged
        set2: the set on the right hand side to be merged
    """
    def _merge_postings(self, set1, op, set2):
        p1, p2 = 0, 0
        skip1, skip2 = 0, 0
        postings1, pointers1 = set1[0], set1[1]
        postings2, pointers2 = set2[0], set2[1]
        len1, len2 = postings1.size, postings2.size
        sk_len1, sk_len2 = pointers1.size, pointers2.size
        result = array.array('i')
        if op == 'AND':
            while p1 < len1 and p2 < len2:
                doc1, doc2 = postings1[p1], postings2[p2]
                if doc1 == doc2:
                    result.append(doc1)
                    p1, p2 = p1 + 1, p2 + 1
                elif doc1 < doc2:
                    if skip1 < sk_len1-1 and postings1[pointers1[skip1]] <= doc2:
                        p1, skip1 = pointers1[skip1], skip1 + 1
                    else:
                        p1 += 1
                else:
                    if skip2 < sk_len2-1 and postings2[pointers2[skip2]] <= doc1:
                        p2, skip2 = pointers2[skip2], skip2 + 1
                    else:
                        p2 += 1
        elif op == 'OR':
            while p1 < len1 and p2 < len2:
                doc1, doc2 = postings1[p1], postings2[p2]
                if doc1 == doc2:
                    result.append(doc1)
                    p1, p2 = p1 + 1, p2 + 1
                elif doc1 < doc2:
                    result.append(doc1)
                    if skip1 < sk_len1-1 and postings1[pointers1[skip1]] <= doc2:
                        for p in range(p1+1, pointers1[skip1]):
                            result.append(postings1[p])
                        p1, skip1 = pointers1[skip1], skip1 + 1
                    else:
                        p1 += 1
                else:
                    if skip2 < sk_len2-1 and postings2[pointers2[skip2]] <= doc1:
                        for p in range(p2+1, pointers2[skip2]):
                            result.append(postings2[p])
                        p2, skip2 = pointers2[skip2], skip2 + 1
                    else:
                        p2 += 1
            while p1 < len1:
                result.append(postings1[p1])
                p1 += 1
            while p2 < len2:
                result.append(postings2[p2])
                p2 += 1

        result = np.frombuffer(result, dtype=np.int32)
        return (result, self.index.CreateSkipPointers(result.size))

    """ get the postings list of the term

    Args:
        term: the term which wants to the corresponding postings list
        postings_lists: the dictionary with terms to posting lists mapping

    Returns:
        postings: the postings list corresponding to the term
    """
    def _get_postings(self, term, postings_lists):
        if not term[1]:
            return postings_lists[term[0]]

        not_term = '~' + term[0]
        if not_term in postings_lists:
            return postings_lists[not_term]
        else:
            postings = postings_lists[term[0]][0]
            postings = np.setdiff1d(self.total_postings, postings)
            postings = (postings, self.index.CreateSkipPointers(postings.size))
            postings_lists[not_term] = postings
            return postings

    """ parse the query based on the Shunting-yard algorithm

    Args: 
        expr: the boolean expression

    Returns:
        terms: a list contains all the terms appeared in the boolean expression
        postfix_expr: a list of operations and operands which knowns as Reverse Polish notation
    """
    def _parse_expr(self, expr):
        parenthese = 0
        op_stack = []
        output_stack = []
        precedence = SearchEngine.precedence

        terms = set()
        tokens = self._tokenize_expr(expr)
        for token in tokens:
            if token == '(':
                op_stack.append(token)
                parenthese += 1
                continue
            if token == ')':
                assert parenthese > 0, "wrong query expression, parentheses are not matched"

                while op_stack[-1] != '(':
                    output_stack.append(op_stack.pop())

                parenthese -= 1
                op_stack.pop()
            elif token in precedence:
                while len(op_stack) and precedence[token] > precedence[op_stack[-1]]:
                    output_stack.append(op_stack.pop())

                op_stack.append(token)

            else:
                token = token.lower()
                output_stack.append(token)
                terms.add(token)

        while len(op_stack):
            output_stack.append(op_stack.pop())

        return list(terms), output_stack

    """ tokenize the expr into tokens

    Args:
        expr: the expr to be tokenized

    Returns:
        tokens: the list of tokens
    """
    def _tokenize_expr(self, expr):
        start = 0
        tokens = []

        for i, c in enumerate(expr):
            if str.isspace(c) or c == '(' or c == ')':
                if start != i:
                    tokens.append(expr[start:i])
                if c == '(' or c == ')':
                    tokens.append(c)

                start = i + 1

        if start < len(expr):
            tokens.append(expr[start:])

        return tokens

if __name__ == '__main__':

    search_engine = SearchEngine('dictionary.txt', 'postings.txt')
    print(search_engine.search('(dean OR kenneth OR douglas) AND dean'))
#18 748 1153 1792 2922 3149 4005 4290 5888 10080 10553 10564 10565 11083 11746 12050 12337 13053
