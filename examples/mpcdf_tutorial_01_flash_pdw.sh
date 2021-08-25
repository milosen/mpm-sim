#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

module load anaconda datashare

# It's practical to have a simulations directory. I suggest calling it runs/ as this name is already ignored by git.
mkdir -p runs

# It's ensured that the data/ directory (which holds the ground-truth data) exists. The ds get command operates on your
# personal datashare. So, make sure the path exists or change it.
[ ! -d data ] && ds get jemris/data.zip && unzip data.zip

# This software (mpm-sim) is installed.
source activate mpm-sim && pip install -e .
# I assume you have already installed the environment as described in the readme. If
# not, execute:
# module load anaconda && conda env create --file environment.yml
# ... and try again

# A new simulation named example_1 is created in the runs directory and data/segmentation.nii is used as the ground-truth
# sample. The sample is interpolated with a factor of 2, i.e. a total of 8 spins per voxel, and the sample is sliced
# in the x direction at position 200 with thickness 1.
# Run mpm-sim init --help for more information on the usage of mpm-sim init.
mpm-sim init runs/example_1 data/segmentation.nii -i 2 -x 200 201

# Also rx and tx coil files are needed, as well as the sequence definition file. The PDw FLASH sequence with
# controlled zeroing of the transverse magnetization is chosen for emulating perfect spoiling.
cp examples/pdw_null/* runs/example_1

# Jemris assumes that the current working directory is also the working directory of the simulation.
# So, we cd into the prepared simulation directory and invoke the batch script from here. Also, it's easier to output
# the logfile of the batch system here to have everything regarding a single simulation in a single enclosed directory.
cd runs/example_1 || exit
sbatch ../../scripts/pjemris.sbatch
