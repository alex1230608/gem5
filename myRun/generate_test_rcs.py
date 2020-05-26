import argparse
import os.path
from os import path

root="/home/kuofeng/myGitRepos/gem5"

parser = argparse.ArgumentParser(description='Generate test rcs files')
parser.add_argument('--rw', choices=['read','write','readWrite'], required=True)
parser.add_argument('--sharded', choices=['shared','sharded'], required=True)
parser.add_argument('--repeat', type=int, action="store", required=True)
parser.add_argument('--test-range', type=int, action="store", required=True)
args = parser.parse_args()

test_name="%s_%s_r%d_i%d"%(args.rw, args.sharded, args.repeat, args.test_range)
content="""
mount /dev/sdb1 /mnt
/myBinaries/kvs /myBinaries/src/kvs/workload/%s.txt
/sbin/m5 exit
"""%test_name

f = open("%s/myScripts/test_%s.rcS"%(root,test_name), "w")
f.write(content)
f.close()

#workload gen
num_nic = 2

time_period = 100
separate = 10000
test_range = args.test_range
test_repeat = args.repeat
interval = 1
sharded = 1 if args.sharded=="sharded" else 0
readWrite = 0 if args.rw == "read" else (1 if args.rw == "write" else 2)

workloadFile = "/mnt/myBinaries/src/kvs/workload/%s.txt"%test_name
if path.exists(workloadFile):
	print("File already exists")
else:
	f = open(workloadFile, "w")

	f.write("%d\n"%num_nic)
	for nic in range(0, num_nic):
		f.write ("%d "%(test_repeat*(test_range/interval)))
	f.write("\n")
	
	for nic in range(0, num_nic):
		if sharded == 1:
			start = nic*separate
		else:
			start = 0
		end = start + test_range
	
		f.write("\n")
		time = 0
		for i in range(0, test_repeat):
			for key in range(start, end, interval):
				time = time + time_period
				f.write("%d\t%d\t%d\n"%(time, key, readWrite))
