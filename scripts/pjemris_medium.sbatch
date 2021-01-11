#!/bin/bash -l
# Standard output and error:
#SBATCH -o ./pjemris.out.%j
#SBATCH -e ./pjemris.err.%j
# Initial working directory:
#SBATCH -D ./
# Job Name:
#SBATCH -J pjemris
#
# Number of nodes and MPI tasks per node:
#SBATCH --nodes=10
#SBATCH --ntasks-per-node=40
#
#SBATCH --mail-type=all
#SBATCH --mail-user=%u@cbs.mpg.de
#
# Wall clock limit:
#SBATCH --time=24:00:00

# Run the program:
srun ../../../build/src/pjemris simu.xml &> pjemris.out
