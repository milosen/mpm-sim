# Jemris MPM utils
Utility scripts for working with multi-parameter maps in [Jemris](https://github.com/JEMRIS/jemris). The most important tool is `mpm-sim sample`, which prepares a phantom for simulation.

## Build Jemris
Chances are you have to build Jemris from source. You can do so by using cmake, but you need to have the dependencies installed. At the institute, jemris is known to work on `maki` and `manati`, and the dependencies are already installed there. To build jemris, execute the following lines individually in your terminal at the machine you want to use:
```shell
# clone git repository
git clone git@github.com:JEMRIS/jemris.git
# create build directory (e.g. in ./jemris_build)
mkdir jemris/build && cd jemris/build
# prepare build configuration files with cmake
cmake ..
# build the software with make
make
```
You'll find the executables at `jemris/build/src/jemris` and `jemris/build/src/pjemris`.

### Local Linux (e.g. Ubuntu at the institute)
If you can install libraries via a package manager, than you need to install the following packages (these exact names are for Ubuntu):
```shell
apt-get install \
libhdf5-dev \
libxerces-c-dev \
libsundials-dev \
libopenmpi-dev \
libboost-all-dev \
libginac-dev 
```

### MPCDF cobra
For the MPCDF in Garching, you can execute the script in `scripts/mpcdf_build_jemris.sh`, e.g. in an interactive run on an interactive node with `ssh cobra-i`:
```shell
srun -p interactive -n 1 ./scripts/mpcdf_build_jemris.sh
```
It will build jemris and it's dependencies from source. You can find the executables in `jemris/build/src/` or `jemris/bin/`.

## Install utilities
You will need other python packages to be able to use this software. You can take a look at `environment.yml` or `requirements.txt` in the root directory of this project, if you want to install them manually, but I recommend using an environment manager instead (e.g. [miniconda 3](https://docs.conda.io/en/latest/miniconda.html)). 

With `conda`, installing dependencies is as simple as:
```shell
conda env create --file environment.yml
```
Now activate the environment
```shell
conda activate jemris
```
and install the mpm tools themselves:
```shell
pip install -e .
```

## Usage
The main interface is called `mpm-sim` and it has the following commands:
```shell
$ mpm-sim
Usage: mpm-sim [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  basic-flash-recon  Run a basic flash reconstruction.
  sample             Prepare a sample for simulation
  sensmap            Prepare sensitivity maps for simulation
```
You can also get help messages for the individual programs, e.g. with `mpm-sim sample --help`.

### Creating a sample
You need to provide jemris with a ground-truth mpm for it to have all the physiological parameters available. The command `mpm-sim sample` helps with creating one from a label map.
```shell
$ mpm-sim sample --help
Usage: mpm-sim sample [OPTIONS] SEG_PATH

  Prepare a sample for simulation

Options:
  --sample_name SAMPLE_NAME
  -o, --out_dir PATH              output directory
  -i, --interpolation INTERP_FACTOR
                                  multiply number of spin by this factor on
                                  each axis using nearest neighbor
                                  interpolation

  -x, --xslice X_SLICE            slicing in x direction
  -y, --yslice Y_SLICE            slicing in y direction
  -z, --zslice Z_SLICE            slicing in z direction
  --help                          Show this message and exit.
```
It takes in a tissue label map and returns a jemris readable `hdf5` file containing an mpm with looked up parameters. You can find an example of a label map at `test/data/segmentation.nii`. Currently, the tool only reads nifty files.

You can also specify a python-type slicing of the 3d volume and an interpolation factor for nearest neighbor interpolation of the voxels. The interpolation is necessary to increase the number of spins per voxel, but choose the factor wisely. The factor is dimension-wise, so a factor of `-i 5` means that you will have 5^3 = 125 spins per voxel. Both, slicing and interpolation, will be applied before the mpm lookup.

The final command might look something like this:
```shell
mpm-sim sample test/data/segmentation.nii -x 200 201 -i 2
```
### Creating a sensitivity map
This is a work in progress.

