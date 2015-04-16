#!/bin/bash
BENCHMARKS_FOLDER=/u/s/w/swapnilh/private/simulators/gem5-gpu/benchmarks/
#RODINIA_DATA_FOLDER=/u/s/w/swapnilh/private/simulators/gem5-gpu/rodinia_2.4/data/
RODINIA_DATA_FOLDER=/u/s/w/swapnilh/private/simulators/gem5-gpu/benchmarks/rodinia-inputs/

#kmeans
#build/X86_VI_hammer_GPU/gem5.opt ../gem5-gpu/configs/se_fusion.py -c $BENCHMARKS_FOLDER/rodinia/kmeans/gem5_fusion_kmeans -o "-o -i $RODINIA_DATA_FOLDER/kmeans/100"

#srad
#build/X86_VI_hammer_GPU/gem5.opt ../gem5-gpu/configs/se_fusion.py -c $BENCHMARKS_FOLDER/rodinia/srad/gem5_fusion_srad -o "16 16 4 5 12 12 0.5 1"

#needleman wunscneedleman wunschh
#build/X86_VI_hammer_GPU/gem5.opt ../gem5-gpu/configs/se_fusion.py -c $BENCHMARKS_FOLDER/rodinia/nw/gem5_fusion_needle -o "32 5"

#lu decomposition
#build/X86_VI_hammer_GPU/gem5.opt ../gem5-gpu/configs/se_fusion.py -c $BENCHMARKS_FOLDER/rodinia/lud/gem5_fusion_lud -o "-v -i $RODINIA_DATA_FOLDER/lud/64.dat"

#hotspot
#build/X86_VI_hammer_GPU/gem5.opt ../gem5-gpu/configs/se_fusion.py -c $BENCHMARKS_FOLDER/rodinia/hotspot/gem5_fusion_hotspot -o "64 2 2 $RODINIA_DATA_FOLDER/hotspot/temp_64 $RODINIA_DATA_FOLDER/hotspot/power_64 hotspot.out"

#cell dim3 dim2 dim1 timesteps pyramid_height
#build/X86_VI_hammer_GPU/gem5.opt ../gem5-gpu/configs/se_fusion.py -c $BENCHMARKS_FOLDER/rodinia/cell/gem5_fusion_cell -o "8 8 8 1 1"

#bfs 
#build/X86_VI_hammer_GPU/gem5.opt ../gem5-gpu/configs/se_fusion.py -c $BENCHMARKS_FOLDER/rodinia/bfs/gem5_fusion_bfs -o "$RODINIA_DATA_FOLDER/bfs/SampleGraph.txt"

#nn
#build/X86_VI_hammer_GPU/gem5.opt ../gem5-gpu/configs/se_fusion.py -c /u/s/w/swapnilh/private/simulators/gem5-gpu/benchmarks/rodinia/nn/gem5_fusion_nn -o "/u/s/w/swapnilh/private/simulators/gem5_gpu/rodinia_2.4/data/nn/filelist.txt -r 3 -lat 30 -lng 90"

#backprop
#build/X86_VI_hammer_GPU/gem5.opt ../gem5-gpu/configs/se_fusion.py -c ../benchmarks/rodinia/backprop/gem5_fusion_backprop -o "16"
