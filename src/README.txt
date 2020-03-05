This is the README file for A0000000X's submission

== Python Version ==

We're using Python Version 3.7.4 for this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

We divide the whole program into two parts, the construction part and the search
part. The former is to build the inverted index, build the skip pointers corresponding
to the postings and save the index into file. The latter is to load the inverted index,
parse the boolean expression query, search all the documents that meet the expression and
save the results into file. We adopt the object-oriented programming approach to build
the whole project, which greatly reduces the coupling between two parts.

[Index]


[Search]
As for the search part, we use the following steps to process a request.
   1. parse the query string based on the Shunting-yard algorithm


== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0214251W, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

* 

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>
