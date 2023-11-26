Currently, lv_micropython will not compile for ESP32S3 targets.  Replace micropython/lib/lv_bindings/mkrules.cmake file with the one from this directory.  That will will remove all dependencies on ESP for the LVGL bindings, and you can compile as usual.

If I receive community support for this change, I will submit a pull request to make the change in lv_micropython_bindings permanently.
