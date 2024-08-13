"""
path.py
To run this command when you launch *Python, type the following, substituting 'python' with the name
of your *Python executable, such as 'python3' or 'micropython':

    python -i path.py

On microcontrollers, you may include it in your boot.py, main.py or code.py, whichever is appropriate:
    
    import path

Edit the 'directories' tuple to include the directories you want to add to the path.
Only directories that already exist on the filesystem will be added to the path.
Does not work for nested directories.
"""

def update():
    # Edit this list to include the directories you want to add to the path.
    directories = ('lib', 'extras', 'examples', 'app_configs')

    import sys
    import os

    # get the path this module is in
    cwd = __file__.split("/")[0:-1]
    cwd = "/".join(font_dir)

    # Get a list of directories on the filesystem.
    if hasattr(os, 'listdir'):
        dirlist = os.listdir()
    else:
        dirlist = [x[0] for x in os.ilistdir()]

    # Check to see if each directory is on the filesystem and if so, add it to the path.
    completed = []
    for directory in directories:
        if directory in dirlist and (d := "/".join([cwd, directory})) not in sys.path:
            sys.path.append(d)
            completed.append(d)

    if completed:
        print(f'path.py:  Added {completed} to sys.path.\n')

update()
