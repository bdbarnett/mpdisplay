#!/bin/env bash
# Copy packages to the micropython-lib directory

SOURCE_DIR=~/gh/pydisplay/src
DEST_DIR=~/gh/micropython-lib/micropython/pydisplay

# Copy all the directories in $SOURCE_DIR/lib except displaysys to $DEST_DIR/$package
# Copy any example files starting with the package name to $DEST_DIR/$package/examples
for package_dir in "$SOURCE_DIR/lib"/*; do
    package=$(basename $package_dir)
    if [ -d $package_dir ] && [ $(basename $package) != "displaysys" ]; then
        mkdir -p $DEST_DIR/$package/examples
        cp -r $package_dir $DEST_DIR/$package/
        cp $SOURCE_DIR/examples/$package*.py $DEST_DIR/$package/examples/
        # write the following text to $DEST_DIR/$package/manifest.py
        cat <<EOF > $DEST_DIR/$package/manifest.py
metadata(
    description="$package",
    version="0.1.0",
    pypi_publish="pydisplay-$package",
)
package("$package")
EOF
    fi
done

# Copy the children of displaysys to $DEST_DIR/displaysys/$package/displaysys
for module in "$SOURCE_DIR/lib/displaysys"/*; do
    if [[ $(basename $module) == __init__.py ]]; then
        package=displaysys
    else
        package=displaysys-$(basename $module .py)
    fi
    mkdir -p $DEST_DIR/displaysys/$package/displaysys
    cp -r $module $DEST_DIR/displaysys/$package/displaysys/
    # if package is jndisplay, pgdisplay, psdisplay or sdldisplay, copy the example
    # $SOURCE_DIR/extras/board_config.py to $DEST_DIR/displaysys/displaysys-$package/examples
    mkdir -p $DEST_DIR/displaysys/$package/examples
    if [[ $package == displaysys ]]; then
        cat <<EOF > $DEST_DIR/displaysys/$package/manifest.py
metadata(
    description="$package",
    version="0.1.0",
    pypi_publish="pydisplay-$package",
)
package("displaysys")
EOF
        cp $SOURCE_DIR/examples/$package*.py $DEST_DIR/displaysys/$package/examples/
    else
        cat <<EOF > $DEST_DIR/displaysys/$package/manifest.py
metadata(
    description="$package",
    version="0.1.0",
    pypi_publish="pydisplay-$package",
)
require("displaysys")
package("displaysys")
EOF
        if [[ $package == displaysys-busdisplay ]]; then
            cp $SOURCE_DIR/../board_configs/busdisplay/i80/wt32sc01-plus/board_config.py $DEST_DIR/displaysys/$package/examples/
        else
            if [[ $package == displaysys-fbdisplay ]]; then
                cp $SOURCE_DIR/../board_configs/fbdisplay/qualia_tl040hds20/board_config.py $DEST_DIR/displaysys/$package/examples/
            else
                cp $SOURCE_DIR/extras/board_config.py $DEST_DIR/displaysys/$package/examples/
            fi
        fi
    fi
done
