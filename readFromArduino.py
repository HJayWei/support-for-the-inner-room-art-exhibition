#!/usr/bin/python
# -*- coding: UTF-8 -*-

import serial
import json
import sys
import time
import datetime
import RPi.GPIO as GPIO
import MFRC522
import signal

# Serial information
COM_PORT = '/dev/ttyACM0'
BAUD_RATES = 9600
ser = serial.Serial(COM_PORT, BAUD_RATES)

def inseToJSON(filename, getRFIDtag, timeToValue):
  with open(filename) as file:
    getList = json.load(file)
    if len(getList) != 0:
      # RFID tag not exist
      noTagNum=True
      for i in range(len(getList[0])):
        # Have RFID tag in array
        if getRFIDtag in getList[0][i]:
          noTagNum=1
          getTag = getList[0][i][getRFIDtag]
          getTag.append(timeToValue)
          getTagLen = len(getList[0][i][getRFIDtag])
          # Have start time
          if getTagLen % 2 == 0:
            timeDiff = getTag[getTagLen-1] - getTag[getTagLen-2]
            timeTotal = getList[len(getList)-1][0] + timeDiff
            del getList[len(getList)-1]
            getList.append([timeTotal])
            print("timeDiff: ", timeDiff)
          noTagNum=False
      # Add new RFID tag
      if noTagNum:
         getList[0].append({getRFIDtag:[timeToValue]})
    # First insert value
    else:
      getList.append([{getRFIDtag:[timeToValue]}])
      getList.append([0])
  
  print('\n')

  # Write data in recordTime.json
  with open(filename,"w") as file: 
    json.dump(getList, file)

continue_reading = True
# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
  global continue_reading
  print("Ctrl+C captured, ending read.")
  continue_reading = False
  GPIO.cleanup()
# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)
# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

try:
  while continue_reading:
    getNowTime = datetime.datetime.now()
    timeToValue = int(getNowTime.hour) * 3600 + int(getNowTime.minute) * 60 + int(getNowTime.second)
    filename = "./recordTime.json"
    # Get arduino information
    while ser.in_waiting:
      # Get RFID Tag and now time
      data_raw = ser.readline()
      getRFIDtag = data_raw.decode('utf-8')
      getRFIDtag = getRFIDtag.strip('\r\n')

      print('Receive Data: ', getRFIDtag)
      print(getNowTime)

      # Update now value in recordTime.json
      inseToJSON(filename, getRFIDtag, timeToValue)


      # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
      print("Card detected")
    
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:
      getUID = hex(uid[0])[2:] + hex(uid[1])[2:] + hex(uid[2])[2:] + hex(uid[3])[2:]
      getUID = getUID.upper()
      # Print UID
      print("Card read UID: %s" % getUID)
      print(getNowTime)
      inseToJSON(filename, getUID, timeToValue)
      print("\n")
      time.sleep(1)
    
# Enter ctrl + c to exit program
except KeyboardInterrupt:
  ser.close()
  print('Bye!')