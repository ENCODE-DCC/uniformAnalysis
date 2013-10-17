
import os, sys

class Log(object):
    """
    defines a log file with methods for logging and dumping contents to stdout
    """
    
    def __init__(self, logFile=None):
        self._logFile = logFile
        self._log = None
        
    def declareFile(self, logFile):
        """
        Sets the log file.  Set to 'None' to begin logging to stdout.
        """
        if logFile != None:
            if self._logFile != None and logFile != self._logFile:
                raise Exception("Declaring log file '" + logFile + "' on top of current log: " \
                                +  self._logFile)
            self._logFile = logFile
        return self._logFile
        
    def file(self):
        """
        Gets the log file.
        """
        return self._logFile
        
    def open(self, mode='a'):
        '''
        Opens log file.  If no file was declared out will go to stdout.
        '''
        if self._log != None and self._log.closed == False:
            return self._log
        if self._logFile != None:
            self._log = open( self._logFile, mode)
        return self._log

    def close(self):
        '''
        closes the log file
        '''
        if self._log != None and self._log.closed == False:
            self._log.close()

    def out(self, text, mode='a'):
        '''
        logs a message as a single line to the current log file
        '''
        if self._logFile == None:
            print text
            return
        self.open(mode)
        self._log.write(text + '\n')
        self.close()  # always close again, so that others might append in turn

    def appendFile(self, fileToAppend):
        """
        Dumps the contents of a file into the log
        """
        self.close()
        if self._logFile != None:
            return os.system('cat ' + fileToAppend + ' >> ' + self._logFile)
        else:
            return os.system('cat ' + fileToAppend)

    def dump(self, appendToLog=None):
        """
        Dumps the log to stdout or a provided appendToLog
        """
        self.close()
        if self._logFile == None:
            return 0
        if appendToLog != None:
            return os.system('cat ' + self._logFile + ' >> ' + appendToLog)
        else: 
            return os.system('cat ' + self._logFile)

    def remove(self):
        '''
        Removes the log file. Useful to ensure log starts empty.
        '''
        self.close()
        if self._logFile == None:
            return 0
        return os.system('rm -f ' + self._logFile)

    def empty(self):
        '''
        Another word for remove.
        '''
        self.remove()


############ command line testing ############
if __name__ == '__main__':
    """
    Command-line testing
    """
    print "======== begin '" + sys.argv[0] + "' test ========"
    log = Log('/hive/users/tdreszer/galaxy/tmp/tmp.log')
    log2 = Log()
    log2.declareFile('/hive/users/tdreszer/galaxy/tmp/tmp2.log')
    log.open('w')
    log.out('How are')
    log.out('        you?')
    log.dump()
    log.empty()
    log.out('I am')
    log.out('fine!','w')
    log2.empty()
    log.dump(log2.file())
    log2.dump()
    log.empty()
    log2.empty()

    print "======== end '" + sys.argv[0] + "' test ========"

