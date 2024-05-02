import sys


### Change the path below to the path to your *Python lib folder.
### To run this command when you run Python, type:
###
###     python -i path.py
if not 'lib' in sys.path:
    sys.path.append('lib')
sys.path.extend(['drivers', 'romfonts', 'examples'])
