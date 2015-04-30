num_states = 4;
num_observations = 4;
observation_length = 100000;

A = random('unif', 0, 1, [num_states, num_states]);
A = A ./ repmat(sum(A, 2), [1,num_states]);

B = random('unif', 0, 1, [num_states, num_observations]);
B = B ./ repmat(sum(B,2), [1,num_observations]);

% B = [[0.88 0.1 0.01 0.01];[0 0.8 0.2 0]; [0.1 0.1 0.76 0.04]; [0 0.05 0 0.95]];
B = eye(4);
[seq, states] = hmmgenerate(observation_length, A, B);


Aguess = random('unif', 0, 1, [num_states, num_states]);
Aguess = Aguess ./ repmat(sum(Aguess, 2), [1,num_states]);

Bguess = random('unif', 0, 1, [num_states, num_observations]);
Bguess = Bguess ./ repmat(sum(Bguess,2), [1,num_observations]);
disp('training..')
[tranEst, emitEst] = hmmtrain(seq, Aguess, Bguess);
