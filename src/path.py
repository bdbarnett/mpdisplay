"""
path.py
To run this command when you launch *Python, type the following, substituting 'python' with the name
of your *Python executable, such as 'python3' or 'micropython':

    python -i path.py

On microcontrollers, you may include it in your boot.py, main.py or code.py, whichever is appropriate:
    
    import path

Edit the 'directories' tuple to include the directories you want to add to the path.
Only directories that already exist in the current working directory will be added to the path.
"""

# Edit this list to include the directories you want to add to the path.
directories = ["lib", "extras", "examples", "drivers", "configs", "lib/displays", "lib/buses"]

def update():

    import sys
    import os

    def find_dir(directory):
        try:
            os.stat(directory)
            return True
        except OSError:
            return False

    cwd = os.getcwd()
    if cwd[-1] != "/":
        cwd += "/"

    added = []
    for directory in directories:
        full_path = cwd + directory
        if find_dir(full_path):
            if full_path not in sys.path:
                sys.path.append(full_path)
                added.append(full_path)

    if added:
        print(f"path.py:  Added {added} to sys.path.")


def add(directory):
    directories.append(directory)
    update()

update()
