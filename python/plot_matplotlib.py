#!/usr/bin/env python

################################################################################
## This script is a command-line tool to easily access Matplotlib from
## a traditional Linux shell. It provides easy flags for the most common
## customizations, while leaving most of the details to the matplotlib library
################################################################################
## Last Modified: 09-19-2020
################################################################################
## Copyright (C) 2020 hagertnl@miamioh.edu
################################################################################

import matplotlib.pyplot as plt
import matplotlib.axes as mplax
import numpy as np
import sys

# user will run without arguments to print usage
if len(sys.argv) < 2:
    print("Usage: \"plot.py [OPT]\"")
    print("Options:")
    print("\t-d <datafile> <colX> <colY> <label>")
    print("\t-t <title>")
    print("\t-xmin <xmin>")
    print("\t-xmax <xmax>")
    print("\t-xlab <xlabel>")
    print("\t-ymin <ymin>")
    print("\t-ymax <ymax>")
    print("\t-ylab <ylabel>")
    print("\t-o <outputfile>")
    print("\t-b <bounds>")
    print("\t-sx <linear | log>")
    print("\t-sy <linear | log>")
    print("\t-ps <pointSize>")
    print("\t-ls <lineSize>")
    print("\t-scatter")
    print("\t-nolegend")
    print("\t-xlab_sci")
    exit(1)

# initilialize data dictionary
data = {}
data['x'] = {}
data['y'] = {}
data['label'] = []
# initialize defaults for arguments
fname = "plot.png"
xlabel = "dummy"
ylabel = "dummy"
title = "dummy"
xmin = 1.0e10
ymin = 1.0e10
xmax = -1.0e10
ymax = -1.0e10
xscale = "linear"
yscale = "linear"
bound_multiplier = 0.25
point_size = 2.0
line_size = 2.0
xmin_flag = False
ymin_flag = False
xmax_flag = False
ymax_flag = False
no_legend = False
scatter = False
xlab_sci = False
datasets = 0

# read user arguments
index = 1
while index < len(sys.argv):
    if sys.argv[ index] == "-d":
        index += 1
        df = open(sys.argv[index], 'r')
        index += 1
        colx = int(sys.argv[index]) - 1
        index += 1
        coly = int(sys.argv[index]) - 1
        index += 1
        data['label'].append(sys.argv[index])
        data['x'][datasets] = []
        data['y'][datasets] = []
        # read data line by line
        for line in df:
            line = line.split()
            # read in line, check if the value requires bounds to be adjusted
            if not line[0] == '#':
                if float(line[colx]) > xmax and not xmax_flag:
                    xmax = float(line[colx])
                if float(line[coly]) > ymax and not ymax_flag:
                    ymax = float(line[coly])
                if float(line[colx]) < xmin and not xmin_flag:
                    xmin = float(line[colx])
                if float(line[coly]) < ymin and not ymin_flag:
                    ymin = float(line[coly])
                data['x'][datasets].append(float(line[colx]))
                data['y'][datasets].append(float(line[coly]))
        datasets += 1
    elif sys.argv[index] == "-o":
        # specifies output file
        index += 1
        fname = sys.argv[index]
    elif sys.argv[index] == "-t":
        # specify title
        index += 1
        title = sys.argv[index]
    elif sys.argv[index] == "-xmin":
        # specify lower x-bound
        index += 1
        xmin_flag = True
        xmin = float(sys.argv[index])
    elif sys.argv[index] == "-b":
        # specify fraction of largest number to set bounds to if automatic
        index += 1
        bound_multiplier = float(sys.argv[index])
    elif sys.argv[index] == "-ymin":
        # specify lower y-bound
        index += 1 
        ymin_flag = True
        ymin = float(sys.argv[index])
    elif sys.argv[index] == "-xmax":
        # specify upper x-bound
        index += 1
        xmax_flag = True
        xmax = float(sys .argv[index])
    elif sys.argv[index] == "-ymax":
        # specify upper y-bound
        index += 1
        ymax_flag = True
        ymax = float(sy s.argv[index])
    elif sys.argv[index] == "-xlab":
        # specify x label
        index += 1
        xlabel = sys.a rgv[index]
    elif sys.argv[index] == "-ylab":
        # specify y label
        index += 1
        ylabel = sys. argv[index]
    elif sys.argv[index] == "-sx":
        # specify x scale (linear, log)
        index += 1
        xscale = sys .argv[index]
    elif sys.argv[index] == "-sy":
        # specify y scale (linear, log)
        index += 1
        yscale = sy s.argv[index]
    elif sys.argv[index] == "-scatter":
        # specify plot type as scatter
        scatter = True
    elif sys.argv[index] == "-xlab_sci":
        # specify to use scientific notation on x tics
        xlab_sci = True
    elif sys.argv[index] == "-nolegend":
        # specify to not show legend
        no_legend = True
    elif sys.argv[index] == "-ps":
        # specify pointSize for scatter plots
        index +=  1
        point_size = float(sys.argv[index])
    elif sys.argv[index] == "-ls":
        # specify lineSize for non-scatter plots
        index += 1 
        line_size = float(sys.argv[index])
    index += 1

# axis scaling
plt.xscale(xscale)
plt.yscale(yscale)
plt.grid(False)

# axis labels
plt.xlabel(xlabel)
plt.ylabel(ylabel)

# title
plt.title(title)

# calculate x-min, x-max, y-min, y-max
if not xmin_flag:
    xmin = xmin - abs(xmin*bound_multiplier)
if not ymin_flag:
    ymin = ymin + abs(ymax*bound_multiplier)
if not ymin_flag:
    ymin = ymin - abs(ymin*bound_multiplier)
if scatter and not xmax_flag:
    xmax = xmax + abs(xmax*bound_multiplier)/2

# set bounds if log scales not active
if not xscale == "log" and not yscale == "log":
    # axis range: xlo, xhi, ylo, yhi
    plt.axis([xmin, xmax, ymin, ymax])

# activate xlab scientific notation if specified
if xlab_sci:
    plt.ticklabel_format(axis='x', style='sci', useMathText=True, scilimits=(0,0))

# for each datafile, plot the points
for index in range(0, datasets):
    if scatter:
        plt.scatter(data['x'][index], data['y'][index], s=point_size, label=data['label'][index])
    else:
        plt.plot(data['x'][index], data['y'][index], label=data['label'][index], linewidth=line_size)

# set legend
if not no_legend:
    plt.legend()

# save figure to specified output filename
plt.savefig(fname)
