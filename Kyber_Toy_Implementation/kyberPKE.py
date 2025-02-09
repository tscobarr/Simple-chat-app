import os
from poly import Polynomial, PolynomialVector
from utils import preprocess_message, postprocess_message
from optimization import round_up_ties, round_q, random_poly_vector, random_poly, expand, compress, decompress, G

def keygenPKE(params):
    """Generates a public and private key pair.

    Args:
        params (dict): Dictionary containing parameters k, n, q, eta1, eta2.

    Returns:
        tuple: A tuple containing the public key (rho, t) and the private key s.
    """
    k = params["k"]
    n = params["n"]
    q = params["q"]
    eta1 = params["eta1"]
    eta2 = params["eta2"]

    N = 0

    # Step 1: Generate random 256-bit seed d
    d = os.urandom(32)

    # Step 2: Compute (ρ, σ) = G(d)
    g_output = G(d)
    rho, sigma = g_output[:32], g_output[32:]

    # Step 3: Generate matrix A ∈ Rq^k×k
    A = expand(rho, k, q, n)

    # Step 4: Sample s ∈ Rq^k from Bη1
    s = random_poly_vector(k, N, q, eta1, sigma)

    # Step 5: Sample e ∈ Rq^k from Bη2
    e = random_poly_vector(k, N, q, eta2, sigma)

    # Step 6: Compute t = A * s + e
    As = PolynomialVector([Polynomial([0] * n, q) for _ in range(k)])
    for i in range(k):
        for j in range(k):
            As.polynomials[i] = As.polynomials[i] + A[i][j].mul_rq(s.polynomials[j], n)

    t = PolynomialVector([As.polynomials[i] + e.polynomials[i] for i in range(k)])

    # Step 7: Public key pk = (t, rho)
    public_key = (rho, t)

    # Step 8: Secret key sk = s
    private_key = s

    return public_key, private_key

def encrypt(params, public_key, message, r=None):
    if r is None:
        r = os.urandom(32)
    return encryptPKE(params, public_key, preprocess_message(message, params["n"]), r)

def encryptPKE(params, public_key, message, r=None):
    """Encrypts a preprocessed message using the public key.

    Args:
        params (dict): Dictionary containing parameters k, n, q, eta1, eta2, du, dv.
        public_key (tuple): The public key (rho, t).
        message (list): The preprocessed message to be encrypted.
        r (PolynomialVector, optional): Random polynomial vector. If None, a new one is generated.

    Returns:
        tuple: The ciphertext (c1, c2).
    """
    k = params["k"]
    n = params["n"]
    q = params["q"]
    eta1 = params["eta1"]
    eta2 = params["eta2"]
    du = params["du"]
    dv = params["dv"]

    N = 0

    # Step 1: Compute A from rho
    rho, t = public_key
    A = expand(rho, k, q, n)

    # Step 2: Select r ∈_CBD (S_eta1)^k, e_1 ∈_CBD (S_eta2)^k, e_2 ∈_CBD S_eta2
    if r is None:
        r = os.urandom(32)
    else:
        r = bytes(r)

    rPoly = random_poly_vector(k, N, q, eta1, r)
    e1 = random_poly_vector(k, N, q, eta2, r)
    e2 = random_poly(q, eta2, r, N)

    # Step 3: Compute u = A^T*r + e_1
    u = PolynomialVector([Polynomial([0] * n, q) for _ in range(k)])
    for i in range(k):
        for j in range(k):
            u.polynomials[i] = u.polynomials[i] + A[j][i].mul_rq(rPoly.polynomials[j], n)
        u.polynomials[i] = u.polynomials[i] + e1.polynomials[i]

    # Step 4: Compute v = t^T*r + e_2 + ⌈q/2⌋*m
    v = Polynomial([0] * n, q)
    for i in range(k):
        v = v + t.polynomials[i].mul_rq(rPoly.polynomials[i], n)
    v = v + e2

    # Add ⌈q/2⌋*m to v (the same as decompress(m,1))
    q_half = round_up_ties(q / 2)
    m_poly = Polynomial([m * q_half for m in message], q)
    v = v + m_poly

    # Step 5: Compute c1 = compress_poly(u, du) and c2 = compress_poly(v, dv)
    c1 = PolynomialVector([Polynomial([compress(c, q, du) for c in poly.coefficients], 2**du) for poly in u.polynomials])
    c2 = Polynomial([compress(c, q, dv) for c in v.coefficients], 2**dv)

    return (c1, c2)

def decrypt(params, private_key, ciphertext):
    return postprocess_message(decryptPKE(params, private_key, ciphertext), params["n"])

def decryptPKE(params, private_key, ciphertext):
    """Decrypts a ciphertext using the private key.

    Args:
        params (dict): Dictionary containing parameters k, n, q, du, dv.
        private_key (PolynomialVector): The private key s.
        ciphertext (tuple): The ciphertext (c1, c2).

    Returns:
        list: The decrypted message.
    """
    k = params["k"]
    n = params["n"]
    q = params["q"]
    du = params["du"]
    dv = params["dv"]
    s = private_key
    c1, c2 = ciphertext

    u = PolynomialVector([Polynomial([decompress(c, q, du) for c in poly.coefficients], q) for poly in c1.polynomials])
    v = Polynomial([decompress(c, q, dv) for c in c2.coefficients], q)

    # Step 1: Compute m = Round_q(v - s^T * u)
    s_u = Polynomial([0] * n, q)
    for i in range(k):
        s_u = s_u + s.polynomials[i].mul_rq(u.polynomials[i], n)
    m_poly = v - s_u
    message = [round_q(c, q) for c in m_poly.coefficients]

    return message