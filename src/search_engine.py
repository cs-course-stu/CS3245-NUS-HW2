#!/usr/bin/python3

import sys
import math
from collections import deque


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

        # self.index = InvertedIndex()

    """ search and return docIds according to the boolean expression

    Args: 
        expr: the boolean expression

    Returns:
        docIds: the list of docIds which match the query in increasing order
    """
    def search(self, expr):
        # get the tokens from the expr
        terms, tokens = self._parse_expr(expr)

        # get the posting lists from the InvertedIndex class
        # postings = self.index.LoadTerms(terms)
        postings = {
            ' ': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
            'mac': (4, ),
            'XP': (1, 2, 3),
            'Gates': (4, 5, 6),
            'bill': (7, 8, 9, 10),
            'vista': (2, 5)
        }

        postings_array = {
            'that': 
        }
        # execute the boolean operations in the expr by group
        group_no = 0
        last_type = False
        exec_stack = []

        tokens.append('')
        for token in tokens:
            if token == "NOT":
                exec_stack[-1][1] = not exec_stack[-1][1]
                continue

            cur_type = token == 'AND' or token == 'OR'
            same = token == exec_stack[-1] == token if exec_stack else False
            
            if last_type and not same:
                group_no += 1
                print('inter %d: '%(group_no), end='')
                self._exec_group(exec_stack, postings)

            if cur_type:
                exec_stack.append(token)
            else:
                exec_stack.append([token, False, 0])
                
            last_type = cur_type

        # return the list of docIds
        return postings[exec_stack[0][0]]

    """ exec a group of boolean operations

    Args:
        exec_stack: the stack holds operations and terms
        postings: the dictionary with terms to posting lists mapping
    """
    def _exec_group(self, exec_stack, postings):
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
                if last[1]:
                    print('~', end='')
                print("'%s'"%last[0], end='')
                if term_num:
                    print(' %s '%op, end='')
                terms.append(last)
                
            exec_stack.pop()
        print('')
            
        # change the execution order
        print("before: ", terms)
        self._optimize_merge(terms, postings)
        print("after: ", terms)

        # merge the posting lists
        result = self._merge_group(op, terms, postings)
        print(result)

        # add the intermediate term
        exec_stack.append(['  ', False, 0])
        postings['  '] = result

    """ optimize the merging process based on merging cost

    Agrs:
        terms: the terms need to be merged
        postings: the dictionary with terms to posting lists mapping

    Returns:
        terms: the list in optimized merging order
    """
    def _optimize_merge(self, terms, postings):
        total_size = len(postings[' '])

        for i, term in enumerate(terms):
            if term[1]:
                term[2] = total_size - len(postings[term[0]])
            else:
                term[2] = len(postings[term[0]])

        terms.sort(key=lambda key: key[2])

        return terms

    """ merge the terms based on the order of the terms in the list

    Args:
        op: the type of merging operation
        terms: the list of terms to be merged
        postings: the dictionary with terms to posting lists mapping

    Returns:
        result: return the merged list of the terms
    """
    def _merge_group(self, op,  terms, postings):
        total_docIds = set(postings[' '])

        result_set = set(postings[terms[0][0]])
        result_set = result_set if not terms[0][1] else total_docIds - result_set
        for i in range(1, len(terms)):
            right_set = set(postings[terms[i][0]])
            right_set = right_set if not terms[i][1] else total_docIds - right_set
            if op == 'AND':
                result_set = result_set & right_set
            elif op == 'OR':
                result_set = result_set | right_set

        return tuple(result_set)

    """ merge the two sets passed in based on the op type

    Args:
        op: the type of merging operation
        set1: the set on the left hand side to be merged
        set2: the set on the right hand side to be merged
    """
    def _merge_postings(self, set1, op, set2, total_docIds):
        if set1[1] == True:
            set1, set2 = set2, set1

        result = []
        return result

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

        if start <= len(expr):
            tokens.append(expr[start:])

        return tokens

if __name__ == '__main__':

    search_engine = SearchEngine('', '')
    print(search_engine.search('bill  OR Gates AND(vista OR XP)AND NOT mac'))
