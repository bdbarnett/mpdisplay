#!/bin/env bash
# Copy packages to the micropython-lib directory
SOURCE_DIR=/home/brad/gh/pydisplay/src
DEST_DIR=/home/brad/gh/micropython-lib/micropython/pydisplay

# Copy all the directories in $SOURCE_DIR/lib except displaysys to $DEST_DIR/$package
# Copy any example files starting with the package name to $DEST_DIR/$package/examples
for package_dir in "$SOURCE_DIR/lib"/*; do
    package=$(basename $package_dir)
    if [ -d $package_dir ] && [ $(basename $package) != "displaysys" ]; then
        cp -r $package_dir $DEST_DIR/$package
        for full_example_path in $SOURCE_DIR/examples/$package*.py; do
            file=$(basename $full_example_path)
            cp $full_example_path $DEST_DIR/$package/examples/$file
        done
    fi
done

# Copy all the *.py files in $SOURCE_DIR/lib to $DEST_DIR/$package
# These modules don't have examples
for file in $SOURCE_DIR/lib/*.py; do
    package=$(basename $file .py)
    mkdir -p $DEST_DIR/$package
    cp $file $DEST_DIR/$package/
done

# Copy the children of displaysys to $DEST_DIR/displaysys/$module_name/displaysys
for module in "$SOURCE_DIR/lib/displaysys"/*; do
    if [ -d $module ]; then
        # It's a directory, like sdldisplay
        module_name=displaysys-$(basename $module)
    else
        # It's a file
        if [[ $(basename $module) == _* ]]; then
            # It's a file starting with _, like __init__.py
            module_name=displaysys
        else
            # It's a .py file, like busdisplay.py
            module_name=displaysys-$(basename $module .py)
        fi
    fi
    cp -r $module $DEST_DIR/displaysys/$module_name/displaysys/
    # if module_name is jndisplay, pgdisplay, psdisplay or sdldisplay, copy the example
    # $SOURCE_DIR/extras/board_config.py to $DEST_DIR/displaysys/displaysys-$module_name/examples
    if [[ $module_name == displaysys-jndisplay || $module_name == displaysys-pgdisplay || $module_name == displaysys-psdisplay || $module_name == displaysys-sdldisplay ]]; then
        cp $SOURCE_DIR/extras/board_config.py $DEST_DIR/displaysys/$module_name/examples/
    fi
done
