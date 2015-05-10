#!/bin/bash 

for CORES in 1 2 #4 8 16 32
do
    for NUM_OBSERVATIONS in 4 #16 64 256 1024 4096 8192 16384
    do
        for OBSLEN in 100 #1000 10000
        do
            echo "Cores: ${CORES}, NUM_STATES/NUM_OBSERVATIONS: ${NUM_OBSERVATIONS}, OBSERVATION_LENGTH: ${OBSLEN}"
            export CORES NUM_OBSERVATIONS OBSLEN
            sbatch -o hmm_c${CORES}_n${NUM_OBSERVATIONS}_l${OBSLEN}.out \
                -e hmm_c${CORES}_n${NUM_OBSERVATIONS}_l${OBSLEN}.err \
                --job-name=hmm_c${CORES}_n${NUM_OBSERVATIONS}_l${OBSLEN} \
                -n ${CORES} submit.sbatch
            echo "Done submitting"
            sleep 1 # pause to be kind to the scheduler
        done
    done
done
