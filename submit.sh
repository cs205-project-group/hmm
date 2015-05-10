#!/bin/bash 

# compile first
module load centos6/gcc-4.8.0
g++ -std=c++11 example2.cpp -I ../graphlab-sdk -shared -fPIC -o example2.so

mkdir outfiles
for CORES in 2 4 8 16 32
do
    for NUM_OBSERVATIONS in 4 16 64 256 1024 4096  
    do
        for OBSLEN in 100 200 500 #1000
        do
            echo "Cores: ${CORES}, NUM_STATES/NUM_OBSERVATIONS: ${NUM_OBSERVATIONS}, OBSERVATION_LENGTH: ${OBSLEN}"
            export NUM_OBSERVATIONS OBSLEN
            mem=$(( ${NUM_OBSERVATIONS} * ${OBSLEN} / 100 ))
            if [ $mem -lt 500 ]
            then 
                mem=500
            fi
            echo "$mem"
            sbatch -o outfiles/hmm_c${CORES}_n${NUM_OBSERVATIONS}_l${OBSLEN}.out \
                -e outfiles/hmm_c${CORES}_n${NUM_OBSERVATIONS}_l${OBSLEN}.err \
                --job-name=hmm_c${CORES} \
                -n ${CORES} --mem=${mem} submit.sbatch
            echo "Done submitting"
            sleep 1 # pause to be kind to the scheduler
        done
    done
done
