import argparse
import os.path
from os import path

root="/home/kuofeng/myGitRepos/gem5"

parser = argparse.ArgumentParser(description='Generate test rcs files')
parser.add_argument('--term-file', action="store", required=True)
parser.add_argument('--lat', type=int, action="store", required=True)
parser.add_argument('--rw', choices=['read','write','readWrite'], required=True)
parser.add_argument('--sharded', choices=['sharded','shared'], required=True)
parser.add_argument('--repeat', type=int, action="store", required=True)
parser.add_argument('--test-range', type=int, action="store", required=True)
args = parser.parse_args()

#terminal_file = "%s/tmp/output/system.terminal"%root
terminal_file = args.term_file
with open(terminal_file) as fp:
	for line in fp:
		words = line.strip().split(' ')
		if words[0] == "elapsed:":
			print("%d\t%s\t%s\t%d\t%d\t%s"%(args.lat, args.rw, args.sharded, args.repeat, args.test_range, words[1]))
