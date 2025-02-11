import os
from .poly import Polynomial, PolynomialVector
from .utils import preprocessMessage, postprocessMessage, encode, decode
from .optimization import roundUpTies, roundQ, randomPolyVector, randomPoly, expand, compress, decompress, G

def keygenPKE(params):
    """Generates a public and private key pair.

    Args:
        params (dict): Dictionary containing parameters k, n, q, eta1, eta2.

    Returns:
        tuple: A tuple containing the serialized public key and the serialized private key.
    """
    k = params["k"]
    n = params["n"]
    q = params["q"]
    eta1 = params["eta1"]
    eta2 = params["eta2"]

    N = 0

    # Generate random 256-bit seed d
    d = os.urandom(32)

    # Compute (rho, sigma) = G(d)
    gOutput = G(d)
    rho, sigma = gOutput[:32], gOutput[32:]

    # Generate matrix A ∈ Rq^k×k
    A = expand(rho, k, q, n)

    # Sample s ∈ Rq^k from Bη1
    s = randomPolyVector(k, N, q, eta1, sigma)

    # Sample e ∈ Rq^k from Bη2
    e = randomPolyVector(k, N, q, eta2, sigma)

    # Compute t = A * s + e
    As = PolynomialVector([Polynomial([0] * n, q) for _ in range(k)])
    for i in range(k):
        for j in range(k):
            As.polynomials[i] = As.polynomials[i] + A[i][j].mulRq(s.polynomials[j], n)

    t = PolynomialVector([As.polynomials[i] + e.polynomials[i] for i in range(k)])

    # Serialize the public key
    serializedPublicKey = rho + encode(t, n, 12)

    # Serialize the private key
    serializedPrivateKey = encode(s, n, 12)

    return serializedPublicKey, serializedPrivateKey

def encrypt(params, publicKey, message, r=None):
    if r is None:
        r = os.urandom(32)
    return encryptPKE(params, publicKey, preprocessMessage(message, params["n"]), r)

def encryptPKE(params, serializedPublicKey, message, r=None):
    """Encrypts a preprocessed message using the public key.

    Args:
        params (dict): Dictionary containing parameters k, n, q, eta1, eta2, du, dv.
        serializedPublicKey (bytes): The serialized public key.
        message (list): The preprocessed message to be encrypted.
        r (PolynomialVector, optional): Random polynomial vector. If None, a new one is generated.

    Returns:
        bytes: The serialized ciphertext.
    """
    k = params["k"]
    n = params["n"]
    q = params["q"]
    eta1 = params["eta1"]
    eta2 = params["eta2"]
    du = params["du"]
    dv = params["dv"]

    N = 0

    # Deserialize the public key
    rho = serializedPublicKey[:32]
    serializedT = serializedPublicKey[32:]
    t = decode(serializedT, q, n, 12, k)

    # Compute A from rho
    A = expand(rho, k, q, n)

    # Select r ∈_CBD (S_eta1)^k, e_1 ∈_CBD (S_eta2)^k, e_2 ∈_CBD S_eta2
    if r is None:
        r = os.urandom(32)
    else:
        r = bytes(r)

    rPoly = randomPolyVector(k, N, q, eta1, r)
    e1 = randomPolyVector(k, N, q, eta2, r)
    e2 = randomPoly(q, eta2, r, N)

    # Compute u = A^T*r + e_1
    u = PolynomialVector([Polynomial([0] * n, q) for _ in range(k)])
    for i in range(k):
        for j in range(k):
            u.polynomials[i] = u.polynomials[i] + A[j][i].mulRq(rPoly.polynomials[j], n)
        u.polynomials[i] = u.polynomials[i] + e1.polynomials[i]

    # Compute v = t^T*r + e_2 + ⌈q/2⌋*m
    v = Polynomial([0] * n, q)
    for i in range(k):
        v = v + t.polynomials[i].mulRq(rPoly.polynomials[i], n)
    v = v + e2

    # Add ⌈q/2⌋*m to v (the same as decompress(m,1))
    qHalf = roundUpTies(q / 2)
    mPoly = Polynomial([m * qHalf for m in message], q)
    v = v + mPoly

    # Compute c1 = compressPoly(u, du) and c2 = compressPoly(v, dv)
    c1 = PolynomialVector([Polynomial([compress(c, q, du) for c in poly.coefficients], 2**du) for poly in u.polynomials])
    c2 = Polynomial([compress(c, q, dv) for c in v.coefficients], 2**dv)

    # Serialize the ciphertext
    serializedC1 = encode(c1, n, du)
    serializedC2 = encode(c2, n, dv)
    serializedCiphertext = serializedC1 + serializedC2

    return serializedCiphertext

def decrypt(params, privateKey, ciphertext):
    return postprocessMessage(decryptPKE(params, privateKey, ciphertext), params["n"])

def decryptPKE(params, serializedPrivateKey, serializedCiphertext):
    """Decrypts a serialized ciphertext using the private key.

    Args:
        params (dict): Dictionary containing parameters k, n, q, du, dv.
        serializedPrivateKey (bytes): The serialized private key.
        serializedCiphertext (bytes): The serialized ciphertext.

    Returns:
        list: The decrypted message.
    """
    k = params["k"]
    n = params["n"]
    q = params["q"]
    du = params["du"]
    dv = params["dv"]

    # Deserialize the private key
    s = decode(serializedPrivateKey, q, n, 12, k)

    # Calculate the sizes of c1 and c2
    c1Size = k * n * du // 8
    c2Size = n * dv // 8

    # Deserialize the ciphertext
    serializedC1 = serializedCiphertext[:c1Size]
    serializedC2 = serializedCiphertext[c1Size:c1Size + c2Size]

    if k == 4:
        qC1 = 2048
        qC2 = 32
    else:
        qC1 = 1024
        qC2 = 16

    c1 = decode(serializedC1, qC1, n, du, k)
    c2 = decode(serializedC2, qC2, n, dv)

    u = PolynomialVector([Polynomial([decompress(c, q, du) for c in poly.coefficients], q) for poly in c1.polynomials])
    v = Polynomial([decompress(c, q, dv) for c in c2.coefficients], q)

    # Compute m = Round_q(v - s^T * u)
    sU = Polynomial([0] * n, q)
    for i in range(k):
        sU = sU + s.polynomials[i].mulRq(u.polynomials[i], n)
    mPoly = v - sU
    message = [roundQ(c, q) for c in mPoly.coefficients]

    return message