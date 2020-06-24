import argparse
import os.path
from os import path

root="/home/kuofeng/myGitRepos/gem5"

parser = argparse.ArgumentParser(description='Generate test rcs files')
parser.add_argument('--term-file', action="store", default=None)
parser.add_argument('--cache-file', action="store", default=None)

parser.add_argument('--lat', type=int, action="store", required=True)
parser.add_argument('-n', type=int, action="store", required=True)

parser.add_argument('--distr', choices=['simple','rackout'], required=True)
parser.add_argument('--sharded', choices=['shared','sharded','threshold','wrr_shared'], required=True)
parser.add_argument('--test-range', type=int, action="store", required=True)
parser.add_argument('--repeat', type=int, action="store", required=True)

# following only work with threshold strategy
parser.add_argument('--probThr', type=float, action="store") 
	# for alpha = 0.99, index range = 32768, maxProb ~ 0.08 
	# => probThr should be smaller than this

# following only work with rackout distr
parser.add_argument('--alpha', type=float, action="store")
parser.add_argument('--read-ratio', type=float, action="store")
parser.add_argument('--heter-cpu-clock', type=int, action="store")
parser.add_argument('--clk-separate', type=int, action="store")
parser.add_argument('--clk-type-count', type=int, action="store")

# following only work with simple distr
parser.add_argument('--rw', choices=['read','write','readWrite'])

args = parser.parse_args()

if args.term_file == None == args.cache_file == None:
	print("Exact one file can be provided\n")
	exit()

if args.distr == "simple":
	if args.rw == None:
		print("Missing parameters\n")
		exit()
elif args.distr == "rackout":
	if args.alpha == None or args.read_ratio == None \
	  or args.heter_cpu_clock == None or args.clk_separate == None or args.clk_type_count == None:
		print("Missing parameters\n")
		exit()
	if args.sharded == "threshold":
		if args.probThr == None:
			print("Threshold strategy needs probThr parameter\n")
			exit()
	if args.sharded == "wrr_shared" and args.clk_type_count == 0:
		args.sharded = "shared"

if args.sharded == "threshold":
	probThr = "%f"%args.probThr
else:
	probThr = "N/A"
if args.heter_cpu_clock == 1:
	heterStr = "%f\t%f"%(args.clk_separate,args.clk_type_count)
else:
	heterStr = "N/A\tN/A"

#terminal_file = "%s/tmp/output/system.terminal"%root
if args.term_file != None:
	terminal_file = args.term_file
	with open(terminal_file) as fp:
		for line in fp:
			words = line.strip().split(' ')
			if words[0] == "elapsed:":
				if args.distr == "simple":
					print("%d\t%s\t%s\t%d\t%d\t%s"%(args.lat, args.rw, args.sharded, args.repeat, args.test_range, words[1]))
				elif args.distr == "rackout":
					print("%d\t%d\t%s\t%f\t%f\t%s\t%s\t%d\t%d\t%s"%(args.n, args.lat, heterStr, args.alpha, args.read_ratio, args.sharded, probThr, args.repeat, args.test_range, words[1]))

if args.cache_file != None:
	with open(args.cache_file) as fp:
		for line in fp:
			words = line.strip().split(':')
			if words[0] == "Parsed packets":
				if args.distr == "simple":
					print("%d\t%s\t%s\t%d\t%d\t%s"%(args.lat, args.rw, args.sharded, args.repeat, args.test_range, words[1]))
				elif args.distr == "rackout":
					print("%d\t%d\t%s\t%f\t%f\t%s\t%s\t%d\t%d\t%s"%(args.n, args.lat, heterStr, args.alpha, args.read_ratio, args.sharded, probThr, args.repeat, args.test_range, words[1]))


