import time
from pyhomeworks import Homeworks

def callback(msg,args):
    print(msg,args)

print("Starting interace")
hw = Homeworks('192.168.2.55',4008, callback)

print("Connected. Waiting for messages.")
time.sleep(10.)

print("Closing.")
hw.close()

print("Done.")
