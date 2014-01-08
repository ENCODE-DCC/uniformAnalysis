These are little glue scripts for analysis.  The rules for a glue script are:

1) Not longer than 25 lines
2) Checks for # of arguments
3) Prints brief usages statement if incorrect # of arguments
4) No ifs except for the one that checked # of arguments.
5) No loops 
6) Written in bash and invoked with -e for terminating at first error

Remember these scripts are as much about documentation as about running.  
We ask user to read them for answers to questions such as 'what parameters
were used with my favorite program' and how did we get from file A to file B.
