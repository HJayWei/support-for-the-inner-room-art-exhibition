#!/usr/bin/python
# -*- coding: UTF-8 -*-

from turtle import *
from datetime import *
import json
import sys
import time

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
    mkHand("secHand", 60)
    mkHand("minHand", 50)
    mkHand("hurHand", 30)
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
    t = datetime.today()
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
    printer.back(700)
    printer.write(Sum(), align="center",
                  font=("Courier", 50, "bold"))
    printer.home()
    tracer(True)
 
    ontimer(Tick, 100)#100ms后继续调用tick
 
def main():
    try:
        setup(width=1300, height=2000)
        tracer(False)
        Init()
        SetupClock(500)
        tracer(True)
        Tick()
        mainloop()
    # Enter ctrl + c to exit program
    except KeyboardInterrupt:
        print('Bye!')
 
if __name__ == "__main__":
    main()
