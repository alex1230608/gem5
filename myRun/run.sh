#!/bin/sh

root="/home/kuofeng/myGitRepos/gem5"
cd $root


get_result=0
prefix="rwself_smallLat_withkey_notime_uint64_notsimplified_fc_notslow_notlocal_pt_se_fw_ns_mc" # abbrv"fixClkProb_slow_local_pointer_singleEntry_fixWrite_nosleep_manycore"
distr="rackout"

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

if [ "$distr" = "simple" ]; then

# For simple distr
rws="read write"
shardeds="shared sharded"
rs="300"
is="2"
lats="10 2000 5000 10000 20000 50000"

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

elif [ "$distr" = "rackout" ]; then

# For rackout distr

# workload parameters
genWorkload=0
alphas="0.990"
#rrs="0.000 0.950 0.990 1.000"
#rrs="0.000 1.000"
rrs="0.950"
#shardeds="shared sharded"
shardeds="shared sharded"
rs="100000"
is="32768"
#is="1"
#lats="2000 3000 4000 5000 10000 20000 30000 40000 50000"
nCores="1 2 4 6 8" # the number of cores are always 9; this is more about cores used by NIC threads
#nCores="1 2 4 6 8 12 24 50" # the number of cores are always 9; this is more about cores used by NIC threads

# system parameters
sys_clock="500MHz"
#sys_clock="100MHz"
cpu_clock="633MHz"
#cpu_clock="180MHz"
#l1_lat="60"
#l1_lat="75"
l1_lat="12"
#l2_lats="125 250 500 1000"
#l2_lats="125"
#l2_lats="150 300 600 1200"
#l2_lats="150"
#l2_lats="25 100 500 2000"
l2_lats="25 2000"
l1d_size="64kB"
l1i_size="32kB"
l2_size="2MB"
#l1d_size="32MB"
#l2_size="1GB"



for alpha in $alphas
do
  for rr in $rrs
  do
    for r in $rs
    do
      for i in $is
      do
        for nCore in $nCores
        do
          for sharded in $shardeds
          do
		test=${prefix}_${distr}_n${nCore}_a${alpha}_rr${rr}_${sharded}_r${r}_i${i}
		if [ $genWorkload -eq 1 ]; then
			sudo python ./myRun/generate_test_rcs.py --distr $distr --alpha $alpha --read-ratio $rr --sharded $sharded --repeat $r --test-range $i -n $nCore --prefix $prefix
		else
			for l2_lat in $l2_lats
			do
				stats_file="myRun/stats/stats_${test}_clk${cpu_clock}_l2lat${l2_lat}.txt"
				term_file="myRun/term/term_${test}_clk${cpu_clock}_l2lat${l2_lat}.txt"
				if [ ! -f $term_file ]; then
					echo "" > $term_file
					build/ARM/gem5.opt -d tmp/output$thread configs/example/fs.py --kernel=./myFullSystemImages/fromGem5Website/binaries/vmlinux.arm64 --bootloader=./myFullSystemImages/fromGem5Website/binaries/boot.arm64 --disk-image=./myFullSystemImages/fromGem5Website/disks/aarch64-ubuntu-trusty-headless.img --disk-image=./myFullSystemImages/fromGem5Website/disks/aarch64-ubuntu-trusty-headless.img --mem-size=16GB --caches --l2cache --cpu-type=TimingSimpleCPU --script=./myScripts/test_${test}.rcS -r 1 --sys-clock $sys_clock --cpu-clock $cpu_clock -n 65 --l1_lat $l1_lat --l2_lat $l2_lat --l1i_size $l1i_size --l1d_size $l1d_size --l2_size $l2_size
					cp tmp/output$thread/stats.txt $stats_file
					cp tmp/output$thread/system.terminal $term_file
				fi
	
				if [ $get_result -eq 1 ]; then
					python ./myRun/extract_result.py --distr $distr --lat $l2_lat --alpha $alpha --read-ratio $rr --sharded $sharded --repeat $r --test-range $i -n $nCore --term-file $term_file >> ./myRun/result.txt
					#python ./myRun/extract_result.py >> ./myRun/result.txt
				fi
        		done
		fi
          done
	done
      done
    done
  done
done

fi

rm tmp/busy$thread
rm tmp/output$thread -r
