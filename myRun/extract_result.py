import argparse
import os.path
from os import path

root="/home/kuofeng/myGitRepos/gem5"

parser = argparse.ArgumentParser(description='Generate test rcs files')
parser.add_argument('--term-file', action="store", required=True)
parser.add_argument('--lat', type=int, action="store", required=True)
parser.add_argument('-n', type=int, action="store", required=True)

parser.add_argument('--distr', choices=['simple','rackout'], required=True)
parser.add_argument('--sharded', choices=['shared','sharded'], required=True)
parser.add_argument('--test-range', type=int, action="store", required=True)
parser.add_argument('--repeat', type=int, action="store", required=True)

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

#terminal_file = "%s/tmp/output/system.terminal"%root
terminal_file = args.term_file
with open(terminal_file) as fp:
	for line in fp:
		words = line.strip().split(' ')
		if words[0] == "elapsed:":
			if args.distr == "simple":
				print("%d\t%s\t%s\t%d\t%d\t%s"%(args.lat, args.rw, args.sharded, args.repeat, args.test_range, words[1]))
			elif args.distr == "rackout":
				print("%d\t%d\t%f\t%f\t%s\t%d\t%d\t%s"%(args.n, args.lat, args.alpha, args.read_ratio, args.sharded, args.repeat, args.test_range, words[1]))
