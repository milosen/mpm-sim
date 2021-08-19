# MPM simulations with JEMRIS
This repository contains helper programs for simulating acquisitions of multi-parameter maps using the [Jemris](https://github.com/JEMRIS/jemris) [1] simulator.

## Links
* Jemris Documentation: http://www.jemris.org/ug_userguide.html
* Jemris Discussion Group: https://groups.google.com/g/jemris?pli=1

## Installation
You will need other python packages to be able to use this software. 
If you want to install them manually, you can take a look at `environment.yml` or `requirements.txt` in the root directory of this project; 
but I recommend using [anaconda](https://docs.conda.io/en/latest/miniconda.html) instead. 

With anaconda, installing dependencies is as simple as:
```shell
conda env create --file environment.yml
```
Now activate the environment
```shell
conda activate jemris
```
and install this repository
```shell
pip install -e .
```

## Usage
The main interface is called `mpm-sim` and it has sub-commands with their own help messages.
For example, run `mpm-sim sample --help` for the sample utility.
A complete list of all commands will be displayed when you try to execute `mpm-sim` without further specifications or run `mpm-sim --help`.

To run simulations, you will need the Jemris simulator. 
Please refer to later sections on how to build Jemris.

### Initializing a simulation
You need to provide a ground-truth multi-parametric map for simulation. 
The command `mpm-sim init` helps with creating one from a tissue map (segmentation) and configures a single simulation run.

You can specify a python-type slicing of the 3d volume and an interpolation factor for nearest neighbor interpolation of the voxels. 
The interpolation is necessary to increase the number of spins per voxel, but choose the factor wisely. The factor is dimension-wise, so a factor of `-i 5` means that you will have 5^3 = 125 spins per voxel. 
Both, slicing and interpolation, will be applied before the mpm lookup.

The final command might look something like this:
```shell
mpm-sim init data/segmentation.nii -x 200 201 -i 2
```

Unfortunately, the script does not generate jemris sequences and RX/TX coil configurations for you.
You can copy them from one of the examples in the `examples/` directory.
For MPM simulations, I suggest starting with a 

### Creating a sensitivity map
This is a work in progress.

## Build Jemris
Chances are you have to build Jemris from source. You can do so by using cmake, but you need to have the dependencies installed. 
At the MPI CBS, Jemris is known to work on `maki` and `manati`, and the dependencies are already installed there. 
To build jemris, execute the following lines individually in your terminal at the machine you want to use:
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

### Install Dependencies on Linux (e.g. Ubuntu at the institute)
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

### Install Dependencies on MPCDF cobra
For the MPCDF in Garching, you can execute the script in `scripts/mpcdf_build_jemris.sh`, e.g. in an interactive run. 
```shell
srun -p interactive -n 1 ./scripts/mpcdf_build_jemris.sh
```
(To login on an interactive node you can type `ssh cobra-i`).
The script will build Jemris and it's dependencies from source. 
You can find the executables in `jemris/build/src/` or `jemris/bin/`.

## References
[1] Stöcker, T., Vahedipour, K., Pflugfelder, D. and Shah, N.J. (2010), High-performance computing MRI simulations. Magn. Reson. Med., 64: 186-193. https://doi.org/10.1002/mrm.22406
