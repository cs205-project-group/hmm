import graphlab
import numpy as np
import example
from sklearn import hmm
NUM_STATES = 4
NUM_OBSERVATIONS=4
OBSERVATION_LENGTH=6
np.random.seed(seed=1)


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
secretB = np.identity(NUM_STATES)

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
				y_t = observationSequence[t-1]
				alphaTable[i, t] = B[i, y_t] * np.dot(alphaTable[:, t-1], A[:, i])
		# http://digital.cs.usu.edu/~cyan/CS7960/hmm-tutorial.pdf
		# also based on other HMM small state space paper
		#if t == 1:
		#	return alphaTable[:,1]

		normalizers[t] = sum(alphaTable[:, t])
		print "t", normalizers[t]
        alphaTable[:, t] /= normalizers[t]
	return alphaTable
	betaTable = np.zeros((NUM_STATES, OBSERVATION_LENGTH+1))

	for t in reversed(xrange(OBSERVATION_LENGTH+1)):
		for i in xrange(NUM_STATES):
			if t == OBSERVATION_LENGTH:
				betaTable[i,t] = 1
			else:
				sm = 0
				y_t = observationSequence[t]
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
	for t in range(OBSERVATION_LENGTH):
		alpha_k_sum = np.dot(alphaTable[:, t], betaTable[:, t]) 
		for i in xrange(NUM_STATES):
			for j in xrange(NUM_STATES):
				y_t1 = observationSequence[t]
				xiTable[i, j] += alphaTable[i, t] * A[i, j] * betaTable[j, t+1] * B[j, y_t1] / (alpha_k_sum * normalizers[t+1])


	newA = np.zeros((NUM_STATES, NUM_STATES))
	for i in range(NUM_STATES):
		for j in range(NUM_STATES):
			newA[i, j] = xiTable[i, j] / (sum(gammaTable[i, :]))# - gammaTable[i, OBSERVATION_LENGTH-1])

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
	for observationSequence in sequences: 
		print np.linalg.norm(A - secretA)
		print np.linalg.norm(B - secretB)
		print np.linalg.norm(prior - secretPrior)
		for i in range(100):
			print 'Iteration %d' %i	
			A, B, prior =  train(A, B, prior, observationSequence)
			print "A error: ", np.linalg.norm(A - secretA)
			print "B error: ", np.linalg.norm(B - secretB)
			print "prior error: ", np.linalg.norm(prior - secretPrior)


def parallel(observationSequence):
	print "starting graph"
	g = SGraph()
	verticesEven = map(lambda i: Vertex(str(i) + " even", attr={'parity': 0, 'i': i, 'ait': [prior[i]] + ([0] * OBSERVATION_LENGTH), 'b': B[i, :]}), range(NUM_STATES))
	verticesOdd = map(lambda i: Vertex(str(i) + " odd", attr={'parity': 1, 'i': i, 'ait': [0] * OBSERVATION_LENGTH, 'b': B[i, :]}), range(NUM_STATES))

	print "set up vertices, add vertices.."
	g = g.add_vertices(verticesOdd + verticesEven)
	print "finshed adding vertices..starting edge appending"
	edges = []
	for i in range (NUM_STATES):
		for j in range (NUM_STATES):
			edges.append(Edge(str(i) + " even", str(j) + " odd", attr={'parity': 0, 'aij': A[i, j]}))
			edges.append(Edge(str(i) + " odd", str(j) + " even", attr={'parity': 1, 'aij': A[i, j]}))

	g = g.add_edges(edges)

	print "finished adding edges. calling example.fg..."
	#g = example.fp(g, observationSequence)
	print "finished calling example fg"
	print g.vertices
	#g.show()
	#import time
	#time.sleep(10000)

print train(A, B, prior, observationSequence)
parallel(sequences[0])

