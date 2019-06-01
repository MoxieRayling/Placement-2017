import time
import smbus
import sys
import math
import threading

bus = smbus.SMBus(1)
func = sys.argv[1]

	
device = 0x27
command = 0x14

w, h = 100, 100;
plot = [[0 for x in range(w)] for y in range(h)] 

bus.write_byte_data(device, 0x00, 0x00)

xCoord = 50
yCoord = 50
maxSpeed = 0.1

def Plot(length):
	for i in range(0,length):
		plot[xCoord][yCoord] = 1
		time.sleep(maxSpeed)
	print(plot)

def Motor(wait, length, dir, motor):
	m1steps = [0x03,0x06,0x0c,0x09]
	m2steps = [0x30,0x60,0xc0,0x90]
	length = int(length)
	if motor == 'x':
		for i in range(0,length):"""
			bus.write_byte_data(device,command,m1steps[0*dir])
			time.sleep(wait)
			bus.write_byte_data(device,command,m1steps[1*dir])
			time.sleep(wait)
			bus.write_byte_data(device,command,m1steps[2*dir])
			time.sleep(wait)
			bus.write_byte_data(device,command,m1steps[3*dir])"""
			x += 1
			time.sleep(wait)
	elif motor == 'y':
		for i in range(0,length):"""
			bus.write_byte_data(device,command,m2steps[0*dir])
			time.sleep(wait)
			bus.write_byte_data(device,command,m2steps[1*dir])
			time.sleep(wait)
			bus.write_byte_data(device,command,m2steps[2*dir])
			time.sleep(wait)
			bus.write_byte_data(device,command,m2steps[3*dir])"""
			y += 1
			time.sleep(wait)



def DrawLine(angle, length):
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
	
	if __name__ == '__main__':
		x = threading.Thread(target=Motor, args=(m1wait,m1length,xdir,'x'))
		y = threading.Thread(target=Motor, args=(m2wait,m2length,ydir,'y'))
		z = threading.Thread(target=Plot, args=(length))
		x.start()
		y.start()
		z.start()

	bus.write_byte_data(device,command,0x00)
	return

	
def DrawCircle(r,faces):
	theta = 360 / faces
	length = math.cos(math.radians(90 - theta / 2)) * r * 2
	
	for angle in range(theta / 2,360,theta):
		DrawLine(angle,length)

if func == "DC":
	DrawCircle(int(sys.argv[2]),int(sys.argv[3]))
if func == "DL":
	DrawLine(float(sys.argv[2]),int(sys.argv[3]))
	
bus.write_byte_data(device, command, 0x00)
