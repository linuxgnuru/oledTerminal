import time
import sys
import subprocess
import re
import termios
import tty
import time
import os
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

RST = None

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
disp.begin()
disp.clear()
disp.display()
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, width, height), outline=0, fill=0)

padding = -2
top = padding
bottom = height - padding
x = 12

font = ImageFont.load_default()

def ResetView(b):
    global x
    global top
    x = 0
    top = -2
    disp.clear()
    disp.display()
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    disp.image(image)
    disp.display()
    if b == True:
        prompt()

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def prompt():
    draw.text((0, top), str('> '),  font=font, fill=255)
    disp.image(image)
    disp.display()

def WriteText(txt):
#    global x
#    global top
#    top += 6
#    if top >= 64:
#        x = 0
#        ResetView(False)
    draw.text((x, top), str(txt),  font=font, fill=255)
    disp.image(image)
    disp.display()

def WrapText(mtxt):
    global x
    global top
    top += 6
    if top >= 64:
        ResetView(False)
    if len(mtxt) >= 20:
        while len(mtxt) >= 20:
            a = mtxt[0:20]
#            print 'a ', a
            WriteText(a)
            b = mtxt[21:len(mtxt)]
#            print 'b ', b
            mtxt = b
            x = 0
            top += 8
            if top >= 64:
                ResetView(False)
        WriteText(mtxt)
    else:
        WriteText(mtxt)

def SplitOut(txt):
    global x
    global top
    for item in (txt.split('\n')):
        x = 0
#        print 'item ', item
        WrapText(item)
        top += 6
        if top >= 64:
            ResetView(False)

button_delay = 0.1

prompt()

br = False
line = ""

while br == False:
    char = getch()
    if char != '\r':
        if char != '\b':
            line += char
            draw.text((x, top), str(char),  font=font, fill=255)
            disp.image(image)
            disp.display()
            x += 6
            if x >= 120:
                x = 0
                top += 8
                if top >= 64:
                    ResetView(False)
            time.sleep(button_delay)
    else:
#        print "line ", line
        if line.strip().lower() == 'exit':
            br = True
            break
        else:
            try:
                cmd = subprocess.Popen(re.split(r'\s+', line), stdout=subprocess.PIPE)
                cmd_out = cmd.stdout.read()
                SplitOut(cmd_out)
                prompt()
            except OSError:
                x = 0
                top += 8
                if top >= 64:
                    ResetView(False)
                WriteText('invalid command')
                WriteText('> ')
            line = ""
