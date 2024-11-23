"""
Custom manifest.py file to include packages from pydisplay

To include this file with your MicroPython build, add the following line to your
make command, replacing the path with the correct path to this file:
    FROZEN_MANIFEST=$(MPY_DIR)/../pydisplay/manifest.py

Available variables:
    $(MPY_DIR)  #  path to the micropython repo.
    $(MPY_LIB_DIR)  #  path to the micropython-lib submodule. Prefer to use require().
    $(PORT_DIR)  #  path to the current port (e.g. ports/stm32)
    $(BOARD_DIR)  #  path to the current board (e.g. ports/stm32/boards/PYBV11)

Available functions:
    add_library(library, library_path, prepend=False)  #  for example: add_library("micropython-lib", "$(MPY_DIR)/lib")
    package(package_path, files=None, base_path='.', opt=None)  #  multiple files, usually with __init__.py
    module(module_path, base_path='.', opt=None)  #  single file
    require(name, library=None)  #  from a library
    include(manifest_path)  #  include another manifest file
    metadata(description=None, version=None, license=None, author=None)

"""
# This file is to be given as
#     make FROZEN_MANIFEST=../../../../../../pydisplay/manifest.py

import os

if 0:
    def include(*args, **kwargs):
        pass
    def package(*args, **kwargs):
        pass
    def module(*args, **kwargs):
        pass

if os.path.exists(os.path.join("$(BOARD_DIR)", "manifest.py")):
    include("$(BOARD_DIR)/manifest.py")
else:
    include("$(PORT_DIR)/boards/manifest.py")

package("displaysys", files=None, base_path="./src/lib", opt=None)
package("eventsys", files=None, base_path="./src/lib", opt=None)
package("displaybuf", files=None, base_path="./src/lib", opt=None)
package("graphics", files=None, base_path="./src/lib", opt=None)
package("palettes", files=None, base_path="./src/lib", opt=None)
package("timer", files=None, base_path="./src/lib", opt=None)
module("touch_keypad.py", base_path="./src/extras")
module("wifi.py", base_path="./src/extras")
