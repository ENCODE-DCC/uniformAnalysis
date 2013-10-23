from src.logicalStep import StepError

def version(step, logOut=True):
    '''
    Returns tool version.  Will log to stepLog unless requested not to.
    '''
    if logOut:
        step.log.out("# autosomeCount [version: unversioned]")
    return 'unversioned'

def countUnique(step, sam, counts):
    '''
    https://github.com/qinqian/GCAP/blob/master/gcap/pipeline-scripts/autosome_uniq_map_bwa.awk
    '''
    step.log.logToolStart('autosome count unique')

    step.err = step.ana.runCmd(
        '{awk} -f {script} {samIn} > {countsOut}'
        .format(awk='awk', script='', samIn=sam, countOut=counts), logOut=False, log=step.log)
          
    step.log.logToolEnd('autosome count unique', step.err)
          
    if step.err != 0:
        raise StepError('countUnique')

