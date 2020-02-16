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

        print(tokens)
        return tokens

if __name__ == '__main__':

    search_engine = SearchEngine('', '')
    print(search_engine._parse_expr('bill  OR Gates AND(vista OR XP)AND NOT mac'))
