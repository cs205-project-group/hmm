import graphlab
import numpy as np
import example2
from sklearn import hmm
import time
import argparse

# set random seed
np.random.seed(seed=1)


# read arguments from command line
parser = argparse.ArgumentParser()
parser.add_argument("--NUM_STATES", metavar="NUM_STATES", type=int, 
                   help="num states", default=4)
parser.add_argument("--NUM_OBSERVATIONS", metavar="NUM_OBSERVATIONS", type=int,
                   help="num observations", default=4)
parser.add_argument("--OBSERVATION_LENGTH", metavar="OBSERVATION_LENGTH", type=int, 
                   help="observation length", default=16)
parser.add_argument("--niters", metavar="niters", type=int, default=5,
help="Number of iterations to run")

args = parser.parse_args()
OBSERVATION_LENGTH = args.OBSERVATION_LENGTH
NUM_STATES = args.NUM_STATES
NUM_OBSERVATIONS = args.NUM_OBSERVATIONS
NITERS = args.niters

def randomHMM():
	# generate normalized, uniformly random parameters for HMM
	A = np.random.rand(NUM_STATES, NUM_STATES)
	# normalization from
	# http://stackoverflow.com/questions/8904694/how-to-normalize-a-2-dimensional-numpy-array-in-python-less-verbose
	A /= A.sum(axis=1)[:, np.newaxis]
	B = np.random.uniform(0, 1, size=(NUM_STATES, NUM_OBSERVATIONS))
	B /= B.sum(axis=1)[:, np.newaxis]
	prior = np.ones(NUM_STATES)
	prior /= prior.sum()
	return (A, B, prior)

def uniformHMM():
	# generate uniform (e.g. 1/NUM_STATES) parameters for HMM
	A = np.ones((NUM_STATES, NUM_STATES))
	# normalization from
	# http://stackoverflow.com/questions/8904694/how-to-normalize-a-2-dimensional-numpy-array-in-python-less-verbose
	A /= A.sum(axis=1)[:, np.newaxis]
	B = np.ones((NUM_STATES, NUM_OBSERVATIONS))
	#B = np.random.uniform(0, 1, size=(NUM_STATES, NUM_OBSERVATIONS))
	B /= B.sum(axis=1)[:, np.newaxis]

	prior = np.ones(NUM_STATES)
	prior /= prior.sum()

	return (A, B, prior)


def train(A, B, prior, observationSequence):
	# one iteration of serial training algorithm for HMM
	alphaTable = np.zeros((NUM_STATES, OBSERVATION_LENGTH +1))
	# http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.334.1331&rep=rep1&type=pdf
	normalizers = np.zeros(OBSERVATION_LENGTH+1)

	# compute forward probabilities
	for t in xrange(OBSERVATION_LENGTH+1):
		for i in xrange(NUM_STATES):
			if t == 0:
				alphaTable[i, t] = prior[i]
			else:
				y_t = int(observationSequence[t-1])
				alphaTable[i, t] = B[i, y_t] * np.dot(alphaTable[:, t-1], A[:, i])
		# http://digital.cs.usu.edu/~cyan/CS7960/hmm-tutorial.pdf
		# also based on other HMM small state space paper

		normalizers[t] = sum(alphaTable[:, t])
		alphaTable[:, t] /= normalizers[t]

	betaTable = np.zeros((NUM_STATES, OBSERVATION_LENGTH+1))

	for t in reversed(xrange(OBSERVATION_LENGTH+1)):
		for i in xrange(NUM_STATES):
			if t == OBSERVATION_LENGTH:
				betaTable[i,t] = 1
			else:
				sm = 0
				y_t = int(observationSequence[t])
				for j in range(NUM_STATES):
					sm += betaTable[j, t+1] * A[i, j] * B[j, y_t]	
				betaTable[i,t] = sm

		if t < OBSERVATION_LENGTH:
			betaTable[:, t] /= normalizers[t+1]

	gammaTable = np.zeros((NUM_STATES, OBSERVATION_LENGTH + 1))
	for i in range (NUM_STATES):
		for t in range(OBSERVATION_LENGTH + 1):
			gammaTable[i, t] = (alphaTable[i, t] * betaTable[i, t] /
			np.dot(alphaTable[:, t], betaTable[:, t]))
	newprior = gammaTable[:,0] # first column

	gammaTable = gammaTable[:, 1:]
	

	xiTable = np.zeros((NUM_STATES, NUM_STATES))
	for t in range(1,OBSERVATION_LENGTH):
		alpha_k_sum = np.dot(alphaTable[:, t], betaTable[:, t]) 
		for i in xrange(NUM_STATES):
			for j in xrange(NUM_STATES):
				y_t1 = int(observationSequence[t])
				xiTable[i, j] += (alphaTable[i, t] * A[i, j] * betaTable[j, t+1]
						* B[j, y_t1] / (alpha_k_sum * normalizers[t+1]))

	newA = np.zeros((NUM_STATES, NUM_STATES))
	for i in range(NUM_STATES):
		for j in range(NUM_STATES):
			newA[i, j] = xiTable[i, j] / (sum(gammaTable[i, :]))

	newB = np.zeros((NUM_STATES, NUM_OBSERVATIONS))
	for i in xrange(NUM_STATES):
		for j in xrange(NUM_OBSERVATIONS):
			s = 0
			ss = 0
			for t in xrange(OBSERVATION_LENGTH):
				if j == observationSequence[t]:
					s += gammaTable[i, t]
				ss += gammaTable[i, t]	
			newB[i, j] = s / ss	

	return(newA, newB, newprior)



def serial():
	# serial training of HMMs
	global A, B, prior
	for observationSequence in sequences: 
		for i in range(NITERS):
			#print 'Iteration %d' %i	
			A, B, prior =  train(A, B, prior, observationSequence)
	print "A", A
	print "B", B


from graphlab import SGraph, Vertex, Edge

def parallel(A, B, prior, observationSequence):
	# parallel HMM training with graphlab
	g = SGraph()

	vertices = map(lambda i: Vertex(str(i) + "a", 
		attr={'i': i, 'ait': [prior[i]] + ([0] * OBSERVATION_LENGTH), 
			'bit': ([0] * OBSERVATION_LENGTH) + [1], 
			'b': B[i, :], 'git': [0] * (OBSERVATION_LENGTH + 1), 
			'self': A[i, i], 'git_sum': 0.0}), xrange(NUM_STATES))

	g = g.add_vertices(vertices)
	edges = []
	for i in xrange(NUM_STATES):
		for j in xrange(NUM_STATES):
			if i != j:
				edges.append(Edge(str(i) + "a", str(j) + "a", 
					attr={'aij': A[i, j], 'xi': 0.0}))

	g = g.add_edges(edges)
	g = example2.fp(g, observationSequence, NITERS)
	print g.vertices

# make sure you run parallel before serial, because serial mutates the
# parameters
# the true parameters
secretA, secretB, secretPrior = randomHMM()

# simulate the sequence
curState = np.random.choice(NUM_STATES, p=secretPrior)
sequences = []
for _ in range (1):
	observationSequence = np.zeros(OBSERVATION_LENGTH)
	for i in xrange(OBSERVATION_LENGTH):
		observationSequence[i] = np.random.choice(NUM_OBSERVATIONS, 
				p=secretB[curState, :])
		curState = np.random.choice(NUM_STATES, p=secretA[curState, :])
	sequences.append(observationSequence)

# starting parameters
A, B, prior = randomHMM()

parallel_start = time.time()
parallel(A, B, prior, sequences[0])
parallel_elapsed = time.time() - parallel_start

serial_start = time.time()
serial()
serial_elapsed = time.time() - serial_start

print("Serial time: " + str(serial_elapsed))
print("Parallel time: " + str(parallel_elapsed))

#NUM_STATES, NUM_OBSERVATIONS, OBSERVATION_LENGTH, serial_elapsed, parallel_elapsed 
print("%d,%d,%d,%e,%e" %(NUM_STATES, NUM_OBSERVATIONS, OBSERVATION_LENGTH,
	serial_elapsed, parallel_elapsed))
