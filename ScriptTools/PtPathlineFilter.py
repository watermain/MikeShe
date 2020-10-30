# Subject:  Copy particle IDs from one registration extraction result shapefile
#           to the particle ID list of one pathline extraction section in a .she-file
#           so that you can run the pathline extraction using the same particles.
# Requires: pyshp (pip install pyshp)
# Usage:    - double click in explorer and answer questions (if python-files on your system are associated with an interpreter)
#           - run from console with -h flag to show help
#           - run with all arguments in a scripting workflow (non-interactive)
#           - run with missing arguments (interactive)
#           - use main() function from other script (not tested)
# Guarantee: none! No extensive testing has been done! BACKUP the she file you are working with!
#            Future changes to the structure of the she file can lead to unpredictable behaviour when using the resulting she-file!
#            This script was deloped for MIKE SHE FlowModelDoc-version: 20
# License:  DHI
# Author:   dhi\uha
# date:     11/2020

# Do not remove the following "APDATA section"! It is being used to store the most recently used configuration!
# Set your default values if you like:
# APPDATA section
# shePath    = C:/Work/MainDev/Products/Source/MSHE/RegTest/WQ/Karup/Karup_PTRegLenses.she
# ptRegName  = PTOR
# ptPathName = qwert
# last modified: 29.10.20 16:15:33
# END APPDATA section

import argparse
from   configparser import ConfigParser, ExtendedInterpolation
from   datetime     import datetime
import glob
import os
import re
import shutil
import traceback

class ptf:
    PtPathExtrTempl = \
    "      [PT_Pathline_Extraction]\n"\
    "         Touched = 1\n"\
    "         IsDataUsedInSetup = 1\n"\
    "         MzSEPfsListItemCount = {0}\n"\
    "         NumberOfExtractions = {0}\n"\
    "{1}"\
    "      EndSect  // PT_Pathline_Extraction\n"

    # arg 0: ID of extraction, arg 1: particleIds section
    extrSectTempl = \
    "         [Extraction_{0}]\n"\
    "            Touched = 1\n"\
    "            IsDataUsedInSetup = 1\n"\
    "            Name = '{1}'\n"\
    "            Comment = 'Generated by PtPathlineFilter.py'\n"\
    "            CreateTextFile = 1\n"\
    "            CreateXMLFile = 1\n"\
    "            CompressedXMLFormat = 1\n"\
    "            ExtrAllParticlesCheck = 0\n"\
    "{2}"\
    "         EndSect  // Extraction_{0}\n\n"

    # arg 0: particle count, arg 1: list of particleIds
    particleIdsTempl = \
    "            [Particle_IDs]\n"\
    "               NumberOfParticleIDs = {0}\n"\
    "{1}\n"\
    "            EndSect  // Particle_IDs\n\n"

    particleIdTempl = "               id = {0}"

    def __init__(self):
        self.shePath    = ""
        self.ptRegName  = "" # which PT-Registration extraction to use
        self.ptPathName = ""

    def __repr__(self):
        res = \
            "shePath:    {0}\n" \
            "ptRegName:  {1}\n" \
            "ptPathName: {2}\n" \
            .format(self.shePath, self.ptRegName, self.ptPathName)
        return res

def readCfg(cfg):
    parser = ConfigParser(interpolation=ExtendedInterpolation())
    reAppdataStart = re.compile(" *# ?APPDATA section.*")
    reAppdataEnd = re.compile(" *# ?END APPDATA section.*")
    reCommentSplit = re.compile("( *#)(.*)")
    reCodeLine = re.compile(" *[^#]")
    inAppdataSection = False
    cfgStr = "[X]\n"
    lFoundStart = False
    lFoundEnd   = False

    with open(__file__, 'r') as thisFile:
        for line in thisFile:
            if inAppdataSection:
                if reCodeLine.match(line) is not None:
                    break # error: non-commented line after start and before end tag
                lFoundStart = True
                inAppdataSection = reAppdataEnd.match(line) is None
                if not inAppdataSection: # then this line has the closing tag
                    lFoundEnd = True
                    break

            if inAppdataSection:
                cfgStr += reCommentSplit.match(line).group(2) + "\n"
            else:
                inAppdataSection = reAppdataStart.match(line) is not None

    if not lFoundStart or not lFoundEnd:
        msg = 'This script file needs to contain the following 2 lines:\n'
        msg += '# APPDATA section\n'
        msg += '# END APPDATA section\n'
        msg += 'Each existing line between these tags must follow the pattern "# key = value", but no line is required to be present'
        raise RuntimeError(msg)
    parser.read_string(cfgStr)
    if "shePath" in parser["X"]:
        cfg.shePath     = parser["X"]["shePath"]
    if "ptRegName" in parser["X"]:
        cfg.ptRegName   = parser["X"]["ptRegName"]
    if "ptPathName" in parser["X"]:
        cfg.ptPathName  = parser["X"]["ptPathName"]

def writeCfg(cfg):
    shutil.copy2(__file__, __file__ + "~") # backup copy
    reAppdataStart = re.compile(" *# APPDATA section.*")
    reAppdataEnd = re.compile(" *# END APPDATA section.*")
    reCommentSplit = re.compile("( *#)(.*)")
    inAppdataSection = False
    cfgStr = "# shePath    = {0}\n" \
             "# ptRegName  = {1}\n" \
             "# ptPathName = {2}\n".format(cfg.shePath, cfg.ptRegName, cfg.ptPathName)
    cfgStr += "# last modified: " + datetime.now().strftime("%d.%m.%y %H:%M:%S") + "\n"

    with open(__file__, 'w') as thisFile, open(__file__ + "~", "r") as inFile:
        for line in inFile:
            if inAppdataSection:
                inAppdataSection = reAppdataEnd.match(line) is None
                if not inAppdataSection:
                    thisFile.write(cfgStr) # new configuration

            if inAppdataSection:
                pass # eat existing config
            else:
                 # outside (includes start/end tag)
                inAppdataSection = reAppdataStart.match(line) is not None
                thisFile.write(line)

def getShePath(lastCfg):
    print("Select your .she file:")
    print('    Enter "b" to browse, "x" to exit,')
    print('    or press enter to use the default:')
    sel = "0"
    while sel and sel != 'b' and sel != 'x':
        sel = str(input('    [{0}]: '.format(lastCfg.shePath)))

    res = ""
    if not sel:
        res = lastCfg.shePath   # default
    elif sel == 'b':
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            # root.withdraw()
            # make root window ~invisible
            root.overrideredirect(True)
            root.geometry('0x0+0+0')
            res = filedialog.askopenfilename(
                title="She-file",
                initialdir  = os.path.dirname(lastCfg.shePath),
                initialfile = os.path.basename(lastCfg.shePath),
                filetypes=[('she-file', '.she')])
            root.destroy() # get rid of it so that focus returns to console!
            del(root)
        except ImportError:
            print('     Warning: Failed to load module tkinter, install it if you want to use the file selection dialog.')
            print('              Continuing in text mode.')
            res = str(input('    Enter the path: '))
    return res

def main(cfg):
    lastCfg = ptf()
    readCfg(lastCfg)
    try:
        import shapefile as shp
    except:
        print('Error: Failed to load module pyshp, install using "pip install pyshp"')
        raise

    if(not cfg.shePath):
        cfg.shePath = getShePath(lastCfg)

    if not cfg.shePath:
        print('Error: No .she-file specified, exiting'.format(cfg.shePath))
        return

    sheFolder = os.path.dirname(cfg.shePath)
    sheName = os.path.basename(cfg.shePath)
    sheName, ext = os.path.splitext(sheName)

    if not os.path.isfile(cfg.shePath) or not sheFolder or not sheName or not ext or ext.lower() != '.she':
        print('Error: File "{0}" doesn\'t exist or is not a .she-file, exiting'.format(cfg.shePath))
        return

    print("")

    while not cfg.ptRegName:
        print("Select the name of the registration extraction that you want to copy the particle IDs from")
        print('    Press enter to use the default, or enter the name: ')
        cfg.ptRegName = str(input('    [{0}]: '.format(lastCfg.ptRegName))) or lastCfg.ptRegName

    print("")

    while not cfg.ptPathName:
        print("Select the name of the pathline extraction that you want to copy the particle IDs to - ")
        print("  will be OVERWRITTEN if it exists!:")
        print('    Press enter to use the default, or enter the name: ')
        cfg.ptPathName = str(input('    [{0}]: '.format(lastCfg.ptPathName))) or lastCfg.ptPathName

    writeCfg(cfg)

    ids = set() # "set" for _unique_ particle IDs
    dbfPath = r"{0}\{1}.she - Result Files\PTReg_{2}.dbf".format(sheFolder, sheName, cfg.ptRegName)

    if not os.path.exists(dbfPath):
        print('Info: Searched for file {0}, but it doesn\'t exist.'.format(dbfPath))
        print('    Option "Create separate shape files for each extracted item" may be selected,')
        print('    trying to find separate files...')
        dbfPathPattern = r"{0}\{1}.she - Result Files\PTReg_{2}*.dbf".format(sheFolder, sheName, cfg.ptRegName)
    else:
        print('Info: Using file {0}.'.format(dbfPath))
        dbfPathPattern = dbfPath

    dbfFiles = glob.glob(dbfPathPattern)
    if len(dbfFiles) == 0:
        print('Error: Also no .dbf-Files similar to "{0}" exist.'.format(dbfPathPattern))
        print('       Possible reasons:')
        print('       - Simulation has not run, or it does not contain the specified registration extraction (spelling?)')
        print('       - The Simulation uses a custom result directory: This is not supported by this script.')
        print('       Exiting')
        return
    else:
        print("    .dbf files found!")

    for dbfFile in dbfFiles:
        with shp.Reader(dbfFile) as sf:
            for rec in sf.iterRecords():
                ids.add(rec[0])

    ptCnt = len(ids)
    ptIds = ""
    first = True
    for id in ids:
        if not first:
            ptIds += "\n"
        first = False
        ptIds += ptf.particleIdTempl.format(id) # "id = {0}"

    ptIdsSect = ptf.particleIdsTempl.format(ptCnt, ptIds) # NumberOfParticleIDs = {0}, [id = {n}\n, ...]

    shePathIn = r"{0}\{1}.~she".format(sheFolder, sheName)
    shePathOut = r"{0}\{1}.she".format(sheFolder, sheName)

    shutil.copy2(shePathOut, shePathIn) # backup copy

    inPtPathSection = False
    rePtPlSecStart    = re.compile(" *\[PT_Pathline_Extraction\]")
    rePtPlSecEnd      = re.compile(" *EndSect  // PT_Pathline_Extraction")
    rePtPathExtrStart = re.compile(' *\[Extraction_[0-9]+\]')
    rePtPathExtrEnd   = re.compile(' *EndSect  // Extraction_[0-9]+')
    rePtPathExtrName = re.compile('( *Name = \')([^\']*)')
    pathExtrCnt = 0
    pathExtrFound = False
    extractionNo = 0
    strCurrentExtr = ""
    strAllExtractions = ""

    with open(shePathIn, "r") as inf, open(shePathOut, "w") as outf:
        for lineIn in inf:
            # assume to be inside the PT-Path section _including_ lines with start- _and_ end-tag
            if not inPtPathSection:
                inPtPathSection = rePtPlSecStart.match(lineIn) is not None

            if inPtPathSection:
                startOfExtraction = rePtPathExtrStart.match(lineIn) is not None
                endOfExtraction = rePtPathExtrEnd.match(lineIn) is not None
                m = rePtPathExtrName.match(lineIn)
                if m:
                    name = m[2]

                strCurrentExtr += lineIn
                if startOfExtraction:
                    strCurrentExtr = lineIn
                if endOfExtraction:
                    extractionNo += 1
                    if name.lower() == cfg.ptPathName.lower():
                        ptExtrSect = ptf.extrSectTempl.format(extractionNo, cfg.ptPathName, ptIdsSect)
                        pathExtrFound = True
                    else:
                        ptExtrSect = strCurrentExtr + "\n"

                    strAllExtractions += ptExtrSect

                inPtPathSection = rePtPlSecEnd.match(lineIn) is None
                if not inPtPathSection: # then this line has the closing tag
                    if not pathExtrFound:
                        extractionNo += 1
                        ptExtrSect = ptf.extrSectTempl.format(extractionNo, cfg.ptPathName, ptIdsSect)
                        strAllExtractions += ptExtrSect
                    PtPathlExtrSect = ptf.PtPathExtrTempl.format(extractionNo, strAllExtractions)
                    outf.write(PtPathlExtrSect)
            else:
                outf.write(lineIn)
    print("\n.she file successfully updated! You can now run the pathline extraction!")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        cfg = ptf()
        parser.add_argument("-s", "--shepath",  help="full path to the she file", dest=cfg.shePath)
        parser.add_argument("-r", "--regname",  help="name of the registration extraction in the she file to use for transfering the particle ids from", dest=cfg.ptRegName)
        parser.add_argument("-p", "--pathname", help="name of the particle extraction in the she file to overwrite/create", dest=cfg.ptPathName)
        parser.parse_args()
        main(cfg)
    except:
        traceback.print_exc()
    input('Press Enter to Exit...')
