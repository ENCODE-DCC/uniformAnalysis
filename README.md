ucscUniformAnalysis
===================

Uniform analysis pipeline for ENCODE 3 data.  This has been through two major revisions so far,
which is reflected in the directory structure.  The first revision was designed to work with
both Galaxy and with the programs for the ENCODE production analysis going through jobTree. It
is the work of Tim Dreszer and Morgan Maddren.  It is still used for Galaxy.  The second revision
aims to make the analysis steps independent of any particular framework, and is used in the
production side. 

The main subdirectories are:
   src - Python source dir for Galaxy and initial standalone pipeline.
   glue - Bash source dir for simplified pipeline steps
   helper - Python source code for simplified pipeline steps.

