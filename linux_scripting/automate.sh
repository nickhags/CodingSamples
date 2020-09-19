#!/bin/bash

################################################################################
## This script is used to post-process files from LAMMPS molecular dynamics
## simulation. The simulation performed mimics a Dynamic Mechanical Analysis
## process, which should generate a periodic strain and stress rate.
################################################################################
## Last Modified: 09-19-2020
################################################################################
## Copyright (C) 2020 hagertnl@miamioh.edu
################################################################################

# used to switch between target frequencies
targFile="strn_xy_targ_ps.dat"
# directories to process
directs=("04_aug_20_900" "13_aug_1000_1000" "18_aug_10000_1000" \
        "20_aug_100000_1000")

# for each directory, do set method of post-processing
for root in ${directs[@]}; do
    # Generate Error files from unformatted LAMMPS output files
    cat "${root}/CIBS_300_strn_ctrl_09_em2.oe" | \
        grep "strn_err" > "${root}/tmp.dat"
    # Generate tbl files with units of fs and ps separately
    awk 'BEGIN{ t=4350; } { print t" "$5" "$6; t += 4350 }' \
        "${root}/tmp.dat" > "${root}/strn_err_fs.tbl"
    awk 'BEGIN{ t=4.350; } { print t" "$5" "$6; t += 4.350 }' \
        "${root}/tmp.dat" > "${root}/strn_err_ps.tbl"
    
    # Generate ps, fs average files from formatted LAMMPS output file
    awk '{ if ($1 != "#") { $1 = $1/1000; } print $0 }' \
        "${root}/CIBS_300_strn_ctrl_09_em2.avg" > \
        "${root}/CIBS_300_strn_ctrl_09_em2_ps.avg"
    cp "${root}/CIBS_300_strn_ctrl_09_em2.avg" \
        "${root}/CIBS_300_strn_ctrl_09_em2_fs.avg"
    
    # create fft directory if it doesn't exist, then perform automated fft
    # calculations on specific columns
    [[ ! -d "${root}/fft" ]] && mkdir "${root}/fft"
    ~/Scripts/c_cpp/fft/fft \
        -roundSize down \
        -infile "${root}/CIBS_300_strn_ctrl_09_em2_fs.avg" \
        -outfile "${root}/fft/cibs_strn.dat" \
        -col 21 \
        -step 435 \
        -alg fast
    ~/Scripts/c_cpp/fft/fft \
        -roundSize down \
        -infile "${root}/CIBS_300_strn_ctrl_09_em2_fs.avg" \
        -outfile "${root}/fft/cibs_strs.dat" \
        -col 7 \
        -step 435 \
        -alg fast
    
    # plot Strain vs Time, Error vs Time, dError/dt vs Time using
    # custom python script
    python ~/bin/plot.py \
        -t "Strain vs Time" \
        -xmin 0 \
        -xlab "Time (ps)" \
        -ylab "Strain" \
        -b 0.1 \
        -ls 1.0 \
        -o "${root}/strain_comparison.png" \
        -d "${root}/CIBS_300_strn_ctrl_09_em2_ps.avg" 1 21 "Simulated" \
        -d "${targFile}" 1 2 "Target"
    python ~/bin/plot.py \
        -t "Error vs Time" \
        -xmin 0 \
        -xlab "Time (ps)" \
        -ylab "Error" \
        -b 0.1 \
        -ls 1.0 \
        -o "${root}/error.png" \
        -d "${root}/strn_err_ps.tbl" 1 2 "Error" \
        -nolegend
    python ~/bin/plot.py \
        -t "d(Error)/dt vs Time" \
        -xmin 0 \
        -xlab "Time (ps)" \
        -ylab "d(Error)/dt" \
        -b 0.1 \
        -ls 1.0 \
        -o "${root}/d_error.png" \
        -d "${root}/strn_err_ps.tbl" 1 3 "Error" \
        -nolegend
    # remove temporary file created
    rm "${root}/tmp.dat"
done
