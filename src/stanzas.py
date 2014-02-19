#!/usr/bin/env python2.7
# stanzas.py module for reading simple (non-hierarchical) RA style files.  Used by ENCODE3.
#            File should contain "stanzas" or sets of settings delimited by at least one blank 
#            line.  Each setting consists of a single line beginning with a key word that is unique
#            to the stanza and the next non-space character starts the value of that setting.
#            Each stanza is expected to begin with a setting that is the stanza key.  All stanzas
#            in a file must begin with the same key word but have a key value that is unique
#            for the file.
#            After reading a RA stanzas file, each stanza can be retrieved as a 'dict' object
#            via the unique primary key, or optionally a secondarily declared key which may not
#            be unique. 
#            '#' based comments are supported anywhere in the file or at the end of a setting line.
#            Use '\#' to escape '#'.   Continuation lines (with '\') ARE supported. 
#            Leading whitespace on continued line is stripped.

# imports needed for Settings class:
from src.settings import Settings

class Stanzas(Settings):
    '''
    Reads in a simple (non-hierarchical) RA style file and retrieves key, and dict of value pairs

    Stanza settings should contain lines whose first word is unique to the stanza and 
    the remaining line is the value.  Each stanza must begin with the identically named setting 
    and with value unique for the file.  A secondary key can be declared after the file is read.
    Comments starting with '#' anywhere in line are stripped.  Use '\\#' to escape '#'.
    Continuation lines ('\\') ARE supported. Leading whitespace on continued line is stripped.
    '''

    @property
    def filename(self):
        return self._filename
    
    def hasAltIndex(self):
        return (self._altIndex != None)
    
    def hasUniqueAltIndex(self):
        return (self._altIndex != None and self._altUnique == True)
    
    def altLabel(self):
        return self._altLabel
    
    def primaryLabel(self):
        return self._primaryLabel
    
    def __init__(self, filePath=None, primaryLabel=None):
        Settings.__init__(self,filePath)
        self._primaryLabel=primaryLabel
        self._sortKeys = None
        self._altIndex = None
        if filePath != None:
            self._primaryLabel = self.read(filePath, primaryLabel)

    def read(self, filePath, primaryLabel=None):
        '''
        Reads RA style stanzas from a file. 
        '''
        self._filename = filePath
        fileH = open(filePath, 'r')
        
        eof = False
        while eof == False:
            stanza = dict()
            stanzaKey = None
            stanzaLabel = None
            while eof == False:
                line = self._readLineMayContinue( fileH )
                if line == None:
                    eof = True
                    break
                    
                # end of stanza?
                if line == '':
                    break
                
                line = self._stripComments(line)
                if line == '':
                    continue
            
                line = line.strip()
                if (line.startswith('#') or line == ''):
                    continue
                else:
                    key = self._loadLine(line,stanza)
                    # Stanza key is the value of the FIRST line
                    if stanzaKey == None:
                        stanzaLabel = key
                        stanzaKey = stanza[stanzaLabel]
                        
            # Make sure we didn't just have a stanza of comments!
            if stanzaKey == None:
                continue
            if primaryLabel == None:
                primaryLabel = stanzaLabel
            else:
                if primaryLabel != stanzaLabel:
                    raise Exception("RA file", self._filename, "stanzas must match on '"+ \
                                    primaryLabel+"', but found '"+stanzaLabel+"'.")
            self[stanzaKey] = stanza
        
        fileH.close()
        return primaryLabel
    
    def getKeyFromStanza(self, stanza):
        '''Returns the Primary key for a stanza.'''
        return stanza[self._primaryLabel]

    def getStanza(self, key):
        '''Returns the stanza from the primary key, or None.'''
        if key not in self:
            return None
        return self[key]

    def getFromStanza(self, stanza, setting, default=None):
        '''
        Returns the value for given a setting in a stanza.
        Not found, without a default is an exception.
        '''
        val = stanza[setting]
        if val == None:
            if default != None:
                val = default
            else:
                raise Exception("Stanza did not have setting '"+setting+"' defined.")

        return val

    def get(self, key, setting, default=None):
        '''
        Returns the value for setting from a stanza found by the given key.
        Not found, without a default is an exception.
        '''
        stanza = self[key]
        return self.getFromStanza(stanza,setting,default)
    
    def altIndex(self, altLabel, unique=True):
        '''
        Establish an alternate key which may be non-unique.
        '''
        self._altLabel = altLabel
        self._altIndex = dict()
        self._altUnique = unique
        multiplesFound = False
        for key in self.keys():
            stanza = self[key]
            altKey = stanza[altLabel]
            if altKey == None:
                raise Exception("RA file", self._filename, "stanza missing alternate label '"+ \
                                    altLabel+"'.")
            if altKey in self._altIndex:
                if unique:
                    raise Exception("RA file", self._filename, " alternate label '"+altLabel+ \
                                    "' has non-unique key '"+altKey+"'.")
                prevKey = self._altIndex[altKey]
                if not isinstance(prevKey, basestring):
                    prevKey.extend( [ self.getKeyFromStanza(stanza) ] )
                    self._altIndex[altKey] = prevKey
                else:
                    self._altIndex[altKey] = [ prevKey, self.getKeyFromStanza(stanza) ]
                multiplesFound = True
            else:
                self._altIndex[altKey] = self.getKeyFromStanza(stanza)
        if not unique and not multiplesFound:
            self._altUnique = True

            
    def getAltKeyFromStanza(self, stanza):
        '''Returns the Primary key for a stanza.'''
        return stanza[self._altLabel]

    def getUniqueStanzaFromAltKey(self, altKey):
        '''
        Returns stanza if only one stanza matches this alternate key.  Else returns None.
        '''
        if self._altIndex == None:
            raise Exception("RA file", self._filename, " does not have an alternate index.")
        if altKey not in self._altIndex:
            raise Exception("RA file", self._filename, "altKey '"+self._altLabel+ \
                            "' value '"+altKey+"' not found.")
            #return None  # Raise an execption?
        key = self._altIndex[altKey]
        if not isinstance(key, basestring):
            return None

        if key not in self:
            raise Exception("RA file", self._filename, "key '"+self._primaryLabel+ \
                            "' value '"+key+"' not found.")
        return self[key]

    def getStanzaFromAlt(self, altKey, iterator=None):
        '''
        Returns the stanza for the alternate key.
        Pass in previous return to iterate through non-unique keys.
        Order of stanzas can be established using setSortOrder().
        '''
        stanza = self.getUniqueStanzaFromAltKey(altKey)
        if stanza != None:
            if iterator == None:
                return stanza
            return None

        # Walk through list of keys and return the first one after the iterator value
        if altKey not in self._altIndex:
            raise Exception("RA file", self._filename, "altKey '"+self._altLabel+ \
                            "' value '"+altKey+"' not found.")
        keyList = self._altIndex[altKey]
        if self._sortKeys:
            keyList = self.sortedKeys(self._sortKeys,keyList)
        alreadyFound = (iterator == None)
        for key in keyList: #.items():
            if key not in self:
                raise Exception("RA file", self._filename, "key '"+self._primaryLabel+ \
                                "' value '"+key+"' not found.")
            stanza = self[key]
            if alreadyFound:
                return stanza
            if iterator == stanza:
                alreadyFound = True
        return None

    def getFromAlt(self, altKey, setting, default, index=0):
        '''
        Returns the setting value for stanza found by the given altKey.  
        If non-unique key then walk through values using 0 based index. 
        Order of stanzas can be established using setSortOrder().
        Not found, without a default is an exception.  Returns None when index exceeds stanzas.
        '''
        stanza = self.getUniqueStanzaFromAltKey(altKey)
        if stanza != None:
            if index != 0:
                return None
            return self.getFromStanza(stanza,setting,default)

        # Walk through list of keys and return the first one after the iterator value
        key = self._altIndex[altKey]
        stanzaCount = 0
        for thisKey in key.items():
            stanza = self[thisKey]
            if index == stanzaCount:
                return self.getFromStanza(stanza,setting,default)
            stanzaCount += 1
        return None

    def altCmpKey(self, key):
        '''Returns an alternate key for sort comparison.'''
        if self._sortKeys != None:
            altKey = ''
            for setting in self._sortKeys:
                altKey = altKey + self.get(key,setting,' ').lower() + ' '
            return altKey
        return self.getAltKeyFromStanza(self[key]).lower() + ' ' + key

    def setSortOrder(self, settingOrder):
        '''
        Sets the standard sort order which can be used for sorting, printing, 
        and non-unique key iteration.
        '''
        if settingOrder == None and self._sortKeys != None:
            settingOrder = self._sortKeys
        if settingOrder == None and self._altIndex != None:
            settingOrder = [ self._primaryLabel, self._altLabel ] 
        if settingOrder == None:
            settingOrder = [ self._primaryLabel ] 
        self._sortKeys = settingOrder
        return self._sortKeys
    
    def sortedKeys(self, settingOrder=None, keys=None):
        '''
        Returns keys sorted by the list of settings supplied.
        '''
        self.setSortOrder(settingOrder)
        if keys == None:
            keys = stanzas.keys()
        keys.sort(key=stanzas.altCmpKey)
        return keys
    
    def stanzaPrint(self, stanza, settingOrder=None):
        '''Prints one stanza.'''
        settingOrder = self.setSortOrder(settingOrder)
        for setting in settingOrder:
            if setting in stanza:
                print setting,stanza[setting]
        for setting in stanza.keys():
            if setting not in settingOrder:
                print setting,stanza[setting]
            


############ command line testing ############
if __name__ == '__main__':
    """
    Test this thang
    """
    stanzas = Stanzas('/hive/groups/encode/encode3/tools/tools.ra')
    print "Primary Label:", stanzas.primaryLabel()
    altLabel = 'packageName'
    stanzas.altIndex(altLabel,unique=False)
    stanzas.setSortOrder([stanzas.altLabel(),'name','version',stanzas.primaryLabel()])
    print '---------------'
    key = 'java'
    stanza = stanzas.getUniqueStanzaFromAltKey(key)
    if stanza != None:
        stanzas.stanzaPrint(stanza)
    else:
        while True:
            stanza = stanzas.getStanzaFromAlt(key,stanza)
            if stanza == None:
                break
            print ' '
            stanzas.stanzaPrint(stanza)
       
    print '---------------\nUnordered List:\n'
    for key in sorted( stanzas.keys() ):
        stanza = stanzas[key]
        print "Tool",stanza['name'],stanzas.primaryLabel()+':'+stanzas.getKeyFromStanza(stanza)
    print '---------------\n'

    print '---------------\nOrdered List:\n'
    keys = stanzas.sortedKeys([altLabel,'name','version'])
    stanzas.setSortOrder([stanzas.primaryLabel(),stanzas.altLabel(),'name','version'])
    for key in keys:
        stanza = stanzas[key]
        print ' '
        stanzas.stanzaPrint(stanza,[stanzas.primaryLabel(),altLabel,'name','version'])
    print '---------------\n'
    

