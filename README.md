# hmm
### Harvard CS 205 Final Project, Spring 2015. 
### Andy Shi, Ding Zhou, Kevin Schmid

## Parallel hidden markov model in Dato GraphLab

To run, first ensure that GraphLab module is installed. This can be found at https://dato.com/download/

Download Dato GraphLab SDK by following the instructions at https://github.com/dato-code/GraphLab-Create-SDK

In the code directory, compile the `hmm.cpp` file by following the instructions in `compile.txt`.

Finally, the code can be run by 
```
usage: runhmm.py [-h] [--NUM_STATES NUM_STATES]
                 [--NUM_OBSERVATIONS NUM_OBSERVATIONS]
                 [--OBSERVATION_LENGTH OBSERVATION_LENGTH] [--niters niters]

optional arguments:
  -h, --help            show this help message and exit
--NUM_STATES NUM_STATES
		num states
  --NUM_OBSERVATIONS NUM_OBSERVATIONS
		num observations
--OBSERVATION_LENGTH OBSERVATION_LENGTH
		observation length
--niters niters
		Number of iterations to run
```
(Command-line argument usage instructions obtained from Python argparse default "help" output.)
  
The default values for these are 4, 4, 16, and 5, respectively. 

## Running this on [Odyssey](rc.fas.harvard.edu)
Please follow the instructions in `odyssey-setup.txt` for installation instructions, and `submit.sh` for the job submission script (note that this calls `submit.sbatch`). 

## Data Analysis
Both the data and the code to analyze the data are found in the analysis folder. 
* `data.csv`: runtime data from Odyssey. Rows with 1 column only correspond to jobs which failed because of time constraints
* `drawPlots.R`: R code to generate the figures for our paper
* `fullout.csv`: full data, including the Odyssey output files from which each row of data came from
* `gather.sh`: Shell script to organize data from Odyssey output files into csv files. 

## Paper
Please find the files for our paper and its associated figures in the paper and figure folders, respectively. 
