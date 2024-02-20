Compiling and testing MicroPython & MicroPyton_SDL2
===================================================
The following is my method of compiling and testing MPDisplay with [mp_lcd_bus](https://github.com/kdschlosser/mp_lcd_bus) for Linux.  I use Ubuntu under Windows Subsystem for Linux (WSL).  Your method will be different if you have a different build environment.  This is not a full tutorial.  I documented it for my own reference and decided to post it online in case it my be useful to someone else.  See the official directions on the [MicroPython repository](https://github.com/micropython/micropython/tree/master/ports/esp32).  There are several Linux packages that will need to be installed beforehand using `sudo apt install`.  

Download repos and build the executable
---------------------------------------
At the bash prompt:
```
# I put all Github repositories in the "gh" directory.  Use your preferred directory.
cd ~
mkdir gh
cd gh

# Clone the MicroPyton_SDL2 repository
git clone https://github.com/russhughes/micropython_sdl2.git

# Download MicroPython and build the MPY cross compiler
git clone -b v1.22-release --recursive https://github.com/micropython/micropython.git
cd micropython
make -C mpy-cross
```

Build MicroPython with MicroPython_SDL2
---------------------------------------
At the bash prompt:
```
# Note we are still in the ~/gh/micropython directory
cd ports/unix
make USER_C_MODULES=../../../../micropython_sdl2/micropython.cmake
```

Copy the executable to your path
--------------------------------
At the bash prompt:
```
# Note we are still in the ~/gh/micropython/ports/unix directory
mkdir ~/bin
cp build-standard/micropython ~/bin
```
