num_states = 4;
num_observations = 4;
observation_length = 3;

%A = random('unif', 0, 1, [num_states, num_states]);
%A = A ./ repmat(sum(A, 2), [1,num_states]);

%B = random('unif', 0, 1, [num_states, num_observations]);
%B = B ./ repmat(sum(B,2), [1,num_observations]);

% B = [[0.88 0.1 0.01 0.01];[0 0.8 0.2 0]; [0.1 0.1 0.76 0.04]; [0 0.05 0 0.95]];
A = [[ 0.1199935   0.0928339   0.30811417  0.14722959  0.33182885];
 [ 0.23700395  0.22209093  0.04099118  0.33918997  0.16072397];
 [ 0.2141698   0.1511275   0.08776786  0.33450914  0.2124257 ];
 [ 0.00121642  0.26153972  0.13842878  0.22336185  0.37545323];
 [ 0.12604671  0.32053613  0.21992483  0.00558182  0.3279105 ]]

B = eye(5);

seq = 1 + [ 4.  0.  1.  0.  2.  0.  2.  3.  2.  1.  0.  4.  1.  1.  3.  2.]
;
[tranEst, emitEst] = hmmtrain(seq, A, B, 'Maxiterations', 1);
