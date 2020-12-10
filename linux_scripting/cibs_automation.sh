#!/bin/bash

################################################################################
## This script creates and prepares a template file to allow scalability
## of molecular dynamics simulations to many systems. Manages the directory
## structure, and handles different compilers/architectures.
################################################################################
## Last Modified: 12-09-2020
################################################################################
## Copyright (C) 2020 hagertnl@miamioh.edu
################################################################################


if [[ $1 == "help" ]]; then
    echo "Usage: ./cibs_automation.sh"
    echo "   All configuration options can be managed in opts.sh"
    exit 1
fi

# user sets certain variables in opts.sh to avoid having excessive
# command-line arguments
source opts.sh

ACCEL_SEL=""

ENABLE_GPU=0
ENABLE_MLA=0

ACCEL="-sf opt"
if (( ${NGPUS} > 0 )); then
    echo "Initializing to run with GPUs"
    ACCEL_SEL=":ngpus=${NGPUS}"
    ACCEL="-sf gpu -pk gpu ${NGPUS}"
    ENABLE_GPU=1
elif (( ${NMLAS} > 0 )); then
    echo "Initializing to run with MLAs"
    ACCEL_SEL=":nmlas=${NMLAS}"
    ACCEL="-sf gpu -pk gpu ${NMLAS} tpa 32"
    ENABLE_MLA=1
else
    echo "No acceleration packages selected"
fi

# Initialize SELECT commands
XLINK_SELECT="select=1:ncpus=${PPN}:mpiprocs=${PPN}${ACCEL_SEL}"
ANNEAL_SELECT="select=${ANNEAL_NODES}:ncpus=${PPN}:mpiprocs=${PPN}${ACCEL_SEL}"
MSD_SELECT="select=${MSD_NODES}:ncpus=${PPN}:mpiprocs=${PPN}${ACCEL_SEL}"
TEMP_SELECT="select=${TEMP_NODES}:ncpus=${PPN}:mpiprocs=${PPN}${ACCEL_SEL}"
DMA_PREP_SELECT="select=${DMA_NODES}:ncpus=${PPN}:mpiprocs=${PPN}${ACCEL_SEL}"

standJobRepl="s|\$PPN|${PPN}|g;s|\$MODULE_LOAD_COMMANDS|${LAMMPS_MODULES}\n${XLINK_MODULES}|"
standJobRepl="${standJobRepl};s|\$ACCEL|${ACCEL}|"
standJobRepl="${standJobRepl};s|\$ROOTDIR|${ROOTDIR}|g;s|\$POLYMERIZE|${POLYMERIZE_EXEC}|"
standJobRepl="${standJobRepl};s|\$LAMMPSEXEC|${LAMMPS_EXEC}|"

if [ -n ${ROOTDIR} ]; then
    echo "Root directory set as ${ROOTDIR}"
else
    echo "Root directory not set"
    exit 1
fi

if [[ -d ~/${ROOTDIR} ]]; then
    echo "~/${ROOTDIR} not empty, removing all files from directory"
    rm -rf ~/${ROOTDIR}
fi

# Create new directory
echo "Creating System Directory: ${ROOTDIR}"
mkdir -p ~/${ROOTDIR}

cp ./TEMPLATE/submit.csh ~/${ROOTDIR}

# COPYING MSI2LMP DIRECTORY ########################################################################
echo "Creating MSI2LMP subdirectory..."
mkdir ~/${ROOTDIR}/MSI2LMP
cp -r ./TEMPLATE/MSI2LMP/* ~/${ROOTDIR}/MSI2LMP/

# COPYING SCRIPTS DIRECTORY ########################################################################
echo "Creating SCRIPTS subdirectory..."
mkdir ~/${ROOTDIR}/SCRIPTS
cp -r ./TEMPLATE/SCRIPTS/* ~/${ROOTDIR}/SCRIPTS/
echo "Rewriting Makefiles for MSI2LMP and MSD..."
# overwrite MSI2LMP Makefile with proper compiler
sed -e "s|\$CXX_COMPILER|${CXX_COMPILER}|" ./TEMPLATE/SCRIPTS/msi2lmp/src/Makefile >\
    ~/${ROOTDIR}/SCRIPTS/msi2lmp/src/Makefile
sed -e "s|\$CXX_COMPILER|${CXX_COMPILER}|" ./TEMPLATE/SCRIPTS/msd/src/Makefile >\
    ~/${ROOTDIR}/SCRIPTS/msd/src/Makefile

# COPYING XL DIRECTORY #############################################################################
echo "Creating XL subdirectory..."
mkdir ~/${ROOTDIR}/XL/
cp ./TEMPLATE/XL/in.initial_equil ~/${ROOTDIR}/XL/
cp ./TEMPLATE/XL/in.equil ~/${ROOTDIR}/XL/
cp ./TEMPLATE/XL/in.anneal ~/${ROOTDIR}/XL/
# Calculate MPI_TOT for Xlinking
MPI_TOT=${PPN}
if (( ${ENABLE_GPU} == 1 )); then
  MPI_TOT=${GPU_MPI_PROCS}
elif (( ${ENABLE_MLA} == 1 )); then
  MPI_TOT=${MLA_MPI_PROCS}
fi
# create in.run
if [[ ${ARCH} == "CRAY" ]]; then
    replaceStr="s|\$LAMMPSEXEC|${LAMMPS_EXEC}|;s|\$PPN|${MPI_TOT}|;s|\$MACHINE_XLINK_CMD|"
    replaceStr="${replaceStr}aprun -n \$NUMPROCS \$LAMMPS_EXEC $ACCEL -in \$INFILE|"
    sed -e "${replaceStr}" ./TEMPLATE/XL/in.run > ~/${ROOTDIR}/XL/in.run
elif [[ ${ARCH} == "HPE" ]]; then
    replaceStr="s|\$LAMMPSEXEC|${LAMMPS_EXEC}|;s|\$PPN|${MPI_TOT}|;s|\$MACHINE_XLINK_CMD|"
    replaceStr="${replaceStr}mpiexec_mpt -np \$NUMPROCS \$LAMMPS_EXEC $ACCEL -in \$INFILE|"
    sed -e "${replaceStr}" ./TEMPLATE/XL/in.run > ~/${ROOTDIR}/XL/in.run
else
    replaceStr="s|\$LAMMPSEXEC|${LAMMPS_EXEC}|;s|\$PPN|${MPI_TOT}|;s|\$MACHINE_XLINK_CMD|"
    replaceStr="${replaceStr}mpirun -np \$NUMPROCS \$LAMMPS_EXEC $ACCEL -in \$INFILE|"
    sed -e "${replaceStr}" ./TEMPLATE/XL/in.run > ~/${ROOTDIR}/XL/in.run
fi
# create cibs_xl.js - xlinking only runs on 1 node
replaceStr="${standJobRepl};s|\$SELECT|${XLINK_SELECT}|;s|\$TOTAL_MPI|${MPI_TOT}|"
replaceStr="${replaceStr};s|\$QUEUE|${XLINK_QUEUE}|;s|\$WALLTIME|${XLINK_WT}|"
sed -e "${replaceStr}" ./TEMPLATE/XL/cibs_xl.js > ~/${ROOTDIR}/XL/cibs_xl.js


# COPYING ANNEAL DIRECTORY #########################################################################
echo "Creating ANNEAL subdirectory..."
mkdir ~/${ROOTDIR}/ANNEAL/
sed -e "s|\$NUMXLINKS|${NUM_XLINKS}|;s|\$POLYMERIZE|${POLYMERIZE_EXEC}|" \
        ./TEMPLATE/ANNEAL/in.cibs_equil > ~/${ROOTDIR}/ANNEAL/in.cibs_equil
MPI_TOT=$((${PPN}*${ANNEAL_NODES}))
if (( ${ENABLE_GPU} == 1 )); then
  MPI_TOT=${GPU_MPI_PROCS}
elif (( ${ENABLE_MLA} == 1 )); then
  MPI_TOT=${MLA_MPI_PROCS}
fi
replaceStr="${standJobRepl};s|\$NUMXLINKS|${NUM_XLINKS}|;s|\$TOTAL_MPI|${MPI_TOT}|"
replaceStr="${replaceStr};s|\$SELECT|${ANNEAL_SELECT}|"
replaceStr="${replaceStr};s|\$QUEUE|${ANNEAL_QUEUE}|;s|\$WALLTIME|${ANNEAL_WT}|"
sed -e "${replaceStr}" ./TEMPLATE/ANNEAL/cibs_anneal.js > ~/${ROOTDIR}/ANNEAL/cibs_anneal.js


# COPYING MSD DIRECTORY ############################################################################
echo "Creating MSD subdirectory..."
mkdir ~/${ROOTDIR}/MSD/
# no mods needed for in.cibs_equil
cp ./TEMPLATE/MSD/in.cibs_equil ~/${ROOTDIR}/MSD/
# copy calc_msd script
sed -e "s|\$ROOTDIR|${ROOTDIR}|;s|\$PPN|${PPN}|" \
        ./TEMPLATE/MSD/calc_msd.sh > ~/${ROOTDIR}/MSD/calc_msd.sh
# copy cibs_msd jobs script
MPI_TOT=$((${PPN}*${MSD_NODES}))
if (( ${ENABLE_GPU} == 1 )); then
  MPI_TOT=${GPU_MPI_PROCS}
elif (( ${ENABLE_MLA} == 1 )); then
  MPI_TOT=${MLA_MPI_PROCS}
fi
replaceStr="${standJobRepl};s|\$NUMXLINKS|${NUM_XLINKS}|;s|\$TOTAL_MPI|${MPI_TOT}|"
replaceStr="${replaceStr};s|\$SELECT|${MSD_SELECT}|"
replaceStr="${replaceStr};s|\$QUEUE|${MSD_QUEUE}|;s|\$WALLTIME|${MSD_WT}|"
sed -e "${replaceStr}" ./TEMPLATE/MSD/cibs_msd.js > ~/${ROOTDIR}/MSD/cibs_msd.js


# COPYING TEMP_DATAFILES DIRECTORY #################################################################
echo "Creating TEMP_DATAFILES subdirectory..."
mkdir ~/${ROOTDIR}/TEMP_DATAFILES/
cp ./TEMPLATE/TEMP_DATAFILES/in.cibs_temp ~/${ROOTDIR}/TEMP_DATAFILES/
MPI_TOT=$((${PPN}*${TEMP_NODES}))
replaceStr="${standJobRepl};s|\$NUMXLINKS|${NUM_XLINKS}|;s|\$TOTAL_MPI|${MPI_TOT}|"
replaceStr="${replaceStr};s|\$SELECT|${TEMP_SELECT}|"
replaceStr="${replaceStr};s|\$QUEUE|${TEMP_QUEUE}|;s|\$WALLTIME|${TEMP_WT}|"
sed -e "${replaceStr}" ./TEMPLATE/TEMP_DATAFILES/cibs_r1.js > ~/${ROOTDIR}/TEMP_DATAFILES/cibs_r1.js


# COPYING DMA_PREP DIRECTORY #######################################################################
echo "Creating DMA_PREP subdirectory..."
mkdir ~/${ROOTDIR}/DMA_PREP/
cp ./TEMPLATE/DMA_PREP/in.cibs_dma_prep ~/${ROOTDIR}/DMA_PREP/
cp ./TEMPLATE/DMA_PREP/get_next_param.py ~/${ROOTDIR}/DMA_PREP/
MPI_TOT=$((${PPN}*${DMA_NODES}))
for temp in $(seq 100 100 1500); do
    mkdir ~/${ROOTDIR}/DMA_PREP/${temp}/
    sedexpr="${standJobRepl};s|\$\$TEMP|${temp}|;s|\$\$TOTAL_MPI|${MPI_TOT}|"
    sed -e "${sedexpr}" ./TEMPLATE/DMA_PREP/run_params.sh > \
        ~/${ROOTDIR}/DMA_PREP/${temp}/run_params.sh
    replaceStr="${standJobRepl};s|\$TOTAL_MPI|${MPI_TOT}|"
    replaceStr="${replaceStr};s|\$SELECT|${DMA_PREP_SELECT}|;s|\$TEMP|${temp}|"
    replaceStr="${replaceStr};s|\$QUEUE|${DMA_PREP_QUEUE}|;s|\$WALLTIME|${DMA_PREP_WT}|"
    sed -e "${replaceStr}" ./TEMPLATE/DMA_PREP/cibs_r1.js > \
        ~/${ROOTDIR}/DMA_PREP/${temp}/cibs_r1.js
done


# PREPARATION ######################################################################################
echo "Compiling MSI2LMP"
cd ~/${ROOTDIR}/SCRIPTS/msi2lmp/src
make
echo "Compiling MSD Scripts"
cd ~/${ROOTDIR}/SCRIPTS/msd/src
make

echo "Running MSI2LMP in ~/${ROOTDIR}/MSI2LMP"
# run MSI2LMP on Car/MDF root files
cd ~/${ROOTDIR}/MSI2LMP/
cp ${CARMDF}.car .
cp ${CARMDF}.mdf .
../SCRIPTS/msi2lmp/src/msi2lmp.exe ${CARMDF} -class II -frc \
        ./pcff_iff_v1_6_CNT_poly_solv_update.frc -ignore > log.msi2lmp
../SCRIPTS/add_cibs_types.py ${CARMDF}.data xl2.data
echo "MSI2LMP Completed..."
echo "To batch-submit the entire job array, run \"source submit.csh\" from within ~/${ROOTDIR}"
