#!/usr/bin/env python

import gzip
import os

thisdir = os.path.abspath('.')
lines = []
for fname in os.listdir(thisdir):
    fpath = os.path.join(thisdir, fname)
    if os.path.isdir(fpath) and 'dt=' in fname:
        fnames = os.listdir(fpath)
        for ffname in fnames:
            ffpath = os.path.join(fpath, ffname)
            with gzip.open(ffpath) as f:
                lines.extend(f.readlines())

s = ' Rate Limits: '
min_n = {}
for line in lines:
    line = str(line)
    j = line.find(s)
    if j >= 0:
        j0 = line.rfind(' ', 0, j) + 1
        kind = line[j0:j]

        if kind not in min_n:
            min_n[kind] = 10000

        j1 = j + len(s)
        j2 = line.find(' ', j1)
        n = int(line[j1:j2])

        if n < min_n[kind]:
            min_n[kind] = n

print(min_n)
