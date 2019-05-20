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
import argparse
import platform
import struct
import os
import inspect
import textwrap
import usb.core
import usb.util
from turtle import *
# from datetime import *

def getJSON():
    filename = "./recordTime.json"
    with open(filename) as file:
        getList = json.load(file)
        sec = getList[1][0]
        hour = sec / 3600
        sec %= 3600
        mini = sec / 60
        sec %= 60
    return [hour, mini, sec]

def Skip(step):
    """
    移动乌龟一段距离，不留痕迹
    :param distance: 像素
    :return:
    """
    penup()
    forward(step)
    pendown()
 
def mkHand(name, length):
    #注册Turtle形状，建立表针Turtle
    reset()
    Skip(-length*0.1)
    begin_poly()
    forward(length*1.1)
    end_poly()
    handForm = get_poly()
    #注册Turtle形状命令register_shape(name,shape=None)
    register_shape(name, handForm)
 
def Init():
    global secHand, minHand, hurHand, printer
    # 重置Turtle指向北
    mode("logo")
    #建立三个表针Turtle并初始化
    #第二个参数为长度
    mkHand("secHand", 40)
    mkHand("minHand", 30)
    mkHand("hurHand", 20)
    secHand = Turtle()
    secHand.shape("secHand")
    secHand.color('red')
    minHand = Turtle()
    minHand.shape("minHand")
    hurHand = Turtle()
    hurHand.shape("hurHand")
    for hand in secHand, minHand, hurHand:
        hand.penup()
        hand.setx(0)
        hand.sety(100)
        hand.pendown()
        hand.shapesize(8, 8, 9)
        hand.speed(0)
    #建立输出文字Turtle
    printer = Turtle()
    printer.hideturtle()
    printer.penup()
 
def SetupClock(radius):
    #建立表的外框
    reset()
    hideturtle()
    penup()
    setx(0)
    sety(100)
    pensize(12)
    for i in range(60):
        Skip(radius)
        if i % 5 == 0:
            forward(20)
            Skip(-radius-20)
        else:
            dot(9)
            Skip(-radius)
        right(6)
 
def Week(t):    
    week = ["星期一", "星期二", "星期三",
            "星期四", "星期五", "星期六", "星期日"]
    return week[t.weekday()]
 
def Date(t):
    y = t.year
    m = t.month
    d = t.day
    return "%s / %d / %d" % (y, m, d)

def Sum():
    sumTime = getJSON()
    return "Total Time: %d h %d m %d s" % (sumTime[0], sumTime[1], sumTime[2])
 
def Tick():
    #绘制表针的动态显示
    #当前时间
    sumTime = getJSON()
    t = datetime.datetime.today()
    # second = t.second + t.microsecond*0.000001
    second = sumTime[2]
    # minute = t.minute + second/60.0
    minute = sumTime[1]
    # hour = t.hour + minute/60.0
    hour = sumTime[0]
    secHand.setheading(6*second)
    minHand.setheading(6*minute)
    hurHand.setheading(30*hour)
 
     #介入Tracer函数以控制刷新速度
    tracer(False)
    printer.reset()
    printer.hideturtle()
    printer.penup()
    printer.setx(0)
    printer.sety(100)
    printer.forward(30)
    printer.write(Date(t), align="center",
                  font=("Courier", 50, "bold"))
    printer.back(180)
    printer.write(Week(t), align="center",
                  font=("Courier", 50, "bold"))
    printer.back(400)
    printer.write(Sum(), align="center",
                  font=("Courier", 30, "bold"))
    printer.home()
    tracer(True)
 
    ontimer(Tick, 100)#100ms后继续调用tick

# buzzier
def buzzier():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    p = GPIO.PWM(12, 100)
    p.start(100)

    print("Do")
    p.ChangeFrequency(1976)
    time.sleep(0.2)

    p.stop()
    GPIO.cleanup()

# printing
example_strings = [ 
'------------------------------',
'Admission time: ',
'Appearing time: ',
'Thank you for your attention.\n\n']

# USB specific constant definitions
PIPSTA_USB_VENDOR_ID = 0x0483
PIPSTA_USB_PRODUCT_ID = 0xA19D
AP1400_USB_PRODUCT_ID = 0xA053
AP1400V_USB_PRODUCT_ID = 0xA19C

valid_usb_ids = {PIPSTA_USB_PRODUCT_ID, AP1400_USB_PRODUCT_ID, AP1400V_USB_PRODUCT_ID}

class printer_finder(object):
    def __call__(self, device):
        if device.idVendor != PIPSTA_USB_VENDOR_ID:
            return False

        return True if device.idProduct in valid_usb_ids else False


CR = b'\x0D'
PIPSTA_LINE_CHAR_WIDTH = 32
FEED_PAST_TEAR_BAR = b'\n' * 5

def setup_usb():
    '''Connects to the 1st Pipsta found on the USB bus'''
    # Find the Pipsta's specific Vendor ID and Product ID (also known as vid
    # and pid)
    dev = usb.core.find(custom_match=printer_finder())
    if dev is None:                 # if no such device is connected...
        raise IOError('Printer not found')  # ...report error

    try:
        dev.reset()

        # Initialisation. Passing no arguments sets the configuration to the
        # currently active configuration.
        dev.set_configuration()
    except usb.core.USBError as err:
        raise IOError('Failed to configure the printer', err)

    # Get a handle to the active interface
    cfg = dev.get_active_configuration()

    interface_number = cfg[(0, 0)].bInterfaceNumber
    usb.util.claim_interface(dev, interface_number)
    alternate_setting = usb.control.get_interface(dev, interface_number)
    intf = usb.util.find_descriptor(
        cfg, bInterfaceNumber=interface_number,
        bAlternateSetting=alternate_setting)

    ep_out = usb.util.find_descriptor(
        intf,
        custom_match=lambda e:
        usb.util.endpoint_direction(e.bEndpointAddress) ==
        usb.util.ENDPOINT_OUT
    )

    if ep_out is None:  # check we have a real endpoint handle
        raise IOError('Could not find an endpoint to print to')
    
    return ep_out

# Serial information
COM_PORT = '/dev/ttyACM0'
BAUD_RATES = 9600
ser = serial.Serial(COM_PORT, BAUD_RATES)

def epochToStr(epoch):
  epochToStr = datetime.datetime.fromtimestamp(epoch)
  return "   " + epochToStr.strftime('%Y-%m-%d %H:%M:%S') + '\n'

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
            # Print image
            os.system('python image_print.py ./logo/Black_s.png')
            time.sleep(2)
            pipsta = setup_usb()
            admission = epochToStr(getTag[getTagLen-1])
            appearing = epochToStr(getTag[getTagLen-2])
            example_strings.insert(2,admission)
            example_strings.insert(4,appearing)
            example_strings.insert(5,"Total time: " + str(timeDiff) + "s\n")

            for line in example_strings:
                print (textwrap.fill(line, PIPSTA_LINE_CHAR_WIDTH))
                pipsta.write(textwrap.fill(line, PIPSTA_LINE_CHAR_WIDTH))
                pipsta.write(CR)
            pipsta.write(CR)
            pipsta.write(FEED_PAST_TEAR_BAR)
            time.sleep(2)
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
  setup(width=720, height=1280)
  tracer(False)
  Init()
  SetupClock(300)
  tracer(True)
  Tick()
  mainloop()
  while continue_reading:
    getNowTime = datetime.datetime.now()
    timeToValue = int(time.mktime(getNowTime.timetuple()))
    filename = "./recordTime.json"
    # Get arduino information
    while ser.in_waiting:
      buzzier()
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
      buzzier()
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
