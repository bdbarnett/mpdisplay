"""
micropython.py - A module to prevent errors when running applications
written for both CPython and MicroPython.  Doesn't (necessarily) allow
the functions to run, but prevents them from throwing errors when loaded.
"""
const = lambda x: x

def viper(func):
    return func

def native(func):
    return func

