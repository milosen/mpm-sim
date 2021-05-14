#!/bin/bash

function build_jemris() {
	local JEMRIS_PREFIX="$1"
	PKG_CONFIG_PATH="$JEMRIS_PREFIX/lib/pkgconfig" cmake -S "$JEMRIS_PREFIX/git_jemris" -B "$JEMRIS_PREFIX/git_jemris/build" -DCMAKE_PREFIX_PATH="$JEMRIS_PREFIX" -DCMAKE_INSTALL_PREFIX="$JEMRIS_PREFIX"
	cmake --build "$JEMRIS_PREFIX/git_jemris/build" -j $NTHREADS
	cmake --build "$JEMRIS_PREFIX/git_jemris/build" --target install	
}

