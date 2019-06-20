#!/usr/bin/python
# -*- coding: UTF-8 -*-

import serial
import json
import sys
import time
import datetime

# Serial information
COM_PORT = '/dev/tty.usbmodem1451'
BAUD_RATES = 9600
ser = serial.Serial(COM_PORT, BAUD_RATES)

try:
  while True:
    # Get arduino information
    while ser.in_waiting:
      # Get RFID Tag and now time
      data_raw = ser.readline()
      getRFIDtag = data_raw.decode('utf-8')
      getRFIDtag = getRFIDtag.strip('\r\n')
      getNowTime = datetime.datetime.now()
      timeToValue = int(getNowTime.hour) * 3600 + int(getNowTime.minute) * 60 + int(getNowTime.second)
      filename = "./recordTime.json"

      print('Receive Data: ', getRFIDtag)
      print(getNowTime)

      # Update now value in recordTime.json
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

# Enter ctrl + c to exit program
except KeyboardInterrupt:
  ser.close()
  print('Bye!')