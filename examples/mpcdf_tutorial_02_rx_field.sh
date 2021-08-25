#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# I assume at this point, that you have already executed the first tutorial script.
module load anaconda datashare
source activate mpm-sim

# Start the receive coil array by specifying magnitude and phase of the first coil in the form of nifti files.
# The flag makes sure that any old rx coil array file is completely overwritten instead of appended to.
mpm-sim prepare-rx-field --overwrite -x 200 201 data/sensmaps/Coils_ch1_Magnitude.nii data/sensmaps/Coils_ch1_Phase.nii runs/example_1

# This part can be placed into a for-loop. The overwrite flag must be ommited now to append the new coils to the coil
# array file in runs/example_1.
mpm-sim prepare-rx-field -x 200 201 data/sensmaps/Coils_ch1_Magnitude.nii data/sensmaps/Coils_ch1_Phase.nii runs/example_1
