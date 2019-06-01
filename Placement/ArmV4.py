import time
import smbus
import sys
import math
import threading
import numpy as np
from PIL import Image

print('script started')

global threadCount
global shoulder
global elbow
global forearm
global upperarm
global maxSpeed
global stepsToDegrees
global step1
global step2
global draw
global segment
global motor1Count
global motor2Count

bus = smbus.SMBus(1)
func = sys.argv[1] 
device = 0x27
port1 = 0x14
port2 = 0x15
maxSpeed = 0.01 #delay between motor steps
segment = 10 #determines accuracy of line
stepsToDegrees = 5.8 #ratio of steps to degrees
step1 = [0x03,0x06,0x0c,0x09] #values to move motor1
step2 = [0x30,0x60,0xc0,0x90] #values to move motor2
cStep1 = 0x03 #current position in steps for motor1
cStep2 = 0x30 #current position in steps for motor2
draw = 0 #0 = pen off paper, 1 = pen on paper
elbow = 90 #position of motor1
shoulder = 90 #position of motor2
forearm = 1430 #length of forearm
upperarm = 1300 #length of upperarm
coord = [-upperarm,forearm] #current position of pen
excess1 = 0 #error in stepsToAngle for motor1
excess2 = 0 #error in stepsToAngle for motor2

#bus.write_byte_data(device, 0x00, 0x00)
#bus.write_byte_data(device, 0x01, 0x00)

if func == "IF":
	data = InterpretFile(sys.argv[2])
	WriteFile(data,sys.argv[3])
elif func == "M":
	Motor(sys.argv[2],sys.argv[3])
elif func == "EF":
	ExecuteFile(sys.argv[2])

def InterpretFile(fileName): #reads file, splits line into command and params, passes command/params to DoIt and appends results to data[]
	data = []
	file = open(fileName)
	line = file.readline()
	while line:
		instruction = line.split() 
		command = instruction[0]
		parameters = instruction[1:]
		data.append(DoIt(command,parameters)) 
		line = file.readline()
	file.close()
	return data

def DoIt(command,parameters):
	data = []
	if command == 'C': 
		if len(parameters) == 2:
			data = Circle(int(parameters[0]),int(parameters[1]))
		elif len(parameters) == 4:
			data = Circle(int(parameters[0]),int(parameters[1]),int(parameters[2]),int(parameters[3]))
	elif command == 'L': 
		data = Line(float(parameters[0]),int(parameters[1]))
	elif command == 'P':
		data = Pen(parameters[0])
	elif command == 'IF': 
		data = InterpretFile(parameters[0])
	return data

def WriteFile(data,fileName): #writes list to file
	output = open(fileName,"w")
	for i in range(len(data)):
		for j in range(len(data[i])):
			output.write(str(data[i][j]) + "\n")
		print("loop")
	output.close()

def ExecuteFile(fileName):
	data = []
	i=0
	file = open(fileName)
	line = file.readline() 
	while line:
		i+=1
		data.append(line[:-1]) #removes new line character, appends to data[]
		line = file.readline()
	file.close()
	for i in range(len(data)): #iterates through data[], calls functions based on item in list
		if data[i] ==  "P":
			Pen()
		else:
			bus.write_byte_data(device,port1,int(data[i])) 
			time.sleep(maxSpeed)
			print("yes")

def Line(x,y): 
	global coord
	global segment
	degrees = []
	#constructs a right-angled triangle abc with hypotenuse between current coord and destination
	a = abs(coord[0] - float(x)) #horizontal
	b = abs(coord[1] - float(y)) #verticle
	c = (a**2 + b**2)**0.5 #hypotenuse
	#hyp is split into segments of length segment, new coordinates are calculated at each segment
	ratio = segment/c 
	xInc = a*ratio #calculates increment for x direction per segment
	yInc = b*ratio #calculates increment for y direction per segment
	d = coord[0]
	e = coord[1]
	i = 0
	while(i < c - segment): #iterates between segments, increments coords
		if coord[0] < x:
			d += xInc
		elif coord[0] > x:
			d -= xInc
		if coord[1] < y:
			e += yInc
		elif coord[1] > y:
			e -= yInc
		degrees.append(CoordsToDegrees(d,e)) #inputs coords, returns degrees required to reach coord [angle1,angle2], appends to degrees[]
		i += segment
	degrees.append(CoordsToDegrees(x,y)) #for remainder segment
	coord[0] = x
	coord[1] = y
	data = DegreesToSteps(degrees) #inputs list of degrees, returns list of steps
	return data

def CoordsToDegrees(x,y): #takes coords, returns angles to move
	global maxSpeed
	global forearm
	global upperarm
	global elbow
	global shoulder
	#constructs right-angled triangle xyz
	x = float(x)
	y = float(y)
	z = (x**2 + y**2)**0.5
	#constructs non-right-angled triangle abc where c=z
	a = forearm
	b = upperarm
	c = z
	C = math.degrees(math.acos((a**2 + b**2 - c**2)/(2*a*b))) #angle oppsite side c
	A = math.degrees(math.acos((b**2 + c**2 - a**2)/(2*b*c))) #angle oppsite side a
	#calculates angle Y in triangle xyz
	if x == 0:
		Y = 90
	elif x > 0 and y == 0:
		Y = 180
	elif x <= 0 and y == 0:
		Y = 0
	else:	
		Y = math.degrees(math.acos((x**2 + z**2 - y**2)/(2*x*z)))
		Y = 180 - Y
	#calculates angle D, D = angle from negative Y axis to line c
	if ((x-upperarm)**2+(y)**2)**0.5 < forearm and x < 0:
		D = 90 + Y - A
	elif x <= 0 or ((x)**2+(y-upperarm)**2)**0.5 < forearm:
		D = 90 + Y - A
	elif x > 0:
		D = 270 - Y - A
	else:
		print("Error: coordinates out of bounds " + str(x) + " " + str(y))
		return
	#calculates difference in current postions and required postions
	angle1 = elbow - C
	angle2 = D - shoulder

	elbow = C
	shoulder = D
	return [angle1, angle2]

def DegreesToSteps(params): #takes degrees, returns steps
	data = []
	global excess1
	global excess2

	for j in range(len(params)): #iterates through list of degrees
		steps1Dir = 1 #direction of motor1, 1=clockwise, -1=anticlockwise, 0=dont move
		steps2Dir = 1
		steps1 = float(params[j][0]) * stepsToDegrees #converts degrees to steps
		steps2 = float(params[j][1]) * stepsToDegrees 
		steps1 += excess1 #adds previous error to steps
		steps2 += excess2
		#updates excess, floors steps, exceptions to correct for modulus on negative numbers
		if steps1 > 0: 
			excess1 = steps1%1
			steps1 = math.floor(steps1)
		else:
			excess1 = steps1%1*-1
			steps1Dir*=-1
			steps1 = math.floor(steps1)+1
		if steps2 > 0:
			excess2 = steps2%1
			steps2 = math.floor(steps2)
		else:
			excess2 = steps2%1-1
			steps2Dir*=-1
			steps2 = math.floor(steps2)+1
		
		if max(steps1,steps2) == 0: #if steps both = 0 then continue to next iteration
			continue
		else:
			ratio = abs(min(steps1,steps2)/max(steps1,steps2)) #calculates ratio between steps
			count = ratio + 0.5 
			#iterates between largest of steps, distributes steps according to ratio
			if steps1 > steps2:
				for i in range(int(abs(steps1))):
					if count > 1:
						data.append(StepsToData([steps1Dir,steps2Dir])) #converts directions into next step, appends to list
						count = count%1
						count += ratio
					elif count >= 0 and count < 0.999:
						data.append(StepsToData([steps1Dir,0]))
						count += ratio
					else:
						data.append(StepsToData([steps1Dir,steps2Dir]))
						count = ratio
			elif steps1 < steps2:
				for i in range(int(abs(steps2))):
					if count > 1:
						data.append(StepsToData([steps1Dir,steps2Dir]))
						count = count%1
						count += ratio
					elif count >= 0 and count < 0.999:
						data.append(StepsToData([0,steps2Dir]))
						count += ratio
					else:
						data.append(StepsToData([steps1Dir,steps2Dir]))
						count = ratio
			else:
				for i in range(int(steps2)):
					data.append(StepsToData([steps1Dir,steps2Dir]))
		#data.append([steps1,steps2])
	return data

def StepsToData(step): #receives directions e.g. [1,1], returns next steps [0x33]
	global step1
	global step2
	global cStep1
	global cStep2
	
	result1 = 0x00 #default result
	result2 = 0x00
	#checks current step and direction, returns next step
	if step1.index(cStep1) == 3 and step[0] == 1: 
		result1 += step1[0] 
		cStep1 = step1[0]
	elif step1.index(cStep1) == 0 and step[0] == -1:
		result1 += step1[3] 
		cStep1 = step1[3]
	elif step[0] != 0:
		result1 += step1[step1.index(cStep1)+int(step[0])]
		cStep1 = step1[step1.index(cStep1)+int(step[0])]

	if step2.index(cStep2) == 3 and step[1] == 1: 
		result2 += step2[0] 
		cStep2 = step2[0]
	elif step2.index(cStep2) == 0 and step[1] == -1:
		result2 += step2[3] 
		cStep2 = step2[3]
	elif step[1] != 0:
		result2 += step2[step2.index(cStep2)+int(step[1])]
		cStep2 = step2[step2.index(cStep2)+int(step[1])]

	return hex(result1 + result2) #hex conversion for readability 

def Circle(r,faces,start = 0,stop = 360): 
	data = []
	theta = int(360 / faces)
	length = math.cos(math.radians(90 - theta / 2)) * r * 2
	for i in range(start, stop,theta):
		x = coord[0] + math.cos(i)*length
		y = coord[1] + math.sin(i)*length
		data.append(Line(x,y))
	return data
			
def Pen(): #stub method - to toggle pen on paper
	global draw
	if draw == 1:
		draw = 0
		time.sleep(0.5)
	else:
		draw = 1
		time.sleep(0.5)
	return "D"

def Motor(motor, angle): #test method to move motors
	if motor == 1:
		for i in range(angle*stepsToDegrees):
			bus.write_byte_data(device, port, 0x03)
			i += 1
			time.sleep(maxSpeed)
			bus.write_byte_data(device, port, 0x06)
			i += 1
			time.sleep(maxSpeed)
			bus.write_byte_data(device, port, 0x0c)
			i += 1
			time.sleep(maxSpeed)
			bus.write_byte_data(device, port, 0x09)
			time.sleep(maxSpeed)
	if motor == 2:
		for i in range(angle*stepsToDegrees):
			bus.write_byte_data(device, port, 0x30)
			i += 1
			time.sleep(maxSpeed)
			bus.write_byte_data(device, port, 0x60)
			i += 1
			time.sleep(maxSpeed)
			bus.write_byte_data(device, port, 0xc0)
			i += 1
			time.sleep(maxSpeed)
			bus.write_byte_data(device, port, 0x90)
			time.sleep(maxSpeed)
	if motor == 0:
		for i in range(angle*stepsToDegrees):
			bus.write_byte_data(device, port, 0x33)
			i += 1
			time.sleep(maxSpeed)
			bus.write_byte_data(device, port, 0x66)
			i += 1
			time.sleep(maxSpeed)
			bus.write_byte_data(device, port, 0xcc)
			i += 1
			time.sleep(maxSpeed)
			bus.write_byte_data(device, port, 0x99)
			time.sleep(maxSpeed)

#bus.write_byte_data(device,port1,0x00)
print("script ended")