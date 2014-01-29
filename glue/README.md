These are little glue scripts for analysis.  The rules for a glue script are:

1) Not too long or complex to read and understand in 2 minutes
2) Checks for # of arguments
3) Prints brief usages statement if incorrect # of arguments
4) Only change script makes to file-system is in new files created named in output args.
5) No ifs except for the one that checked # of arguments.
6) No loops 
7) Written in bash and invoked with -e for terminating at first error
8) Output files are moved as a separate operation from their creation
   so as to avoid incomplete output files.
9) Clean up is ultimately responsibility of caller, but glue scripts are encouraged
   to kill the biggest most useless temp files.
10) For eap_run scripts, all the software used in the script should be in the
    corresponding eapAnalysisStep's software list.  You don't need to include
    standard Unix utilities like "mv" and "grep."

Remember these scripts are as much about documentation as about running.  
We ask user to read them for answers to questions such as 'what parameters
were used with my favorite program' and how did we get from file A to file B.
