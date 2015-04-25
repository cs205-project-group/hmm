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
observationSequence = []
for i in range (OBSERVATION_LENGTH):
	observationSequence.append(np.random.choice(NUM_OBSERVATIONS, p=secretB[curState, :]))
	curState = np.random.choice(NUM_STATES, p=secretA[curState, :])

print observationSequence


def train(A, B, prior):
	alphaTable = np.zeros((NUM_STATES, OBSERVATION_LENGTH))

	# compute forward probabilities
	for t in range(OBSERVATION_LENGTH):
		for i in range(NUM_STATES):
			if t == 0:
				y_0 = observationSequence[0]
				alphaTable[i, t] = prior[i] * B[i, y_0]
			else:
				y_t = observationSequence[t]
				alphaTable[i, t] = B[i, y_t] * np.dot(alphaTable[:, t-1], A[:, i])

	betaTable = np.zeros

A, B, prior = randomHMM()			
print train(A, B, prior)
