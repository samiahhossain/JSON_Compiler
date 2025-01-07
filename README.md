# JSON Frontend Compiler

This compiler is made from python and is composed of three parts: a scanner, a syntactic parser, and a semantic parser. It is made for a simplified version of JSON.

The scanner takes in the plain JSON as outputs the tokens generated. If there are lexical errors in the input, it will print the errors but attempt to recover and print tokens.
The syntactic parser takes in tokens made from the scanner and outputs the parse tree generated. If there are syntax error in the input (based on the order and type of tokens), it will print the errors but attempt to recover and print a parse tree.
The semantic parser also takes in tokens made from the scanner and outputs an abstract syntax tree. If there semantic errors in the input (rules on which tokens should exist), it will print the errors. It will not attempt to recover from the error.

Currently each part works separately. Soon they will be combined to form one whole compiler!
