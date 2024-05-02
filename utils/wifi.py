'''
wifi.py - connect to wifi

Usage:
    import wifi
    wlan = wifi.connect(SSID, PASSWORD)
'''
_retries = 10

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
                print('\nNetwork config:', wlan.ifconfig(), '\n')
                break
            tries += 1
        else:
            print('\nFailed to connect.\n')
    return wlan
