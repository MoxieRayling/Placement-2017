import time
import smbus
import sys
import math
import threading

bus = smbus.SMBus(1)
func = sys.argv[1]

	
device = 0x27
port = 0x14
xCoord = 50
yCoord = 10
w, h = 100, 100;
plot = [[0 for x in range(w)] for y in range(h)] 
threadCount = 0

bus.write_byte_data(device, 0x00, 0x00)


maxSpeed = 0.01

def Plot(length):
	global threadCount
	length = int(length) + 1
	while (threadCount < 4):
		plot[xCoord][yCoord] = 1
		time.sleep(maxSpeed*0.01)
	threadCount += 1

def PrintPlot():
	global w
	global h
	global plot
	line = ""
	for i in range(0,w):
		for j in range(0,h):
			if (i==50 and j==50):
				line += 'O'
			elif plot[i][j]:
				line += 'X'
			else:
				line += '.'

		print(line)
		line = ''



def Motor(wait, length, direction, motor):
	global threadCount
	global xCoord
	global yCoord
	m1steps = [0x03,0x06,0x0c,0x09]
	m2steps = [0x30,0x60,0xc0,0x90]
	length = int(length)
	if motor == 'x':
		for i in range(0,length):
			
			bus.write_byte_data(device,port,m1steps[0]*direction)
			time.sleep(wait)
			bus.write_byte_data(device,port,m1steps[1]*direction)
			time.sleep(wait)
			bus.write_byte_data(device,port,m1steps[2]*direction)
			time.sleep(wait)
			bus.write_byte_data(device,port,m1steps[3]*direction)
			#	xCoord += direction
			#plot[xCoord][yCoord] = 1

			time.sleep(wait)
	elif motor == 'y':
		for i in range(0,length):
			
			bus.write_byte_data(device,port,m2steps[0]*direction)
			time.sleep(wait)
			bus.write_byte_data(device,port,m2steps[1]*direction)
			time.sleep(wait)
			bus.write_byte_data(device,port,m2steps[2]*direction)
			time.sleep(wait)
			bus.write_byte_data(device,port,m2steps[3]*direction)
			#yCoord += direction
			#plot[xCoord][yCoord] = 1
			time.sleep(wait)
	threadCount += 1



def DrawLine(angle, length):
	global threadCount
	m1wait = maxSpeed
	m2wait = maxSpeed
	angle = angle % 360
	m1length = round(length * abs(math.cos(math.radians(angle))))
	m2length = round(length * abs(math.sin(math.radians(angle))))
	xdir = 1
	ydir = 1
	xy = 1
	yx = 1
	if m1length > 0 and m2length > 0:
		xy = m1length / m2length
		yx = m2length / m1length

	if xy < 1:
		m1wait = m1wait / xy
	elif yx < 1:
		m2wait = m2wait / yx

	if (angle >= 0 and angle < 90) or (angle >= 270 and angle < 360):
		xdir = -1

	if(angle >= 180 and angle < 360):
		ydir = -1
	print(angle)
	if __name__ == '__main__':
		x = threading.Thread(target=Motor, args=(m1wait,m1length,xdir,'x'))
		y = threading.Thread(target=Motor, args=(m2wait,m2length,ydir,'y'))
		#z = threading.Thread(target=Plot, args=(length,))
		x.start()
		y.start()
		#z.start()
	while (threadCount < 2):
		time.sleep(0.1)
		"""
	PrintPlot()
	print(yCoord)
	print(xCoord)"""
	bus.write_byte_data(device,port,0x00)
	return

	
def DrawCircle(r,faces):
	theta = int(360 / faces)
	length = math.cos(math.radians(90 - theta / 2)) * r * 2
	
	for angle in range(theta, 360 + theta, theta):
		DrawLine(angle,length)

if func == "DC":
	DrawCircle(int(sys.argv[2]),int(sys.argv[3]))
	#PrintPlot()
	print(yCoord)
	print(xCoord)
if func == "DL":
	DrawLine(float(sys.argv[2]),int(sys.argv[3]))
	#PrintPlot()
	print(yCoord)
	print(xCoord)
	
bus.write_byte_data(device, port, 0x00)
