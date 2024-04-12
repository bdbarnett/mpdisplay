'''
wifi.py - connect to wifi

Usage:
    import wifi
    wlan = wifi.connect(SSID, PASSWORD)
'''

def connect(ssid, password):
    import network
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active() or not wlan.isconnected():
        wlan.active(True)
        print('Connecting to:', ssid, end=' ')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            print('.', end='')
    print('\nNetwork config:', wlan.ifconfig(), '\n')
    return wlan
