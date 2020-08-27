from esptempconfig import esptempconfig
import machine
from machine import Pin
import onewire
import time, ds18x20
import urequests
import utime, urandom
import uhashlib, ubinascii

class espTemp:
  ow = None
  ds = None
  rtc = None
  led = None

  def __init__(self):
   self.ow = onewire.OneWire(Pin(12)) # create a OneWire bus on GPIO12
   self.ow.scan()               # return a list of devices on the bus
   self.ow.reset()              # reset the bus
   self.ds = ds18x20.DS18X20(self.ow)
   
   self.rtc = machine.RTC()
   self.rtc.irq(trigger=self.rtc.ALARM0, wake=machine.DEEPSLEEP)

   self.led = Pin(2, Pin.OUT)
   self.led.on() # led is inverted

   # seeding prng
   t1 = utime.ticks_cpu()
   self.get_temp()
   t2 = utime.ticks_cpu()
   urandom.seed(t2-t1)

  def goSleep(self):
    # send ESP to deepsleep
    print("Going to deepsleep ({}sec)...".format(esptempconfig.deepsleep_time/1000))
    self.rtc.alarm(self.rtc.ALARM0, esptempconfig.deepsleep_time)
    machine.deepsleep()

  def get_temp(self):
    # read current temperature from sensor
    roms = self.ds.scan()
    self.ds.convert_temp()
    time.sleep_ms(750)
    return self.ds.read_temp(roms[0])

  def setLED(self,state):
    # activate LED ist state==True
    if state is True:
      self.led.off()
    else:
      self.led.on()

  def sayHi(self):
    # blink LED
    self.setLED(False)
    for i in range(0,5):
      self.setLED(True)
      time.sleep(0.5)
      self.setLED(False)
      time.sleep(0.5)

  def sendTemp(self):
    print("Sending temperature...", end="")
    temp = self.get_temp()
    random = urandom.getrandbits(32)
    hash = uhashlib.sha256()
    hash.update(str(esptempconfig.api_id)+str(random)+str(temp)+esptempconfig.api_key)
    signature = ubinascii.hexlify(hash.digest()).decode()
    data = "sensor={}&time={}&temp={}&signature={}".format(esptempconfig.api_id, random, temp, signature)

    resp = urequests.post(esptempconfig.api_endpoint, headers={'content-type':'application/x-www-form-urlencoded'}, data=data)

    if resp.status_code == 200:
      print("OK")
      return True
    else:
      print("FAILED")
      print("  Data: {}".format(data))
      print("  HTTP-Status: {}".format(resp.status_code))
      print("  Response: {}".format(resp.text))
      return False
