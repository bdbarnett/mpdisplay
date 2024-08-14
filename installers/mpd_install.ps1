# mpd_install.ps1

# Set the following variables to your desired paths
$REPO = "./gh"  # Path to clone repositories into
$TARGET = "./mp"  # Path to copy Python files

# Set to the executable you want to use for the test at the end of the script
$EXE = "python3"  # micropython, python3 or python

$BOARD_CONFIG = "displays/board_configs/desktop/board_config.py"  # with .py extension
$LAUNCH = "paint"  # without .py extension

# If $REPO directory does not exist, create it
if (!(Test-Path -Path $REPO)) {
    New-Item -ItemType Directory -Path $REPO
}

# Clone the repositories. This will error if the repositories already exist.
git clone https://github.com/bdbarnett/displays.git $REPO/displays
git clone https://github.com/bdbarnett/lcd_bus.git $REPO/lcd_bus
git clone https://github.com/bdbarnett/timer.git $REPO/timer
git clone https://github.com/bdbarnett/console.git $REPO/console
git clone https://github.com/bdbarnett/playing_cards.git $REPO/playing_cards
git clone https://github.com/bdbarnett/testris.git $REPO/testris
git clone https://github.com/peterhinch/micropython-touch.git $REPO/micropython-touch
git clone https://github.com/adafruit/Adafruit_CircuitPython_Ticks $REPO/Adafruit_CircuitPython_Ticks

# If $TARGET directory does not exist, create it
if (!(Test-Path -Path $TARGET)) {
    New-Item -ItemType Directory -Path $TARGET
}

# Stage the files in $TARGET
Copy-Item -Path $REPO/$BOARD_CONFIG -Destination $TARGET/ -Force

Copy-Item -Path $REPO/displays/lib -Destination $TARGET/ -Recurse -Force
Copy-Item -Path $REPO/displays/fonts -Destination $TARGET/ -Recurse -Force
Copy-Item -Path $REPO/displays/examples -Destination $TARGET/ -Recurse -Force
Copy-Item -Path $REPO/displays/extras/* -Destination $TARGET/lib/ -Force
Copy-Item -Path $REPO/displays/app_configs/* -Destination $TARGET/ -Force

Copy-Item -Path $REPO/lcd_bus/lcd_bus -Destination $TARGET/lib/ -Recurse -Force

Copy-Item -Path $REPO/timer/timer -Destination $TARGET/lib/ -Recurse -Force
Copy-Item -Path $REPO/timer/examples -Destination $TARGET/ -Recurse -Force

Copy-Item -Path $REPO/console/console.py -Destination $TARGET/lib/ -Force
Copy-Item -Path $REPO/console/examples -Destination $TARGET/ -Recurse -Force

Copy-Item -Path $REPO/playing_cards/playing_cards.py -Destination $TARGET/lib/ -Force
Copy-Item -Path $REPO/playing_cards/examples -Destination $TARGET/ -Recurse -Force

Copy-Item -Path $REPO/testris/testris.py -Destination $TARGET/examples/ -Force

Copy-Item -Path $REPO/micropython-touch/gui -Destination $TARGET/ -Recurse -Force

Copy-Item -Path $REPO/Adafruit_CircuitPython_Ticks/adafruit_ticks.py -Destination $TARGET/lib/ -Force

# Launch the test app
Write-Host "`nInstallation complete.  To run the '$LAUNCH' example, type the following:"
Write-Host "`ncd $TARGET"
Write-Host "$EXE -i path.py"
Write-Host "import $LAUNCH"
Write-Host "`n"