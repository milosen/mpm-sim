#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

mkdir -p jemris
cd jemris
JEMRIS_PREFIX=$(realpath .)

JEMRIS_REPO="https://github.com/JEMRIS/jemris.git"
JEMRIS_TAG="v2.8.3"

CLN_REPO="git://www.ginac.de/cln.git"
CLN_TAG="cln_1-3-4"

GINAC_REPO="git://www.ginac.de/ginac.git"
GINAC_TAG="release_1-7-4"

XERCES_REPO="https://github.com/apache/xerces-c.git"
XERCES_TAG="v3.2.3"

SUNDIALS_REPO="https://github.com/LLNL/sundials.git"
SUNDIALS_TAG="v2.7.0"

NTHREADS=$(nproc)

module purge
module load git cmake gcc openmpi hdf5-serial boost autoconf automake libtool pkg-config

[ ! -d git_cln ] && git clone --depth 1 --branch "$CLN_TAG" "$CLN_REPO" git_cln
cd git_cln
autoreconf -iv
./configure --prefix="$JEMRIS_PREFIX"
make MAKEINFO=true -j $NTHREADS
make MAKEINFO=true -j $NTHREADS check
make MAKEINFO=true install
cd "$JEMRIS_PREFIX"

[ ! -d git_ginac ] && git clone --depth 1 --branch "$GINAC_TAG" "$GINAC_REPO" git_ginac
cd git_ginac
autoreconf -i
CLN_LIBS="-L\"$JEMRIS_PREFIX/lib\" -lcln" CLN_CFLAGS="-I\"$JEMRIS_PREFIX/include\"" ./configure --prefix="$JEMRIS_PREFIX"
make MAKEINFO=true -j $NTHREADS
make MAKEINFO=true -j $NTHREADS check
make MAKEINFO=true install
cd "$JEMRIS_PREFIX"

[ ! -d git_xerces ] && git clone --depth 1 --branch "$XERCES_TAG" "$XERCES_REPO" git_xerces
cmake -S git_xerces -B git_xerces/build -DCMAKE_PREFIX_PATH="$JEMRIS_PREFIX" -DCMAKE_INSTALL_PREFIX="$JEMRIS_PREFIX"
cmake --build git_xerces/build -j $NTHREADS
cmake --build git_xerces/build --target test -j $NTHREADS # potentially ctest is the better option
cmake --build git_xerces/build --target install

[ ! -d git_sundials ] && git clone --depth 1 --branch "$SUNDIALS_TAG" "$SUNDIALS_REPO" git_sundials
cmake -S git_sundials -B git_sundials/build -DCMAKE_PREFIX_PATH="$JEMRIS_PREFIX" -DCMAKE_INSTALL_PREFIX="$JEMRIS_PREFIX"
cmake --build git_sundials/build -j $NTHREADS
cmake --build git_sundials/build --target install

[ ! -d git_jemris ] && git clone --depth 1 --branch "$JEMRIS_TAG" "$JEMRIS_REPO" git_jemris
PKG_CONFIG_PATH="$JEMRIS_PREFIX/lib/pkgconfig" cmake -S git_jemris -B git_jemris/build -DCMAKE_PREFIX_PATH="$JEMRIS_PREFIX" -DCMAKE_INSTALL_PREFIX="$JEMRIS_PREFIX"
cmake --build git_jemris/build -j $NTHREADS
cmake --build git_jemris/build --target install

