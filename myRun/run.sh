#!/bin/sh

root="/home/kuofeng/myGitRepos/gem5"
cd $root

#rw="read"
#sharded="sharded"
#sharded_txt="sharded"
#r="300"
#i="2"

rws="read write"
shardeds="shared sharded"
rs="300"
is="2"
lats="2000 5000 10000 20000 50000 100000"
get_result=1

#find available output direcotry
thread=0
while [ -f tmp/busy$thread ]
do
	thread=$((thread+1))
done
echo "" > tmp/busy$thread
cp tmp/output tmp/output$thread -r

if [ $get_result -eq 1 ]; then
	echo "" > ./myRun/result.txt
fi

for rw in $rws
do
  for sharded in $shardeds
  do
    for r in $rs
    do
      for i in $is
      do
	sudo python ./myRun/generate_test_rcs.py --rw $rw --sharded $sharded --repeat $r --test-range $i
	
	for lat in $lats
	do
		stats_file="myRun/stats/stats_l2lat${lat}_${rw}_${sharded}_r${r}_i${i}.txt"
		term_file="myRun/term/term_l2lat${lat}_${rw}_${sharded}_r${r}_i${i}.txt"
		if [ ! -f $term_file ]; then
			echo "" > $term_file
			build/ARM/gem5.opt -d tmp/output$thread configs/example/fs.py --kernel=./myFullSystemImages/fromGem5Website/binaries/vmlinux.arm64 --bootloader=./myFullSystemImages/fromGem5Website/binaries/boot.arm64 --disk-image=./myFullSystemImages/fromGem5Website/disks/aarch64-ubuntu-trusty-headless.img --disk-image=./myFullSystemImages/fromGem5Website/disks/aarch64-ubuntu-trusty-headless.img --mem-size=16GB --caches --l2cache --l2_lat $lat -n 3 --cpu-type=TimingSimpleCPU --script=./myScripts/test_${rw}_${sharded}_r${r}_i$i.rcS -r 1
			cp tmp/output$thread/stats.txt $stats_file
			cp tmp/output$thread/system.terminal $term_file
		fi

		if [ $get_result -eq 1 ]; then
			python ./myRun/extract_result.py --lat $lat --rw $rw --sharded $sharded --repeat $r --test-range $i --term-file $term_file >> ./myRun/result.txt
			#python ./myRun/extract_result.py >> ./myRun/result.txt
		fi
	done
      done
    done
  done
done

rm tmp/busy$thread
rm tmp/output$thread -r
