# hmm
### Harvard CS 205 Final Project, Spring 2015. 
### Andy Shi, Ding Zhou, Kevin Schmid

**Parallel hidden markov model in Dato GraphLab**

To run, first ensure that GraphLab module is installed. This can be found at https://dato.com/download/

Download Dato GraphLab SDK by following the instructions at https://github.com/dato-code/GraphLab-Create-SDK

In the code directory, compile the hmm.cpp file by following the instructions in compile.txt.

Finally, the code can be run by 

	usage: runhmm.py [-h] [--NUM_STATES NUM_STATES]
                 [--NUM_OBSERVATIONS NUM_OBSERVATIONS]
                 [--OBSERVATION_LENGTH OBSERVATION_LENGTH] [--niters niters]

	optional arguments:
	  -h, --help            show this help message and exit
  	  o
	--NUM_STATES NUM_STATES
    			num states
  	--NUM_OBSERVATIONS NUM_OBSERVATIONS
        	       	num observations
	--OBSERVATION_LENGTH OBSERVATION_LENGTH
        	        observation length
	--niters niters
			Number of iterations to run

(Command-line argument usage instructions obtained from Python argparse default "help" output.)
  
The default values for these are 4,4,16,5, respectively. 

**Running this on Odyssey**





