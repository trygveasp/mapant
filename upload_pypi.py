#!/usr/bin/env python3

import mapant
import os
import sys

repo = ""
if len(sys.argv) > 1:
    print("Test to testpypi")
    repo = "--repository-url https://test.pypi.org/legacy/"

ver = mapant.__version__

distfile = "dist/mapant-" + ver + ".tar.gz"
if os.path.exists(distfile):
    os.unlink(distfile)

cmd = "python3 setup.py sdist"
print(cmd)
ret = os.system(cmd)
if ret != 0:
    raise Exception

if os.path.exists(distfile):
    print("Upload " + distfile)
    cmd = "twine upload " + repo + " " + distfile
    print(cmd)
    ret = os.system(cmd)
    if ret != 0:
        raise Exception
else:
    raise FileNotFoundError(distfile)
