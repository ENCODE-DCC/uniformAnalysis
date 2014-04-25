#!/usr/bin/env python2.7
# toolsRaCheck.py v1 module for validating the tools.ra: ENCODE Analysis Pipeline tools DB file.
#            The file is a simple RA file (as read by Stanzas.py).  Several settings that can
#            be verified are: md5sum, version, archive file and size of archive, and installed dir.
#            Not every tool has all aof these settings defined and some may not be validatable.
#            The md5sum can also be fixed, if it is in error.
#     Usage: toolsRaCheck.py [--fixMd5sum] [{tools.ra}]
#            --fixMd5sum  Updates md5sums if it is able to
#            {tools.ra}   File to check.  Default ${EAP_TOOLS_DIR}/tools.ra

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
    toolsRaCheck.py v1 - Checks the tools.ra file for consistency.
    Usage: toolsRaCheck.py [--fixMd5sum] [{tools.ra}]
           --fixMd5sum  Updates md5sums if it is able to
           {tools.ra}   File to check.  Default ${EAP_TOOLS_DIR}/tools.ra
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
            if versionFound == version:
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

