# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
from esptempconfig import esptempconfig
import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
import webrepl
webrepl.start()
gc.collect()

import network
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(esptempconfig.wifi_name, esptempconfig.wifi_psk)

import os
#os.remove('main.py')