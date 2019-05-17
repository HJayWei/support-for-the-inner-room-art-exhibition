#!/usr/bin/python
# -*- coding: UTF-8 -*-

import RPi.GPIO as GPIO
import time

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

buzzier()