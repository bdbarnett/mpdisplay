'''
wifi.py - connect to wifi

Usage:
    import wifi
    wlan = wifi.connect(SSID, PASSWORD)
'''
from time import sleep_ms
_retries = 100

def connect(ssid, password):
    import network
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active() or not wlan.isconnected():
        wlan.active(True)
        print('Connecting to:', ssid, end=' ')
        wlan.connect(ssid, password)
        tries = 0
        while tries < _retries:
            print('.', end='')
            if wlan.isconnected():
                print('\nConnection established.\nNetwork config:', wlan.ifconfig(), '\n')
                break
            sleep_ms(100)
            tries += 1
        else:
            print('\nFailed to connect.\n')
    else:
        print('\nAlready connected.\nNetwork config:', wlan.ifconfig(), '\n')
    return wlan
