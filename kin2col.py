#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

parser = argparse.ArgumentParser(description='Convert Plate Reader Data for better usage.')
parser.add_argument('inputfile', help="Raw input txt file.")
parser.add_argument('--header', default=0, help="Print only header information, for debugging. (0 or 1)")
parser.add_argument("-t","--time_unit", default="sec", type=str, help="Which time units will be outputted. Default is seconds. (sec or min)")
args = parser.parse_args()

fnfull    = args.inputfile
time_unit = args.time_unit

fid = open(fnfull, 'rU')
raw = fid.readlines()
fid.close()

def convertTimes(strinput, units="sec"):
    tmp = strinput.split(':')
    if len(tmp) == 2:
        # the first one is minutes, second one is seconds
        retval = float(tmp[0]) * 1 + float(tmp[1]) / 60.
        if units=="min":
            return str(round(retval,4))
        elif units=="sec":
            return str(round(retval * 60.0,4))

    elif len(tmp) == 3: # first one is hours, minutes and then seconds
        retval = float(tmp[0]) * 60. + float(tmp[1]) * 1. + float(tmp[2]) / 60.
        if units=="min":
            return str(round(retval,4))
        elif units=="sec":
            return str(round(retval * 60.0, 4))


# number of total lines
Nlines = len(raw)
initID  = []
# find the initial index, this is where the data heaader begins
for rawid, rawline in enumerate(raw):
    if 'Plate:' in rawline:
        initID = rawid

# get metadata from the 4th line
metadat = raw[initID].split('\t')

if not args.header:

    # Wavelengths read at
    if metadat[5]=='Absorbance':
        WaveRead = metadat[15]
        Ndat = int(metadat[8])
    elif metadat[5]=='Fluorescence':
        WaveRead = metadat[16]
        Ndat = int(metadat[9])
        if metadat[4]=='Spectrum':
            WaveRead = metadat[12]
            Ndat = int(metadat[9])
    elif metadat[5]=='Fluor Polarization':
        WaveRead = metadat[15]
        Ndat = int(metadat[8])
    else:
        print "Experiment mode not recognized. Please implement this for : %s" % (metadat[5])
        sys.exit("Experiment type Error.")

    WaveRead = WaveRead.split(' ')
    Nwave    = len(WaveRead)

    # Acquisition type
    AcqType  = raw[initID].split('\t')[5]

    # Get Data that is not empty
    beginIdx = initID+2 
    example  = raw[initID+2].split('\t')
    goodCol  = []

    for cc in range(len(example)):
        if example[cc] != '' and example[cc] != '\n':
            goodCol.append(int(cc))

    # Get column titles
    header   = raw[initID+1].split('\t')
    header   = [header[idx] for idx in goodCol]
    if metadat[4]=='Kinetic':
        header[0] = 'Time(%s)' % (time_unit)
        header[1] = 'Temperature'
    elif metadat[4]=='Endpoint':
        header[0] = 'Temperature'
    elif metadat[4]=='Spectrum':
        header[0] = 'Wavelength(nm)'
        header[1] = 'Temperature'

    print "#### HEADER INFO ####"
    print header

    for eachWavelength in range(Nwave):
        
        fnout = '%s_%s%s.%s' % (fnfull[:-4],AcqType,WaveRead[eachWavelength],'tab.txt')
        fid   = open(fnout,'w')
        print 'Wavelength : %d' % eachWavelength

        #Write header
        for hid,hval in enumerate(header):
            fid.write(hval)
            if hid < (len(header)-1):
                fid.write('\t')

        fid.write('\n')

        if eachWavelength > 0:
            spacer = eachWavelength
        else:
            spacer = 0
            
        for eachRow in range(Ndat):
            
            currow = beginIdx + Ndat*eachWavelength + eachRow + spacer

            tmp = raw[currow].split('\t')
            try:
                goodtmp = [tmp[eachCol] for eachCol in goodCol]
            except IndexError:
                print "Error at line %d: " % (eachRow+1)
                print tmp

            if metadat[4]=='Kinetic':
                goodtmp[0] = convertTimes(goodtmp[0])

            for colid,colval in enumerate(goodtmp):
                fid.write(colval)
                if colid < (len(goodtmp)-1):
                    fid.write('\t')
                    
            fid.write('\n')

        fid.close()
# debug only, print out header information if flag is args.header is True        
else: 
    for i,e in enumerate(metadat):
        print "index ===> %d :\t\t %s" % (i,e)

    
        
