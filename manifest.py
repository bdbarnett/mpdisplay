# Custom manifest.py file
#
# Available variables:
    # $(MPY_DIR) - path to the micropython repo.
    # $(MPY_LIB_DIR) - path to the micropython-lib submodule. Prefer to use require().
    # $(PORT_DIR) - path to the current port (e.g. ports/stm32)
    # $(BOARD_DIR) - path to the current board (e.g. ports/stm32/boards/PYBV11)
#
# Available functions:
    # add_library(library, library_path, prepend=False) - for example: add_library("micropython-lib", "$(MPY_DIR)/lib")
    # package(package_path, files=None, base_path='.', opt=None) - multiple files, usually with __init__.py
    # module(module_path, base_path='.', opt=None)  - single file
    # require(name, library=None) - from a library
    # include(manifest_path) - include another manifest file
    # metadata(description=None, version=None, license=None, author=None)
#


import os
if os.path.exists(os.path.join("$(BOARD_DIR)", "manifest.py")):
    include("$(BOARD_DIR)/manifest.py") # type: ignore  # noqa: F821
else:
    include("$(PORT_DIR)/boards/manifest.py") # type: ignore  # noqa: F821
