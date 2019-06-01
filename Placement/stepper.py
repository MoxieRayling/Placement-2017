import time
import smbus

device = 0x24
command = 0x14
m1steps = [0x03,0x06,0x0c,0x09]
m2steps = [0x30,0x60,0xc0,0x90]

write_byte_data(device, 0x00, 0x00)

def stepper(m1dir, m2dir, wait, steps):
	wait = wait/1000
	steps = [0x00,0x00,0x00,0x00]
	
	if m1dir = 1:
		for x in steps:
			steps[x] += m1steps[x]
	if m1dir = -1:
		for x in reversed(steps):
			steps[x] += m1steps[x]
	if m2dir = 1:
		for x in steps:
			steps[x] += m2steps[x]
	if m2dir = -1:
		for x in reversed(steps):
			steps[x] += m2steps[x]		
			
	for x in steps:
		write_byte_data(device, command, steps[0])
		time.sleep(wait)
		write_byte_data(device, command, steps[1])
		time.sleep(wait)
		write_byte_data(device, command, steps[2])
		time.sleep(wait)
		write_byte_data(device, command, steps[3])
		time.sleep(wait)
		
	write_byte_data(device,command,0x00)
	return

