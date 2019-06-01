import time
import sys
import math
import threading
import numpy as np
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

print('script started')

plot = np.zeros( (1024,1024,3), dtype=np.uint8 )
func = sys.argv[1]

xCoord = 512
yCoord = 512
threadCount = 0

maxSpeed = 0.01


def PrintPlot(mode=''):
	global plot
	img = Image.fromarray(plot, 'RGB')
	if mode == 'html':
		img.save('htmlimage.png')
	else:
		img.save('image.png')
	img = Image.open("image.png")
	draw = ImageDraw.Draw(img)
	# font = ImageFont.truetype(<font-file>, <font-size>)
	font = ImageFont.truetype("PressStart2P-Regular.ttf", 16)
	# draw.text((x, y),"Sample Text",(r,g,b))
	draw.text((500, 500),"Sample Text",(0,255,0),font=font)
	img.save('sample-out.png')
	print("printed")

def Motor(wait, length, direction, xory, draw):
	global threadCount
	global xCoord
	global yCoord
	global plot
	print('thread started')
	length = int(length)
	if xory == 'x':
		for i in range(0,length):
			xCoord += direction
			if xCoord > 1023:
				xCoord -= 1023
			if draw == 1:
				plot[xCoord,yCoord] = [254,0,0]
			time.sleep(wait)
	elif xory == 'y':
		for i in range(0,length):
			yCoord += direction
			if yCoord > 1023:
				yCoord -= 1023
			if draw == 1:
				plot[xCoord,yCoord] = [254,0,0]
			time.sleep(wait)
	if draw == 1:
		plot[xCoord,yCoord] = [0,0,254]
	threadCount += 1

def DrawLine(angle, length):
	global threadCount
	global xCoord
	global yCoord
	xwait = maxSpeed
	ywait = maxSpeed
	angle = angle % 360
	xlength = round(length * abs(math.cos(math.radians(angle))))
	ylength = round(length * abs(math.sin(math.radians(angle))))
	xdir = 1
	ydir = 1
	xy = 1
	yx = 1
	if xlength > 0 and ylength > 0:
		xy = xlength / ylength
		yx = ylength / xlength

	if xy < 1:
		xwait = xwait / xy
	elif yx < 1:
		ywait = ywait / yx

	if (angle >= 0 and angle < 90) or (angle >= 270 and angle < 360):
		xdir = -1

	if(angle >= 180 and angle < 360):
		ydir = -1
	threadCount = 0
	print('starting threads')
	if __name__ == '__main__':
		x = threading.Thread(target=Motor, args=(xwait,xlength,xdir,'x',1))
		y = threading.Thread(target=Motor, args=(ywait,ylength,ydir,'y',1))
		x.start()
		y.start()
	while (threadCount < 2):
		time.sleep(maxSpeed)
	print(xCoord)
	print(yCoord)
	return

def DrawLineByCoords(x,y):
	global threadCount
	global xCoord
	global yCoord
	xwait = maxSpeed
	ywait = maxSpeed
	xlength = abs(xCoord - x)
	ylength = abs(yCoord - y)
	xdir = 1
	ydir = 1
	xy = 1
	yx = 1

	if xlength == 0:
		xy = 1
	elif ylength == 0:
		yx = 1
	else:
		xy = xlength/ylength
		yx  =ylength/xlength


	if xy < 1 and xy != 0:
		xwait = xwait / xy

	elif yx < 1 and yx != 0:
		ywait = ywait / yx

	if x < xCoord:
		xdir = -1

	if y < yCoord:
		ydir = -1

	threadCount = 0
	if __name__ == '__main__':
		x = threading.Thread(target=Motor, args=(xwait,xlength,xdir,'x',1))
		y = threading.Thread(target=Motor, args=(ywait,ylength,ydir,'y',1))
		x.start()
		y.start()
	while (threadCount < 2):
		time.sleep(maxSpeed)
	print(xCoord)
	print(yCoord)
	return

def GoTo(x,y):
	global threadCount
	global xCoord
	global yCoord
	'''
	xwait = maxSpeed
	ywait = maxSpeed
	xlength = abs(xCoord - x)
	ylength = abs(yCoord - y)
	xdir = 1
	ydir = 1
	xy = 1
	yx = 1

	if xlength == 0:
		xy = 1
	elif ylength == 0:
		yx = 1
	else:
		xy = xlength/ylength
		yx  =ylength/xlength


	if xy < 1 and xy != 0:
		xwait = xwait / xy

	elif yx < 1 and yx != 0:
		ywait = ywait / yx

	if x < xCoord:
		xdir = -1

	if y < yCoord:
		ydir = -1

	threadCount = 0
	if __name__ == '__main__':
		x = threading.Thread(target=Motor, args=(xwait,xlength,xdir,'x',0))
		y = threading.Thread(target=Motor, args=(ywait,ylength,ydir,'y',0))
		x.start()
		y.start()
	while (threadCount < 2):
		time.sleep(maxSpeed)
	print(xCoord)
	print(yCoord)
	'''
	xCoord=x
	yCoord=y
	return

def Circle(r, start = 0, stop = 360):
	global xCoord
	global yCoord
	stop = stop*r/200*math.pi
	start = start*r/200*math.pi
	x = 0
	y = r
	a = 0
	r2 = int((r**2/2)**0.5)
	count = 'y'
	xDirection = 1
	yDirection = -1
	for j in range(0,8):
		if j == 2 or j == 6:
			xDirection *= -1
		if j == 4:
			yDirection *= -1
		if j == 0 or j == 4:
			x += xDirection
			for i in range(0,r2):
				x += xDirection
				a += 1
				if (abs(r**2 - y**2)**0.5) < abs(x):
					y += yDirection
				if a >= start and a <= stop:
					plot[(x+yCoord)%1024,(y+xCoord)%1024] = [254,0,0]
				if a > stop:
					break

		if j == 1 or j == 5:
			for i in range(0,r2):
				y += yDirection
				a += 1
				if r-(abs(r**2 - x**2)**0.5) < r-abs(y):
					x += xDirection
				if a >= start and a <= stop:
					plot[(x+yCoord)%1024,(y+xCoord)%1024] = [254,0,0]
				if a > stop:
					break

		if j == 2 or j == 6:
			for i in range(0,r2):
				y += yDirection
				a += 1
				if (abs(r**2 - y**2)**0.5) < abs(x):
					x += xDirection
				if a >= start and a <= stop:
					plot[(x+yCoord)%1024,(y+xCoord)%1024] = [254,0,0]
				if a > stop:
					break

		if j == 3 or j == 7:
			for i in range(0,r2):
				x += xDirection
				a += 1
				if r-(abs(r**2 - x**2)**0.5) < r-abs(y):
					y += yDirection
				if a >= start and a <= stop:
					plot[(x+yCoord)%1024,(y+xCoord)%1024] = [254,0,0]
				if a > stop:
					break
		if a > stop:
			break
def DrawCircle(r,faces,start = 0,stop = 360):
	theta = int(360 / faces)
	length = math.cos(math.radians(90 - theta / 2)) * r * 2
	for i in range(start, stop,theta):
		DrawLine(i,length)
	print('drew circle')

"""if func == "DrawSmiley":
	GoTo(512,62)
	DrawCircle(450,60)
	GoTo(312,212)
	DrawCircle(100,60)
	GoTo(312,612)
	DrawCircle(100,60)
	GoTo(512,812)
	DrawCircle(300,60,180,363)
	GoTo(512,212)
	DrawLine(90,600)
elif func == "DC":
	DrawCircle(int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]))
elif func == "DL":
	DrawLine(float(sys.argv[2]),int(sys.argv[3]))"""


def RunFile(fileName):
    file = open(fileName)
    line = file.readline()
    while line:
        instruction = line.split() 
        command = instruction[0]
        parameters = instruction[1:]
        doIt(command,parameters)
        line = file.readline()
    file.close()
    
def doIt(command,parameters):
    if command == 'GT': 
    	GoTo(int(parameters[0]), int(parameters[1]))
    elif command == 'DC': 
    	if len(parameters) == 1:
    		Circle(int(parameters[0]))
    	elif len(parameters) == 3:
       		Circle(int(parameters[0]),int(parameters[1]),int(parameters[2]))
    elif command == 'DL': 
    	DrawLine(float(parameters[0]),int(parameters[1]))
    elif command == 'RF': 
    	RunFile(parameters[0])

if func == "RF":
	RunFile(sys.argv[2])
PrintPlot(sys.argv[3])