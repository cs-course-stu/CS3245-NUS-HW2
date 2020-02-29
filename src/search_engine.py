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
        tokens = self._parse_expr(expr)
        tokens.append('')

        # get the posting lists from the InvertedIndex class
        postings = {}

        # execute the boolean operations in the expr by group
        group_no = 0
        last_type = False
        exec_stack = []
        for token in tokens:
            if token == "NOT":
                exec_stack[-1][1] = not exec_stack[-1][1]
                continue

            cur_type = token == 'AND' or token == 'OR'
            same = token == exec_stack[-1] == token if exec_stack else False
            
            if last_type and not same:
                group_no += 1
                print('inter %d: op: %s: '%(group_no, exec_stack[-1]), end='')
                self.exec_group(group_no, exec_stack, postings)

            if cur_type:
                exec_stack.append(token)
            else:
                exec_stack.append([token, False])
                
            last_type = cur_type

        # return the list of docIds
        print(exec_stack[0][0])

    """ exec a group of boolean operations

    Args:
        retult_no: the intermediate term no
        exec_stack: the stack holds operations and terms
        postings: the dictionary with terms to posting lists mapping
    """
    def exec_group(self, result_no, exec_stack, postings):
        terms = []
        term_num = 1
        while exec_stack and term_num:
            last = exec_stack[-1]
            if type(last) == str:
                term_num += 1
            else:
                term_num -= 1
                if last[1]:
                    print('~', end='')
                print(last[0], ' ', end='')
                terms.append(last)
                
            exec_stack.pop()
        print('')
            
        # change the execution order

        # merge the posting lists
        self.merge_group(terms, postings)

        # add the intermediate term
        exec_stack.append(['inter_%d'%(result_no), False])

    """ merge the terms based on the order of the terms in the list

    Args:
        terms: the list of terms to be merged
        postings: the dictionary with terms to posting lists mapping

    Returns:
        merged_list: return the merged list of the terms
    """
    def merge_group(self, terms, postings):
        pass

    """ parse the query based on the Shunting-yard algorithm

    Args: 
        expr: the boolean expression

    Returns:
        ret: a list of tokens
    """
    def _parse_expr(self, expr):
        precedence = SearchEngine.precedence
        parenthese = 0
        output_stack = []
        op_stack = []
        
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

        while len(op_stack):
            output_stack.append(op_stack.pop())
        
        return output_stack

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
    print(search_engine._parse_expr('bill  OR Gates AND(vista OR XP)AND NOT mac'))
    search_engine.search('bill  OR Gates AND(vista OR XP)AND NOT mac')
