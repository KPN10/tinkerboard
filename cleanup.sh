#!/bin/bash

find .\
    -type f\
    \(\
    ! -name "*.sh"\
    ! -name "*.md"\
    ! -name "*.py"\
    ! -name "*.c"\
    ! -path "*git*"\
    \)\
    -print\
    -delete