#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# I assume at this point, that you have already executed the first tutorial script.
module load anaconda datashare
source activate mpm-sim

# The receive coil array is initialized by specifying magnitude and phase fields of the first coil in the form of nifti
# files. The overwrite flag makes sure that any old rx coil array file is completely overwritten instead of appended to.
mpm-sim prepare-rx-field --overwrite -x 200 201 data/sensmaps/Coils_ch1_Magnitude.nii data/sensmaps/Coils_ch1_Phase.nii runs/example_1

# This part can be placed into e.g. a for-loop to loop over the coils and their ground truth rx-fields and to add them
# to the coil array. The overwrite flag must be ommited to append each new coil to the coil array file in runs/example_1.
mpm-sim prepare-rx-field -x 200 201 data/sensmaps/Coils_ch2_Magnitude.nii data/sensmaps/Coils_ch2_Phase.nii runs/example_1
