import argparse
import os.path
from os import path
from distr import TruncatedZipf
import random

root="/home/kuofeng/myGitRepos/gem5"

parser = argparse.ArgumentParser(description='Generate test rcs files')
parser.add_argument('--distr', choices=['simple','rackout'], required=True)
parser.add_argument('--sharded', choices=['shared','sharded'], required=True)
parser.add_argument('--test-range', type=int, action="store", required=True)
parser.add_argument('--repeat', type=int, action="store", required=True)
parser.add_argument('-n', type=int, action="store", required=True)

# following only work with rackout distr
parser.add_argument('--alpha', type=float, action="store")
parser.add_argument('--read-ratio', type=float, action="store")


# following only work with simple distr
parser.add_argument('--rw', choices=['read','write','readWrite'])

args = parser.parse_args()

if args.distr == "simple":
	if args.rw == None:
		print("Missing parameters\n")
		exit()
elif args.distr == "rackout":
	if args.alpha == None or args.read_ratio == None:
		print("Missing parameters\n")
		exit()

if args.distr == "simple":
	test_name="%s_n%d_%s_%s_r%d_i%d"%(args.distr, args.n, args.rw, args.sharded, args.repeat, args.test_range)
elif args.distr == "rackout":
	test_name="%s_n%d_a%.3f_rr%.3f_%s_r%d_i%d"%(args.distr, args.n, args.alpha, args.read_ratio, args.sharded, args.repeat, args.test_range)

content="""
mount /dev/sdb1 /mnt
/myBinaries/kvs /myBinaries/src/kvs/workload/%s.txt
/sbin/m5 exit
"""%test_name

f = open("%s/myScripts/test_%s.rcS"%(root,test_name), "w")
f.write(content)
f.close()

#workload gen
num_nic = args.n
time_period = 1

workloadFile = "/mnt/myBinaries/src/kvs/workload/%s.txt"%test_name
if path.exists(workloadFile):
	print("File already exists")
	exit()

f = open(workloadFile, "w")

if args.distr == "rackout":
	reqsPerNic = [[] for i in range(0,num_nic)]
	time = 0
	nic = 0
	rvToKeyMap = range(0, args.test_range)
	random.shuffle(rvToKeyMap)

	for i in range(0, args.repeat):
		distr = TruncatedZipf(args.alpha, args.test_range)
		key = rvToKeyMap[distr.rv()-1]
		readWrite = 0 if random.random() < args.read_ratio else 1
		# load-balancing: sharded or shared
		if args.sharded == "sharded":
			nic = num_nic*key/args.test_range
		else:
			nic = (nic+1)%num_nic
		reqsPerNic[nic].append("%d\t%d\t%d"%(time,key,readWrite))
		time += time_period

	f.write("%d\n"%num_nic)
	for nic in range(0, num_nic):
		f.write("%d "%len(reqsPerNic[nic]))
	f.write("\n")
	for nic in range(0, num_nic):
		f.write("\n")
		for req in reqsPerNic[nic]:
			f.write("%s\n"%req)
elif args.distr == "simple":
	separate = 10000
	test_range = args.test_range
	test_repeat = args.repeat
	interval = 1
	sharded = 1 if args.sharded=="sharded" else 0
	readWrite = 0 if args.rw == "read" else (1 if args.rw == "write" else 2)

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
