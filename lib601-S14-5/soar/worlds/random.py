from random import uniform

dimensions(8,8)
for i in range(int(uniform(2, 11))):
	wall((uniform(0, 8), uniform(0, 8)), (uniform(0, 8), uniform(0, 8)))
