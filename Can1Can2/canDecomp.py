import numpy as np
import itertools
import scipy

ATOL = 1E-3

np.set_printoptions(suppress=True)

# Canonical to magic basis matrix mapping
Q = np.asarray(
    [[1, 0, 0, 1j], [0, 1j, 1, 0], [0, 1j, -1, 0], [1, 0, 0, -1j]]
) / np.sqrt(2)
# Q dagger
Q_H = Q.conj().T

# Pauli single-qubit operator matrices
I = [[1, 0],[0, 1]]
X = [[0, 1],[1, 0]]
Y = [[0, 1j],[-1j, 0]]
Z = [[1, 0],[0, -1]]

# Tensor product of pauli matrices
XX = np.kron(X,X)
YY = np.kron(Y,Y)
ZZ = np.kron(Z,Z)

#=====================================
# ======== Input 2-qubit Gate ========
# *all the gates are written as horizontal concatenations
# of column vectors

# CNOT with det() = 1
# U = np.asarray(
#     [[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]
# )
#-----------------------------

# Example from paper (for debugging purposes)
# U = np.asarray(
#     [[1, 0, 0, 1], [0, 1, 1, 0], [0, 1, -1, 0], [1, 0, 0, -1]]
# )/np.sqrt(2)
#-----------------------------

# QFT 
# U = np.asarray(
#     [[1, 1, 1, 1], [1, 1j, -1, -1j], [1, -1, 1, -1], [1, -1j, -1, 1j]]
# )/2
#-----------------------------

# Swap Gate
# U = np.asarray(
#     [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]
# )
#-----------------------------

# Controlled Z Gate
# U = np.asarray(
#     [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]]
# )
#-----------------------------

# Controlled V Gate
# U = np.asarray(
#     [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, (1+1j)/2, (1-1j)/2], [0, 0, (1-1j)/2, (1+1j)/2]]
# )
#-----------------------------

# sqrt(SWAP) Gate
# U = np.asarray(
#     [[1, 0, 0, 0], [0, (1+1j)/2, (1-1j)/2, 0], [0, (1-1j)/2, (1+1j)/2, 0], [0, 0, 0, 1]]
# )
#-----------------------------

# The Magic Gate itself (Q)
U = np.asarray(
    [[1, 0, 0, 1j], [0, 1j, 1, 0], [0, 1j, -1, 0], [1, 0, 0, -1j]]
) / np.sqrt(2)
#-----------------------------

# --------------------------------------
# --------------------------------------
# --------------------------------------
# Starting decomposition

# Transform input 2-qubit gate to the magic basis
U_mb = Q_H @ U @ Q
# Find matrix M = Q^T * Q. This matrix will be used to extract the eigenvalues of the canonical gate
# in the magic basis as well as the tensor product of the single-qubit operations before and after
# the application of the canonical gate.
M = U_mb.transpose() @ U_mb

# Decompose the matrix M using an orthogonal eigenvector basis.
for i in range(16):
    c = np.random.uniform(0,1)
    auxM = c*M.real + (1-c)*M.imag
    _, eigvecs = np.linalg.eigh(auxM)
    eigvecs = np.array(eigvecs, dtype=complex)
    eigvals = np.diag(eigvecs.transpose() @ M @ eigvecs)

    reconstructed = eigvecs @ np.diag(eigvals) @ eigvecs.transpose()
    if np.allclose(M,reconstructed):
        break

# Use the eigenvalues of the matrix M to determine the coordinates of the canonical gate.
lambdas = np.sqrt(eigvals)
try:
    for permutation in itertools.permutations(range(4)):
        for signs in ([1, 1, 1, 1], [1, 1, -1, -1], [-1, 1, -1, 1], [1, -1, -1, 1]):
            signed_lambdas = lambdas * np.asarray(signs)
            perm = list(permutation)
            lambdas_perm = signed_lambdas[perm]

            l1, l2, l3, l4 = lambdas_perm
            tx = np.real(1j/4 * np.log(l1*l2/(l3*l4))) / np.pi
            ty = np.real(1j/4 * np.log(l2*l4/(l1*l3))) / np.pi
            tz = np.real(1j/4 * np.log(l1*l4/(l2*l3))) / np.pi

            coords = np.asarray([tx,ty,tz])
            coords[np.abs(coords-1) < ATOL] = -1
            if all(coords<0):
                coords += 1
            if np.abs(coords[0] - coords[1]) < ATOL:
                coords[1] = coords[0]
            if np.abs(coords[1] - coords[2]) < ATOL:
                coords[2] = coords[1]
            if np.abs(coords[0] - coords[1] - 1 / 2) < ATOL:
                coords[1] = coords[0] - 1 / 2
            coords[np.abs(coords) < ATOL] = 0

            tx, ty, tz = coords

            # Check whether coordinates are inside the Weyl Chamber
            if (1/2 >= tx >= ty >= tz >= 0) or (1/2 >= (1-tx) >= ty >= tz > 0):
                print('pass')
                raise StopIteration

except StopIteration:
    pass


lambdas = (lambdas*signs)[perm]
O2 = (np.diag(signs) @ eigvecs.transpose())[perm]
F = np.diag(lambdas)
O1 = U_mb @ O2.transpose() @ F.conj()

neg = np.diag([-1, 1, 1, 1])
if np.linalg.det(O2) < 0:
    O2 = neg @ O2
    O1 = O1 @ neg

K1 = Q @ O1 @ Q_H
A = Q @ F @ Q_H
K2 = Q @ O2 @ Q_H

U_decomp = K1 @ A @ K2

Can = scipy.linalg.expm(-1j*np.pi*(tx*XX+ty*YY+tz*ZZ))

print('============================')
print('Matrix A : Diagonal matrix F in the magic basis')
print(A)
print('')
print('----------------------------')
print('')
print('Canonical gate : matrix F in the canonical basis')
print(Can)
print('')

U_decomp_2 = K1 @ Can @ K2
l1,l2,l3,l4 = np.around(lambdas,3)
print('=================================')
print('                                 ')
print('Decomposition of U using matrix A')
print('l1 = ', l1, '; l2 = ', l2, '; l3 = ', l3, '; l4 = ', l4)
print('----------------------------------------')
print(np.around(U_decomp,4))
if np.allclose(U,U_decomp):
    print('                                                  ')
    print('== Decomposition matches between canonical and magic bases ==')
    print('                                                  ')

U_decomp = np.around(U_decomp,5)
aPha = []
aAbs = []
for x in U_decomp:
  for y in x:
    aPha.append(np.angle(y)/np.pi)
    aAbs.append(np.abs(y))
bPha = []
bAbs = []
U_decomp_2 = np.around(U_decomp_2,5)
for x in U_decomp_2:
  for y in x:
    bPha.append(np.angle(y)/np.pi)
    bAbs.append(np.abs(y))
cPha = []
for i in range(len(aPha)):
    if abs(bAbs[i]-aAbs[i]) < ATOL:
        diffPha = aPha[i]-bPha[i]
        if diffPha < 0:
            cPha.append(diffPha + 2)
        else:
            cPha.append(diffPha)
count = 1
for i in range(len(cPha)-1):
    if np.abs(cPha[i] - cPha[i+1]) < ATOL:
        cPha[i+1] = cPha[i]
        count += 1
print('========================================')
print('                                        ')
print('Decomposition of U using canonical gate:')
print('tx = ', np.around(tx,4), '; ty = ', np.around(ty,4), '; tz = ', np.around(tz,4))
print('----------------------------------------')
if count == len(cPha):
    globalPhase = cPha[0]
    if abs(globalPhase) < ATOL:
        print('Global phase found: theta = 0')
    else:    
        print('Global phase found: theta = pi /', np.around(1/globalPhase,2))
    print('----------------------------------------')
    U_decomp_2 = U_decomp_2*np.exp(1j*np.pi*globalPhase)
print(np.around(U_decomp_2,4))
if np.allclose(U_decomp,U_decomp_2):
    print('                                                  ')
    print('== Decomposition into canonical gate successful ==')
    print('                                                  ')
