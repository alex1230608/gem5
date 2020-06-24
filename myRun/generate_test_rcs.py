import argparse
import os.path
from os import path
from distr import TruncatedZipf
import random
import numpy as geek

root="/home/kuofeng/myGitRepos/gem5"

parser = argparse.ArgumentParser(description='Generate test rcs files')
parser.add_argument('--prefix', action="store", required=True)
parser.add_argument('--distr', choices=['simple','rackout'], required=True)
parser.add_argument('--sharded', choices=['shared','sharded','threshold','wrr_shared'], required=True)
parser.add_argument('--test-range', type=int, action="store", required=True)
parser.add_argument('--repeat', type=int, action="store", required=True)
parser.add_argument('-n', type=int, action="store", required=True)

# following only work with threshold strategy
parser.add_argument('--probThr', type=float, action="store") 
	# for alpha = 0.99, index range = 32768, maxProb ~ 0.08 
	# => probThr should be smaller than this

# following only work with rackout distr
parser.add_argument('--alpha', type=float, action="store")
parser.add_argument('--read-ratio', type=float, action="store")
parser.add_argument('--clk-separate', type=int, action="store")
parser.add_argument('--clk-type-count', type=int, action="store")
parser.add_argument('--cpu-clock', action="store")

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
	if args.sharded == "threshold":
		if args.probThr == None:
			print("Threshold strategy needs probThr parameter\n")
			exit()
	if args.sharded == "wrr_shared":
		if args.clk_separate == None or args.clk_type_count == None or args.cpu_clock == None:
			print("Missing parameters for wrr_shared\n")
			exit()
		if args.clk_type_count == 0:
			args.sharded = "shared"

if args.distr == "simple":
	test_name="%s_%s_n%d_%s_%s_r%d_i%d"%(args.prefix, args.distr, args.n, args.rw, args.sharded, args.repeat, args.test_range)
elif args.distr == "rackout":
	if args.sharded == "threshold":
		test_name="%s_%s_n%d_a%.3f_rr%.3f_%s_p%.4f_r%d_i%d"%(args.prefix, args.distr, args.n, args.alpha, args.read_ratio, args.sharded, args.probThr, args.repeat, args.test_range)
	elif args.sharded == "wrr_shared":
		test_name="%s_%s_n%d_a%.3f_rr%.3f_%s_clk%s_sep%d_tc%d_r%d_i%d"%(args.prefix, args.distr, args.n, args.alpha, args.read_ratio, args.sharded, args.cpu_clock, args.clk_separate, args.clk_type_count, args.repeat, args.test_range)
	else:
		test_name="%s_%s_n%d_a%.3f_rr%.3f_%s_r%d_i%d"%(args.prefix, args.distr, args.n, args.alpha, args.read_ratio, args.sharded, args.repeat, args.test_range)


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
	rrNic = 0
	rvToKeyMap = range(0, args.test_range)
	random.shuffle(rvToKeyMap)

	distr = TruncatedZipf(args.alpha, args.test_range)
	pdf = distr.pdf

	load = [0]*num_nic
	if args.sharded == "wrr_shared":
		# calculate weights based on speed
        	int_middle_clk = int(args.cpu_clock[:-3])
        	start = int_middle_clk - (args.clk_type_count-1)*args.clk_separate/2
        	step = args.clk_separate
        	stop = int_middle_clk + (args.clk_type_count-1)*args.clk_separate/2 + 1
        	cpu_clocks = range(start, stop, step)
		w = map(float, cpu_clocks) * (num_nic/args.clk_type_count) # w = cpu speed
		print w
	for i in range(0, args.repeat):
		rank = distr.rv()-1
		key = rvToKeyMap[rank]
		readWrite = 0 if random.random() < args.read_ratio else 1
		# load-balancing: sharded or shared
		if args.sharded == "sharded":
			nic = num_nic*key/args.test_range
		elif args.sharded == "shared":
			nic = (nic+1)%num_nic
		elif args.sharded == "threshold":
			prob = pdf[rank]
			if prob > args.probThr:
				# probability of this key is very often 
				# => shared to increase throughput
				rrNic = (rrNic+1)%num_nic
				nic = rrNic
			else:
				# probability of this key is small
				# => partitioned is enough
				nic = num_nic*key/args.test_range
		elif args.sharded == "wrr_shared":
			# WRR based on weihts
			nic = geek.argmin(load, axis=0)
			load[nic] += 1./w[nic]
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
