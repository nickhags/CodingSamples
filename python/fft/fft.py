#!/usr/bin/env python

################################################################################
## This script is a more-automated Python version of the C++ program
## located in the cpp directory. This script was still used in a very
## controlled environment, and is not intended to be robust against
## corrupt data.
################################################################################
## Last Modified: 09-19-2020
################################################################################
## Copyright (C) 2020 hagertnl@miamioh.edu
################################################################################

import math
import cmath
import sys
import numpy as np
from numpy.fft import fft

def readFile(fname, fcol):
    """ReadFile takes a filename and column number and returns a dict object
        of the column data for each column."""
    infile = open(fname, 'r')
    data_dict = {}
    # get first non-comment line to set number of columns
    line = infile.readline()
    while line[0] == '#' or len(line) == 0:
        line = readline()
    # line currently holds first line of data, used to set dict size
    desc = line.split()
    szDesc = len(desc)
    # initialize dictionary
    for i in range(1, szDesc + 1):
        data_dict[i] = [desc[i-1]]
    # read through each line of the file to process
    while True:
        line = infile.readline()
        if not line:
            break
        desc = line.split()
        # if desc holds data, add data to dictionary
        if desc[0] != '#' and len(desc) > 0:
            if (len(desc) > szDesc):
                print("Desc > length, line: " + line)
            else:
                for i in range(1, szDesc + 1):
                    data_dict[i].append(float(desc[i-1]))
    infile.close()
    # calculate size of each column as nearest power of 2 < currentLength
    dict_size = len(data_dict[1])
    nextPow = pow(2, int(math.log(dict_size, 2)))
    # round each column to new size
    for i in range(1, szDesc + 1):
        data_dict[i] = data_dict[i][0:nextPow]
    return data_dict

# check for correct usage
if len(sys.argv) < 4:
    print("Usage:")
    print("\t./pgm.py <infile> <col> <step>")
    sys.exit()

# returns dictionary of np.arrays by column index (1-based)
datafile = readFile(sys.argv[1], int(sys.argv[2]))

N = len(datafile[1])
step = float(sys.argv[3])
f = []
# generate list of frequencies for transformed data
for i in range(0, N / 2):
    f.append(float(i) / (float(step) * N))

# convert all datafile lists into numpy arrays
for i in range(1, len(datafile) + 1):
    datafile[i] = np.array(datafile[i], dtype=float)
# choose column specified by user to perform FFT on
data = datafile[int(sys.argv[2])]
# call numpy's fft
fftdata = fft(data, n = N)
# print data to standard output (redirected by user on command-line)
for i in range(0, N / 2):
    toPrint = complex(fftdata[i])
    print(str(f[i]) + " " + repr(abs(toPrint.real)) + " " + repr(toPrint.imag))
