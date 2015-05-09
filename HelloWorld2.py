import graphlab
import numpy as np
import example2
from sklearn import hmm
NUM_STATES = 4
NUM_OBSERVATIONS=8
OBSERVATION_LENGTH=10
np.random.seed(seed=1)

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--NUM_STATES", metavar="NUM_STATES", type=int, 
                   help="num states", default=4)
parser.add_argument("--NUM_OBSERVATIONS", metavar="NUM_OBSERVATIONS", type=int,
                   help="num observations", default=4)
parser.add_argument("--OBSERVATION_LENGTH", metavar="OBSERVATION_LENGTH", type=int, 
                   help="observation length", default=16)

args = parser.parse_args()
OBSERVATION_LENGTH = args.OBSERVATION_LENGTH
NUM_STATES = args.NUM_STATES
NUM_OBSERVATIONS = args.NUM_OBSERVATIONS

def randomHMM():
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

secretA, secretB, secretPrior = randomHMM()
#secretB = np.identity(NUM_STATES)

curState = np.random.choice(NUM_STATES, p=secretPrior)
sequences = []
for _ in range (1):
	observationSequence = np.zeros(OBSERVATION_LENGTH)
	for i in xrange(OBSERVATION_LENGTH):
		observationSequence[i] = np.random.choice(NUM_OBSERVATIONS, p=secretB[curState, :])
		curState = np.random.choice(NUM_STATES, p=secretA[curState, :])
	sequences.append(observationSequence)

def train(A, B, prior, observationSequence):
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
			gammaTable[i, t] = alphaTable[i, t] * betaTable[i, t] / np.dot(alphaTable[:, t], betaTable[:, t])
	newprior = gammaTable[:,0] # first column

	gammaTable = gammaTable[:, 1:]
	

	xiTable = np.zeros((NUM_STATES, NUM_STATES))
	for t in range(1,OBSERVATION_LENGTH):
		alpha_k_sum = np.dot(alphaTable[:, t], betaTable[:, t]) 
		for i in xrange(NUM_STATES):
			for j in xrange(NUM_STATES):
				y_t1 = int(observationSequence[t])
				xiTable[i, j] += alphaTable[i, t] * A[i, j] * betaTable[j, t+1] * B[j, y_t1] / (alpha_k_sum * normalizers[t+1])

	newA = np.zeros((NUM_STATES, NUM_STATES))
	for i in range(NUM_STATES):
		for j in range(NUM_STATES):
			newA[i, j] = xiTable[i, j] / (sum(gammaTable[i, :]))#  - gammaTable[i, OBSERVATION_LENGTH])

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

A, B, prior = secretA, secretB, secretPrior

from graphlab import SGraph, Vertex, Edge
def serial():
	global A, B, prior
	for observationSequence in sequences: 
		for i in range(10):
			print 'Iteration %d' %i	
			A, B, prior =  train(A, B, prior, observationSequence)
	print "A", A
	print "B", B

def parallel(A, B, prior, observationSequence):
	g = SGraph()

	vertices = map(lambda i: Vertex(str(i) + "a", attr={'i': i, 'ait': [prior[i]] +
		([0] * OBSERVATION_LENGTH), 'bit': ([0] * OBSERVATION_LENGTH) + [1],
		'b': B[i, :], 'git': [0] * (OBSERVATION_LENGTH + 1), 'self': A[i, i], 'git_sum': 0.0}),
		xrange(NUM_STATES))

	g = g.add_vertices(vertices)
	edges = []
	for i in xrange(NUM_STATES):
		for j in xrange(NUM_STATES):
			if i != j:
				edges.append(Edge(str(i) + "a", str(j) + "a", attr={'aij': A[i, j], 'xi': 0.0}))

	g = g.add_edges(edges)
	print observationSequence
	g = example2.fp(g, observationSequence, 10)
	print g.vertices
parallel(A, B, prior, sequences[0])
serial()

