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
import sys, os.path, commands
from src.stanzas import Stanzas

def backupFile(filePath):
    '''Back up the file before making any changes.'''
    err = os.system('cp -f ' + filePath +' ' + filePath + '.bak')
    if err != 0:
        raise Exception("Failed to make a backup copy of " + filePath)
    print "Copied "+filePath+" to "+filePath+".bak"
        
def replaceLine(filePath,oldLine,newLine):
    '''Rewrites the entire file replacing this one line.'''
    found = False
    curFile = open(filePath, 'r')
    newFile = open(filePath+'.new', 'w')
    while True:
        line = curFile.readline()
        if line == '':
            curFile.close()
            newFile.close()
            break
        if oldLine == line.rstrip():
            found = True
            newFile.write(newLine+'\n')
        else:
            newFile.write(line)
    if found:
        err = os.system('mv -f ' + filePath + '.new ' + filePath)
        if err != 0:
            raise Exception("Failed to update " + filePath)
        print "Updated '"+oldLine+"' to '"+newLine+"'"
    else:
        raise Exception("Failed to find '"+oldLine+"' in " + filePath)
    return found
        

if __name__ == '__main__':
    """
    Usage: toolsRaCheck.py [--fixMd5sum] [{tools.ra}]
           Checks the tools.ra file for consistency
    """

    # make sure toolsDir is on path    
    err, toolsDir = commands.getstatusoutput("echo $EAP_TOOLS_DIR | tr -d ' '")
    if err == 0 and toolsDir != None and toolsDir != '':
        path = os.environ.get('PATH')
        if path != None and path.find(toolsDir) == -1:
            newPath = toolsDir + os.pathsep + path
            os.environ['PATH'] = newPath

    # Get the correct file
    toolDbFile = toolsDir + '/tools.ra'
    fixMd5sum = False
    for arg in sys.argv[1:]:
        if arg == '-fixMd5sum' or arg == '--fixMd5sum' or arg == '-fix' or arg == '--fix':
            fixMd5sum = True
        elif not arg.startswith('-'):
            toolDbFile = arg
        else: # All other options fall to here
            print "toolsRaCheck.py v1 - Checks the tools.ra file for consistency.\n" + \
                  "Usage: toolsRaCheck.py [--fixMd5sum] [{tools.ra}]\n" + \
                  "       --fixMd5sum  Updates md5sums if it is able to\n" + \
                  "       {tools.ra}   File to check.  Default ${EAP_TOOLS_DIR}/tools.ra"
            sys.exit(1)
    if not os.path.exists(toolDbFile):
        print "Failed to find '"+toolDbFile+"' tools database."
        sys.exit(1)
            
    print "--- Running '" + ' '.join(sys.argv[:]) + "' [version: V1] ---'"
    
    # If altering file, be sure to back it up first
    if fixMd5sum:
        backupFile(toolDbFile)
    
    # Counters are useful
    checkedCount = 0
    errorCount = 0
    updateCount = 0
    
    # Get the tool stanzas loaded
    tools = Stanzas(toolDbFile)
    tools.altIndex('name',unique=False)

    # Tiptoe through tools
    for key in tools.sortedKeys(['name','version','toolId']):
        toolData = tools.getStanza(key)
        name = toolData['name']
        
        # Some flags
        okay = True
        updateThisMd5sum = True  # May not be able to fix md5sum in some cases (e.g. 2 versions)
        versionPass = False
        md5Pass = False
        archivePass = False
        archiveSizePass = False
        installedDirPass = False

        # Verify version:
        try:
            version = toolData['version']
            versionCommand = toolData['versionCommand']
            err, versionFound = commands.getstatusoutput(versionCommand)
            if err != 0:
                okay = False
                print key + " {:<35}".format(name+' ('+version+')') + " ERROR: " + \
                      "expected version '" + version + "' command '" + versionCommand + "' failed"
            elif versionFound == version:
                versionPass = True
            else:
                # Look for matching tool with alternate key
                altTool = None
                while True: 
                    altTool = tools.getStanzaFromAlt(name,altTool)
                    if altTool == None:
                        okay = False
                        print key + " {:<35}".format(name+' ('+version+')') + " ERROR: " + \
                              "found version '" + versionFound + "'"
                        break
                    if altTool['version'] == versionFound:
                        versionPass = True
                        updateThisMd5sum = False # Can't always fix md5s with multi-versions
                        break;
        except:
            pass

        # Manage md5sum:
        executable = name
        if 'executable' in toolData:
            subDirExec = toolData['executable']
            if os.path.exists(toolsDir+'/'+subDirExec):
                executable = subDirExec
        err, md5sum = commands.getstatusoutput('md5sum '+toolsDir+'/'+executable + \
                                               " | awk '{print $1}'")
        if err != 0 or md5sum != key:
            if name != 'java': # java has problems: it is different exe on different machines
                okay = False
                print key + " {:<35}".format(name+' ('+version+')') + " ERROR: " + \
                      "found md5sum " + md5sum
                # update?
                if fixMd5sum and updateThisMd5sum:
                    if replaceLine(toolDbFile,'toolId '+key,'toolId '+md5sum):
                        updateCount += 1
        else:
            md5Pass = True

        # Anticipate archive
        if 'archive' in toolData:
            archive = toolData['archive']
            if not os.path.exists(archive):
                okay = False
                print key + " {:<35}".format(name+' ('+version+')') + " ERROR: " + \
                      "archive '" + archive + "' not found."
            else:
                archivePass = True
                # Check the archive size just because we can ?
                if 'packageSize' in toolData:
                    archiveSize = int(toolData['packageSize'])
                    archiveSizeFound = os.path.getsize(archive)
                    if archiveSize != archiveSizeFound:
                        print key + " {:<35}".format(name+' ('+version+')') + " ERROR: " + \
                              "archive size " + str(archiveSize) + "' does not match " + \
                              str(archiveSizeFound)
                    else:
                        archiveSizePass = True

        # Interrogate installed
        if 'installed' in toolData:
            installed = toolData['installed']
            if not os.path.exists(installed):
                okay = False
                print key + " {:<35}".format(name+' ('+version+')') + " ERROR: " + \
                      "installed directory '" + installed + "' not found."
            else:
                installedDirPass = True

        # Tool tally
        if okay:
            passMsg = 'passed:'
            if md5Pass:
                passMsg += ' md5sum'
            else:
                passMsg += '       '
            if versionPass:
                passMsg += ' version'
            else:
                passMsg += '        '
            if archivePass:
                passMsg += ' archive'
                if archiveSizePass:
                    passMsg += '/size'
                else:
                    passMsg += '     '
            else:
                passMsg += '             '
            if installedDirPass:
                passMsg += ' installedDir'
            else:
                passMsg += '             '
            print key + " {:<42}".format(name+' ('+version+')')[:41] + " " + passMsg
        else:
            errorCount += 1
        checkedCount += 1

    # Final fate
    closingMsg = "--- Tools checked: "+str(checkedCount)+"   In error: " + str(errorCount)
    if fixMd5sum:
        closingMsg += "   Fixed md5sum: "+ str(updateCount) 
    print closingMsg

