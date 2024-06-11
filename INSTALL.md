# Installing MPDisplay

A full installation of MPDisplay, required libraries for specific platforms, and recommended optional libraries to get started is provided by the following methods.

## Prerequisites:
- There are no prerequisites for MicroPython or CircuitPython on microcontrollers
- For MicroPython or CPython on Unix / Linux / ChromeOS / Single Board Computers, install SDL2 and Pygame:
```
sudo apt update && sudo apt upgrade
sudo apt install libsdl2-2.0-0
sudo apt install python3-pygame
```
- For CPython on Windows, install SDL2 and Pygame:
    - Save the `SDL2.dll` file extracted from `SDL2-2.??.?-win32-x??.zip` downloaded from [SDL Releases](https://github.com/libsdl-org/SDL/releases/) to your `C:\Windows\System32\` directory
    - install Pygame by entering `pip install pygame` or `pip3 install pygame` at the Command Prompt
- Although I have not tested this yet, you should be able to use SPI and I2C LCDs on single board computers (SBC) such as the Raspberry Pi 4 and 5 by installing [Adafruit Blinka DisplayIO](https://github.com/adafruit/Adafruit_Blinka_Displayio).  Note, if you are using an HDMI display on an SBC, see the requirements for CPython on Unix / Linux above instead.

Note, MPDisplay attempts to use SDL2 before Pygame.  If both are installed and you want to force it to use Pygame, set the environment variable `MPDisplay=PGDisplay`.  I found this necessary on my Chromebook because SDL2 doesn't behave the same way on it for some reason.  To do that in bash:
```
export MPDisplay=PGDisplay
```
To do that in Windows:
```
set MPDisplay=PGDisplay
```

## For MicroPython on Unix / Linux or wifi capable microntrollers

### To connect your microcontroller to wifi:

Copy [wifi.py](utils/wifi.py) from the [utils](utils) directory and save it in the `lib` directory of your microcontroller.  Type the following at the REPL (or add it to your boot.py) to connect:

```
import wifi
wlan = wifi.connect("YOURSSID", "YOURPASSWORD")
```

### Once your microcontroller is connected to wifi, or for MicroPython on Unix / Linux

Note, MIP and it's dependencies must be "frozen" into your MicroPython executable or firmware.  It is by default, but some packages, such as the MicroPython package in Ubuntu 24.04 LTS, do not include MIP.

At the REPL, type:

```
import mip
mip.install("github:bdbarnett/mpdisplay/mpd_install.json", target=".")
```

As an alternative, you may save [mpd_install.py](mpd_install.py) from the root of the repository to your board, edit it to install only the libraries you want, and simply type:

```
import mpd_install.py
```

## For CPython on Unix / Linux

You can use this method to download MPDisplay for use in CPython, but may also use it to stage files to upload to your microcontroller later using your preferred method, which may be mpremote, Thonny, or something else.

The [mpd_install.sh](mpd_install.sh) bash script will clone all repositories to a directory specified by REPO (default is `~/gh/`) and then stage the required files from those repos into the directory specified by TARGET (default is `~/mp/`).  To download the file, at the bash prompt type:

```
wget https://raw.githubusercontent.com/bdbarnett/mpdisplay/main/mpd_install.sh
```

Edit `mpd_install.sh` to set the REPO and TARGET directories to your preferred locations.  Then make the file executable and run it by typing the following at the bash prompt:

```
chmod u+x mpd_install.sh
./mpd_install.sh
```

## For CPython on Windows

There is no native installer for Windows, but the above directions for CPython on Unix / Linux work under Windows Subsytem for Linux (WSL).  I recommended you get Ubuntu 24.04 LTS (the latest release) from the [Microsoft Store](https://apps.microsoft.com/detail/9nz3klhxdjp5).  You may simply download the files under WSL and then copy / move them to a directory visible to the Command Prompt.  Instead, I create a `mp` directory in my my Windows user profile directory, then create a symbolic link to it in my Linux home directory.  My Windows username is brad, so I type the following at the bash prompt before running the `mpd_install.sh` script in WSL:

```
mkdir /mnt/c/Users/brad/mp
ln -s /mnt/c/Users/brad/mp/ ~/
```

After performing the directions under CPython on Unix, in WSL I can:
```
cd ~/mp
python3 -i path.py  # or python -i path.py or micropython -i path.py
```

At a Windows Command Prompt, I type:
```
cd c:\Users\brad\mp
python -i path.py  # or python3 -i path.py
```

## For CircuitPython

Currently, there isn't an installer for CircuitPython, but I may create one using `circup` in the future.  Stage the files to you your home directory using the CPython on Unix / Linux method above, then copy them to your board like you normally would.  It may be easier for you if you use the symbolic link to stage the files in your Windows user profile as mentioned above in CPython on Windows.
