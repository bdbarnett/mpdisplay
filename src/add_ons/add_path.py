"""
Determines which directory this file is in and adds it to the path if it is not already there.

Leave it named 'path.py' and place it in the directory you want to add to the path, then run it.
For example, save it in "examples" and run it with the following command:
    import examples.path

You may add the contents to an __init__.py file in the directory if you prefer.  Then run it with:
    import examples
"""
import os
import sys


# Set to True to use relative paths instead of absolute paths.
RELPATH = True

directory, file = __file__.rsplit("/", 1)
if RELPATH:
    cwd = os.getcwd()
    if cwd[-1] != "/":
        cwd += "/"
    directory = directory.split(cwd, 1)[-1]

if directory not in sys.path:
    sys.path.append(directory)
    print(f"{file}:  Added '{directory}' to sys.path.")
