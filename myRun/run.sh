#!/bin/sh

root="/home/kuofeng/myGitRepos/gem5"
cd $root


step=0
# 0: genWorkload, 1: run gem5, 2: get_result, 3: get_cache_ctrl
#prefix="rwself_smallLat_withkey_notime_uint64_notsimplified_fc_notslow_notlocal_pt_se_fw_ns_mc" # abbrv"fixClkProb_slow_local_pointer_singleEntry_fixWrite_nosleep_manycore"
prefix="thresh_rwself_smallLat_withkey_notime_uint64_notsimplified_fc_notslow_notlocal_pt_se_fw_ns_mc" # abbrv"fixClkProb_slow_local_pointer_singleEntry_fixWrite_nosleep_manycore"
#prefix="heterClk_thresh_rwself_smallLat_withkey_notime_uint64_notsimplified_fc_notslow_notlocal_pt_se_fw_ns_mc" # abbrv"fixClkProb_slow_local_pointer_singleEntry_fixWrite_nosleep_manycore"
distr="rackout"

#find available output direcotry
thread=0
while [ -f tmp/busy$thread ]
do
	thread=$((thread+1))
done
echo "" > tmp/busy$thread
cp tmp/output tmp/tmpOutput$thread -r

if [ $step -eq 2 ] || [ $step -eq 3 ]; then
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
			build/ARM/gem5.opt -d tmp/tmpOutput$thread configs/example/fs.py --kernel=./myFullSystemImages/fromGem5Website/binaries/vmlinux.arm64 --bootloader=./myFullSystemImages/fromGem5Website/binaries/boot.arm64 --disk-image=./myFullSystemImages/fromGem5Website/disks/aarch64-ubuntu-trusty-headless.img --disk-image=./myFullSystemImages/fromGem5Website/disks/aarch64-ubuntu-trusty-headless.img --mem-size=16GB --caches --l2cache --l2_lat $lat -n 3 --cpu-type=TimingSimpleCPU --script=./myScripts/test_${rw}_${sharded}_r${r}_i$i.rcS -r 1
			cp tmp/tmpOutput$thread/stats.txt $stats_file
			cp tmp/tmpOutput$thread/system.terminal $term_file
		fi

		if [ $step -eq 2 ]; then
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

alphas="0.250 0.354 0.500 0.707 0.990 1.414 2.000"
#alphas="0.001 0.500 0.600 0.700 0.800 0.990"
#alphas="0.990"
#rrs="0.000 0.250 0.500 0.750 0.950 1.000"
#rrs="0.000 1.000"
rrs="0.950"
shardeds="threshold shared sharded"
#shardeds="shared sharded"
#shardeds="shared wrr_shared"
#shardeds="shared"
#probThr="0.0025 0.0050 0.0100 0.0200 0.0400"
probThr="0.0050"
#rs="2000000"
rs="500000"
is="32768"
#is="1"
#lats="2000 3000 4000 5000 10000 20000 30000 40000 50000"
#nCores="1 2 4 6 8" # the number of cores are always 9; this is more about cores used by NIC threads
nCores="6" # the number of cores are always 9; this is more about cores used by NIC threads
#nCores="1 2 4 6 8 10 12 14 16" # the number of cores are always 9; this is more about cores used by NIC threads
#nCores="1 8 16 24 32 40" # the number of cores are always 9; this is more about cores used by NIC threads
#nCores="1 2 4 6 8 12 24 50" # the number of cores are always 9; this is more about cores used by NIC threads

# system parameters
sys_clock="500MHz"
#sys_clock="100MHz"

#clk_separates="50 100 200"
clk_separates="50"
#clk_type_counts="0 2 6"
clk_type_counts="0"
cpu_clock="633MHz"
#cpu_clock="180MHz"

#l1_lat="60"
#l1_lat="75"
l1_lat="12"
#l2_lats="125 250 500 1000"
#l2_lats="125"
#l2_lats="150 300 600 1200"
#l2_lats="150"
#l2_lats="25 100 500 1000 2000 4000"
l2_lats="25 1000"
l1d_size="64kB"
l1i_size="32kB"
l2_size="2MB"
#l1d_size="32MB"
#l2_size="1GB"


for l2_lat in $l2_lats
do
  for alpha in $alphas
  do
    for r in $rs
    do
      for rr in $rrs
      do
        for i in $is
        do
          for nCore in $nCores
          do
            for sharded in $shardeds
            do
              for p in $probThr
              do
                for sep in $clk_separates
                do
                  for tc in $clk_type_counts
                  do
	                if [ "$tc" = "0" ]; then
				heter_str=""
				heter_cmd="--heter-cpu-clock 0 --clk-separate 0 --clk-type-count 0"
			else
				heter_str="_heter_sep${sep}_tc${tc}"
				heter_cmd="--heter-cpu-clock 1 --clk-separate $sep --clk-type-count $tc"
			fi
	
			if [ "$sharded" = "threshold" ]; then
				test=${prefix}_${distr}_n${nCore}_a${alpha}_rr${rr}_${sharded}_p${p}_r${r}_i${i}
			elif [ "$sharded" = "wrr_shared" ] && [ "$tc" != "0" ]; then
				test=${prefix}_${distr}_n${nCore}_a${alpha}_rr${rr}_${sharded}_clk${cpu_clock}_sep${sep}_tc${tc}_r${r}_i${i}
			else
				if [ "$sharded" = "wrr_shared" ]; then
					test=${prefix}_${distr}_n${nCore}_a${alpha}_rr${rr}_shared_r${r}_i${i}
				else
					test=${prefix}_${distr}_n${nCore}_a${alpha}_rr${rr}_${sharded}_r${r}_i${i}
				fi
			fi
			stats_file="myRun/stats/stats_${test}_clk${cpu_clock}_l2lat${l2_lat}${heter_str}.txt"
			cache_file="myRun/cache/cache_${test}_clk${cpu_clock}_l2lat${l2_lat}${heter_str}.trc.gz"
			term_file="myRun/term/term_${test}_clk${cpu_clock}_l2lat${l2_lat}${heter_str}.txt"
	
			if [ $step -eq 0 ]; then
				sudo python ./myRun/generate_test_rcs.py --distr $distr --alpha $alpha --read-ratio $rr --sharded $sharded --probThr $p --repeat $r --test-range $i -n $nCore --prefix $prefix --cpu-clock $cpu_clock --clk-separate $sep --clk-type-count $tc
			elif [ $step -eq 2 ]; then
				python ./myRun/extract_result.py --distr $distr --lat $l2_lat --alpha $alpha --read-ratio $rr --sharded $sharded --probThr $p --repeat $r --test-range $i -n $nCore --term-file $term_file $heter_cmd >> ./myRun/result.txt
				#python ./myRun/extract_result.py >> ./myRun/result.txt
			elif [ $step -eq 1 ]; then
				if [ ! -f $term_file ]; then
					echo "" > $term_file
					build/ARM/gem5.opt -d tmp/tmpOutput$thread configs/example/fs.py --kernel=./myFullSystemImages/fromGem5Website/binaries/vmlinux.arm64 --bootloader=./myFullSystemImages/fromGem5Website/binaries/boot.arm64 --disk-image=./myFullSystemImages/fromGem5Website/disks/aarch64-ubuntu-trusty-headless.img --disk-image=./myFullSystemImages/fromGem5Website/disks/aarch64-ubuntu-trusty-headless.img --mem-size=16GB --caches --l2cache --cpu-type=TimingSimpleCPU --script=./myScripts/test_${test}.rcS -r 1 --sys-clock $sys_clock --cpu-clock $cpu_clock -n 65 --l1_lat $l1_lat --l2_lat $l2_lat --l1i_size $l1i_size --l1d_size $l1d_size --l2_size $l2_size $heter_cmd
					cp tmp/tmpOutput$thread/stats.txt $stats_file
					cp tmp/tmpOutput$thread/mytrace.trc.gz $cache_file
					cp tmp/tmpOutput$thread/system.terminal $term_file
				fi
			elif [ $step -eq 3 ]; then
				python util/decode_packet_trace.py $cache_file myRun/tmpCache.txt > myRun/tmpPktCount.txt
				python ./myRun/extract_result.py --distr $distr --lat $l2_lat --alpha $alpha --read-ratio $rr --sharded $sharded --probThr $p --repeat $r --test-range $i -n $nCore $heter_cmd --cache-file myRun/tmpPktCount.txt >> ./myRun/result.txt
				rm myRun/tmpPktCount.txt
				rm myRun/tmpCache.txt
			fi
                  done
                done
              done
            done
          done
	done
      done
    done
  done
done

fi

rm tmp/busy$thread
rm tmp/tmpOutput$thread -r
