#!/bin/bash 

#SBATCH -N 1 # on one machine
#SBATCH -t 900 #Runtime in minutes 
#SBATCH -p holyseasgpu #Partition to submit to 

source new-modules.sh
module load python/2.7.6-fasrc01
source activate graphlab

module load legacy
module load centos6/gcc-4.8.0

# which python are we using
which python

# actually run the program
python HelloWorld2.py --NUM_STATES ${NUM_OBSERVATIONS} --NUM_OBSERVATIONS ${NUM_OBSERVATIONS} --OBSERVATION_LENGTH ${OBSLEN}
