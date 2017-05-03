import time
import serial
import array
import sys

class WorldCoord:
	def __init__(self, q, a):
		self.q = q
		self.a = a
		self.x = 0.0
		self.y = 0.0
		self.z = 0.0
		self.vx = 0.0
		self.vy = 0.0
		self.vz = 0.0
		self.last_us = -1
		self.count = 0

	def tick(self):
		t = time.time()
		if self.last_us == -1:
			self.last_us = t
			return
		else:
			diff = t - self.last_us
			self.last_us = t
			self.x += self.vx * diff + 0.5 * self.a[0] * self.a[0] * diff
			self.y += self.vy * diff + 0.5 * self.a[1] * self.a[1] * diff
			self.z += self.vz * diff + 0.5 * self.a[2] * self.a[2] * diff
			self.vx += diff * self.a[0]
			self.vy += diff * self.a[1]
			self.vz += diff * self.a[2]

def main():
	ser = serial.Serial('/dev/ttyACM0', 115200) # Establish the connection on a specific port
	while True:
		ser.write('1\n')
		line = ser.readline()
		if line.find("DMP ready!") == 0:
			break
	count = 0

	serialCount = 0
	aligned = 0
	#buf = ' '*20
	buf = array.array('c', ['\0' for _ in xrange(20)])
	q = [0,0,0,0]
	a = [0,0,0]
	world = WorldCoord(q, a)
	a_sum = [0, 0, 0]
	while True:
		ch = ser.read(1)
		if ch == '$':
			serialCount = 0
		#print aligned, ord(ch)
		if aligned < 4:
			if serialCount == 0:
				if ord(ch) == ord('$'):
					aligned += 1
				else:
					aligned = 0
			elif serialCount == 1:
				if ord(ch) == 2:
					aligned += 1
				else: 
					aligned = 0
			elif serialCount == 18:
				if ord(ch) == ord('\r'):
					aligned += 1
				else:
					aligned = 0
			elif serialCount == 19:
				if ord(ch) == ord('\n'):
					aligned += 1
				else:
					aligned = 0
			serialCount += 1
			if serialCount == 20:
				serialCount = 0
		else:
			if serialCount > 0 or ch == '$':
				buf[serialCount] = ch
				serialCount += 1
				if serialCount == 20:
					serialCount = 0
					q[0] = (ord(buf[2]) * 256 + ord(buf[3])) / 16384.0
					q[1] = (ord(buf[4]) * 256 + ord(buf[5])) / 16384.0
					q[2] = (ord(buf[6]) * 256 + ord(buf[7])) / 16384.0
					q[3] = (ord(buf[8]) * 256 + ord(buf[9])) / 16384.0
					for i in range(3):
						a[i] = (ord(buf[10+i*2]) * 256 + ord(buf[11+i*2]))
						if a[i] >=  32768:
							a[i] -= 65536
						a[i] /= 2048.0
					#a[0] = (ord(buf[10]) * 256 + ord(buf[11]))
					#a[1] = (ord(buf[12]) * 256 + ord(buf[13]))
					#a[2] = (ord(buf[14]) * 256 + ord(buf[15]))

					#if a[0] >=  32768:
						#a[0] -= 65536
					#if a[0] >=  32768:
						#a[0] -= 65536
					if count > 2000:
						if count <= 3000:
							a_sum[0] += a[0]
							a_sum[1] += a[1]
							a_sum[2] += a[2]

					if count > 3000:
						a[0] -= a_sum[0] / 1000
						a[1] -= a_sum[1] / 1000
						a[2] -= a_sum[2] / 1000
						world.tick()
						print "world", world.x, world.y, world.z
					count += 1
					if count % 200 == 0:
						print q, a
						sys.stdout.flush()

if __name__ == '__main__':
	main()