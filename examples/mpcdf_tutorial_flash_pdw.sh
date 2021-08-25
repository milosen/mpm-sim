#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

module load anaconda datashare
source activate mpm-sim

# Its practical to have a simulations directory, I suggest calling it runs/ as this name is already ignored by git.
mkdir -p runs

[ ! -d data ] && ds get jemris/data.zip && unzip data.zip

# Create a new simulation named example_1 in the runs directory and use data/segmentation.nii as the ground-truth
# sample. Interpolate the sample with a factor of 2, i.e. create a total of 8 spins per voxel, and select slice 200
# in the x direction. Run mpm-sim init --help for more information on the usage of mpm-sim init.
mpm-sim init runs/example_1 data/segmentation.nii -i 2 -x 200 201

# We also need rx and tx coil files as well as the sequence definition file. Choose the PDw FLASH sequence with
# controlled zeroing of the transverse magnetization for perfect spoiling
cp examples/pdw_null/* runs/example_1

# Jemris assumes that the current working directory is also the working directory of the simulation. So, we cd into the
# prepared simulation directory and invoke the batch script from here.
cd runs/example_1 || exit
sbatch ../../scripts/pjemris.sbatch
