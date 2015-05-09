#!/bin/bash 

#SBATCH -J graphlab # Name of your run
#SBATCH -t 900 #Runtime in minutes 
#SBATCH -p holyseasgpu #Partition to submit to 
#SBATCH -n 2 # number of CPUs

#SBATCH -o graphlab.out  # Name of file to store output
#SBATCH -e graphlab.err  # Name of file to store stderr

#SBATCH --mail-user=your email here # Add your email address to be
                                                # notified when
#SBATCH --mail-type=BEGIN # The run began
#SBATCH --mail-type=END # The run ended
#SBATCH --mem-per-cpu=500 # in MB

source new-modules.sh
module load python/2.7.6-fasrc01
source activate graphlab

module load legacy
module load centos6/gcc-4.8.0

which python

python HelloWorld2.py

