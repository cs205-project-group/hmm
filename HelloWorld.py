import numpy as np
NUM_STATES = 10
NUM_OBSERVATIONS=5
OBSERVATION_LENGTH=100

np.random.seed(seed=1)


def randomHMM():
	A = np.random.rand(NUM_STATES, NUM_STATES)
	# normalization from
	# http://stackoverflow.com/questions/8904694/how-to-normalize-a-2-dimensional-numpy-array-in-python-less-verbose
	A /= A.sum(axis=1)[:, np.newaxis]

	B = np.random.uniform(0, 1, size=(NUM_STATES, NUM_OBSERVATIONS))
	B /= B.sum(axis=1)[:, np.newaxis]

	prior = np.random.uniform(0, 1, size=(NUM_STATES))
	prior /= prior.sum()
	return (A, B, prior)

secretA, secretB, secretPrior = randomHMM()

# generate testing observation sequence
curState = np.random.choice(NUM_STATES, p=secretPrior)
observationSequence = np.zeros(OBSERVATION_LENGTH)
for i in xrange(OBSERVATION_LENGTH):
	observationSequence[i] = np.random.choice(NUM_OBSERVATIONS, p=secretB[curState, :])
	curState = np.random.choice(NUM_STATES, p=secretA[curState, :])

print observationSequence


def train(A, B, prior, observationSequence):
	alphaTable = np.zeros((NUM_STATES, OBSERVATION_LENGTH))

	# compute forward probabilities
	for t in xrange(OBSERVATION_LENGTH):
		for i in xrange(NUM_STATES):
			if t == 0:
				y_0 = observationSequence[0]
				alphaTable[i, t] = prior[i] * B[i, y_0]
			else:
				y_t = observationSequence[t]
				alphaTable[i, t] = B[i, y_t] * np.dot(alphaTable[:, t-1], A[:, i])

	betaTable = np.zeros((NUM_STATES, OBSERVATION_LENGTH))

	for t in reversed(xrange(OBSERVATION_LENGTH)):
		for i in xrange(NUM_STATES):
			if t == OBSERVATION_LENGTH-1:
				betaTable[i,t] = 1
			else:
				Bj_aij = betaTable[:,t+1] * A[i,:]
				y_t = observationSequence[t+1]
				betaTable[i,t] = np.dot(Bj_aij, B[:,y_t])

	gammaTable = (alphaTable * betaTable) # matrix element-wise mult
	gammaTable = gammaTable / np.sum(gammaTable, axis=0) #[:, np.newaxis]

	xiTable = np.zeros((NUM_STATES, NUM_STATES))

		
	for i in xrange(NUM_STATES):
		row = np.zeros(NUM_STATES)
		for t in reversed(xrange(OBSERVATION_LENGTH-1)):
			y_t1 = observationSequence[t+1]
			Bj_yt1 = B[:,y_t1]
			row += ((alphaTable[i,t] * betaTable[:,t+1] * Bj_yt1 * A[i,:]) / 
					np.dot(alphaTable[:,t], betaTable[:,t]))
		xiTable[i] = row
	
	newprior = gammaTable[:,0] # first column
	#print "Prior sum is: ", np.sum(newprior)
	#print newprior
	# sum over all columns except last
	newA = xiTable / np.sum(gammaTable[:,:-1], axis=1)#[:, np.newaxis]
	newB = np.zeros((NUM_STATES, NUM_OBSERVATIONS))
	
	for i in xrange(NUM_OBSERVATIONS):
		curMask = np.array(observationSequence == i, dtype=np.int32)
		mask = np.tile(curMask, (NUM_STATES,1))
		row = np.sum(mask * gammaTable)
		newB[:,i] = row / np.sum(gammaTable, axis=1)

	return(newA, newB, newprior)


A, B, prior = randomHMM()	
print 'pre-update'
print A.shape
print B.shape
print prior.shape

print 'initial badness'
print np.linalg.norm(A - secretA)
print np.linalg.norm(B - secretB)
print np.linalg.norm(prior - secretPrior)

for i in xrange(50):	
	print 'Iteration %d' %i	
	A, B, prior =  train(A, B, prior, observationSequence)
print np.linalg.norm(A - secretA)
print np.linalg.norm(B - secretB)
print np.linalg.norm(prior - secretPrior)
#print A
#print B
print prior
print secretPrior
