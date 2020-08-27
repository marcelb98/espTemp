import espTemp
import time

print("....")
print("....")
et = espTemp.espTemp()

et.sayHi()

if machine.reset_cause() != machine.DEEPSLEEP_RESET:
  # not comming from deepsleep
  print("Waiting 30sec...")
  time.sleep(30)
  print("Done. Starting...")
  et.sayHi()
else:
  print("back from deepsleep")

et.sendTemp()
et.goSleep()