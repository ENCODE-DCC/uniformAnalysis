#!/usr/bin/env python2.7
# settings.py module for reading simple key value pairs from file.  Used by ENCODE3.
#            File should contain lines whose first word is unique to the file and 
#            the remaining line is the value (file works like a single RA stanza). 
#            '#' based comments are supported anywhere in line.  Use '\#' to escape '#'.
#            Continuation lines (with '\') ARE supported. 
#            Leading whitespace on continued line is stripped.

# imports needed for Settings class:
import os, sys, string

class Settings(dict):
    '''
    Reads in a simple settings file and retrieves key, value pairs

    Simple settings file should contain lines whose first word is unique to the file and 
    the remaining line is the value (file works like a single RA stanza). 
    Comments starting with '#' anywhere in line are stripped.  Use '\\#' to escape '#'.
    Continuation lines ('\\') ARE supported. Leading whitespace on continued line is stripped.
    '''

    @property
    def filename(self):
        return self._filename
    
    def __init__(self, filePath=None, key=None):
        dict.__init__(self)
        if filePath != None:
            self.read(filePath, key)

    def read(self, filePath, key=None):
        '''
        Reads in a simple settings file. 
        '''
        self._filename = filePath
        file = open(filePath, 'r')

        #entry = None
        lines = list()
        keyValue = ''

        while True:
            line = self._readLineMayContinue( file )
            if line == None:
                break
                
            line = self._stripComments(line)
            if line == '':
                continue
        
            line = line.strip()
            if (line.startswith('#') or line == ''):
                continue
            else:
                self._loadLine(line)
        
        file.close()

        if key != None:
            return self[key]
            
    def get(self, key, default=None, alt=None):
        '''
        Returns the value for given a key
        Not found, without a default is an exception.
        '''
        val = None
        try:
            val = self[key]
        except:
            if alt != None:
                try:
                    val = self[alt]
                except:
                    pass            
        if val == None:
            if default != None:
                val = default
            else:
                raise Exception("Settings file", self._filename, "must have '"+key+"' defined.")

        return val

    def getBoolean(self, key, default=None, alt=None):
        '''
        Returns the boolean value for given a key.
        Returns False for case-insensitive 'False','F','No','N' or '0', all others return True
        Not found, without a default is an exception.
        '''
        val = self.get(key, default, alt)
        if val == False or val == "0" or val.lower() == 'no'    or val.lower() == 'n' or \
                                         val.lower() == 'false' or val.lower() == 'f':
            return False
        return True
        
    def getDir(self, key, default=None, alt=None):
        '''
        Returns an absolute path to a directory (always ending in '/').
        '''
        val = self.get(key, default, alt)
        if val != None and len(val) > 0:
            val = os.path.abspath( val )
            if not val.endswith('/'):
                val = val + '/'
        return val

    def _loadLine(self, line):
        '''
        Reads a single line extracting the key-value pair.  Returns key
        '''
        if line.startswith('#') or line == '':
            return None
        else:
            pair = line.split(None, 1) # None means separate on whitespace
            key = pair[0]
            if key in self:
                raise KeyError('Duplicate Key ' + key)
            val = ''
            if (len(pair) == 2):
                val = pair[1]
            self[key] = val
            
        return key
        
    def _readLineMayContinue(self, file):
        """
        Another readLine, but this one supports the '\' continuation character
        """
        line = ''
        while True:
            rawLine = file.readline()
            if rawLine == '':
                return None
        
            line = line + rawLine.strip()
            if len(line) > 0 and line[ len(line) - 1 ] == '\\':
                #line = line[ 0:len(line) - 1 ]
                line = line[ :-1 ]
                continue
                
            break
            
        return line

    def _stripComments(self, line):
        """
        Strips comments from a line
        """
        bam = -1
        while True:
            bam = line.find('#',bam + 1)
            if bam == -1:
                return line
            if bam == 0:
                return ''
            if line[ bam -1 ] != '\\':
                return line[ 0:bam ]  
            else: #if line[ bam -1 ] == '\\': # strip backslash and ignore '#'
                line = line[ 0:bam - 1 ] + line[ bam: ]  


############ command line testing ############
if __name__ == '__main__':
    """
    Test this thang
    """
    settings = Settings('/hive/users/tdreszer/galaxy/galaxy-dist/tools/encode/settingsE3.txt')
    # sort not sorting?  settings.sort()
    #for key in settings.keys():
    print '---------------'
    for key in sorted( settings.keys() ):
        print key+'="'+settings[key]+'"'
    print '---------------\n'
    

