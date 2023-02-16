#!/usr/bin/env texlua


maindir = os.getenv('SOURCE') .. '/class'
unpackdir = os.getenv('BUILD') .. '/unpack'
localdir = os.getenv('BUILD')
lfs.chdir(maindir)
dofile('./build.lua')
