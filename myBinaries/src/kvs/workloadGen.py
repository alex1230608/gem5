num_nic = 2

time_period = 100
separate = 10000
test_range = 2
test_repeat = 300
interval = 1
sharded = 1
readWrite = 1


print("%d"%num_nic)
for nic in range(0, num_nic):
	print "%d"%(test_repeat*(test_range/interval)),
print ""

for nic in range(0, num_nic):
	if sharded == 1:
		start = nic*separate
	else:
		start = 0
	end = start + test_range

	print ""
	time = 0
	for i in range(0, test_repeat):
		for key in range(start, end, interval):
			time = time + time_period
			print("%d\t%d\t%d"%(time, key, readWrite))
