from cvxopt import matrix, log, exp, solvers

Rint = 0.48
Cin = 4
Cint = 6
Cext = 10
A = 8.0


"""
  D1 = 0.69*Rint*Cint + 0.69*Rint*Cin* x1^-1 * x2  
  D2 = 0.69*Rint*Cint + 0.69*Rint*Cext * x2^-1
"""

F = matrix([[ 0.,  0.,  1.,  0.],
            [ 0.,  0.,  0.,  1.],
            [-1.,  1., -1.,  0.],
            [ 0.,  0., -1.,  0.],
            [ 0.,  0.,  0., -1.],
            [ 0., -1.,  0., -1.],
            [ 1.,  0.,  0.,  0.],
            [ 0.,  1.,  0.,  0.]])


Amax = 0.000001

g = log( matrix( [1., 1., 0.69*Rint*Cin, 0.69*Rint*Cint, 0.69*Rint*Cint, 0.69*Rint*Cext, A/Amax, A/Amax]))
print matrix( [1., 1., 0.69*Rint*Cin, 0.69*Rint*Cint, 0.69*Rint*Cint, 0.69*Rint*Cext, A/Amax, A/Amax])
K = [2, 2, 2, 2]


result = exp( solvers.gp(K, F.trans(), g)['x'] )
print result

