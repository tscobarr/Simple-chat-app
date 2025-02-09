import hashlib
import math
from poly import Polynomial, PolynomialVector

def round_up_ties(x):
    """Rounds up ties (e.g., 2.5, -3.5) to the nearest integer.

    Args:
        x (float): The number to be rounded.

    Returns:
        int: The rounded integer.
    """
    if x - math.floor(x) == 0.5:  # Check for ties
        return math.ceil(x)
    return round(x)

def mods(value, q):
    """Computes the symmetric modulo operation.

    Args:
        value (int): The value to be reduced.
        q (int): The modulus.

    Returns:
        int: The result of the symmetric modulo operation.
    """
    return ((value + q // 2) % q) - q // 2

def round_q(value, q):
    """Rounds a value to 0 or 1 based on its distance from the nearest multiple of q/4.

    Args:
        value (int): The value to be rounded.
        q (int): The modulus.

    Returns:
        int: The rounded value (0 or 1).
    """
    sym_value = mods(value, q)
    if -q / 4 < sym_value < q / 4:
        return 0
    else:
        return 1

def H(data):
    return hashlib.sha3_256(data).digest()

def G(data):
    return hashlib.sha3_512(data).digest()

def XOF(data, length):
    shake = hashlib.shake_128()
    shake.update(data)
    return shake.digest(length)

def PRF(seed, nonce, length):
    """Pseudorandom Function (PRF) using SHAKE-256.

    Args:
        seed (bytes): The seed for the PRF.
        nonce (int): The nonce.
        length (int): The length of the output.

    Returns:
        bytes: The pseudorandom output.
    """
    shake = hashlib.shake_256()
    shake.update(seed + nonce.to_bytes(1, 'little'))
    return shake.digest(length)

def KDF(data, length):
    """Key Derivation Function (KDF) using SHAKE-256.

    Args:
        data (bytes): The input data.
        length (int): The length of the output.

    Returns:
        bytes: The derived key.
    """
    shake = hashlib.shake_256()
    shake.update(data)
    return shake.digest(length)

def cbd(input_bytes, eta):
    """Generates a polynomial with coefficients in a centered binomial distribution.

    Args:
        input_bytes (bytes): The input bytes.
        eta (int): The parameter eta.

    Returns:
        list: The polynomial coefficients.
    """
    assert 64 * eta == len(input_bytes)
    
    # Convert bytes to bits
    bits = []
    for byte in input_bytes:
        bits.extend([int(bit) for bit in format(byte, '08b')])
    
    coefficients = [0 for _ in range(256)]
    
    for i in range(256):
        a = sum(bits[2 * i * eta + j] for j in range(eta))
        b = sum(bits[2 * i * eta + eta + j] for j in range(eta))
        coefficients[i] = (a - b) % 3329
    
    return coefficients

def random_poly_vector(k, N, q, eta, seed):
    """Generates a random polynomial vector.

    Args:
        k (int): The number of polynomials.
        n (int): The degree of the polynomials.
        q (int): The modulus.
        eta (int): The parameter eta.
        seed (bytes): The seed for the PRF.

    Returns:
        PolynomialVector: The random polynomial vector.
    """
    polynomials = []
    for _ in range(k):
        prf_output = PRF(seed, N, 64 * eta)
        coefficients = cbd(prf_output, eta)
        polynomials.append(Polynomial(coefficients, q))
        N += 1
    return PolynomialVector(polynomials)

def random_poly(q, eta, seed, N):
    """Generates a random polynomial.

    Args:
        q (int): The modulus.
        eta (int): The parameter eta.
        seed (bytes): The seed for the PRF.
        N (int): The nonce.

    Returns:
        Polynomial: The random polynomial.
    """
    prf_output = PRF(seed, N, 64 * eta)
    coefficients = cbd(prf_output, eta)
    return Polynomial(coefficients, q)

def expand(rho, k, q, n):
    """Expands a seed into a matrix of polynomials.

    Args:
        rho (bytes): The seed.
        k (int): The dimension of the matrix.
        q (int): The modulus.
        n (int): The degree of the polynomials.

    Returns:
        list: The matrix of polynomials.
    """
    A = []
    for i in range(k):
        row = []
        for j in range(k):
            seed = rho + i.to_bytes(1, 'little') + j.to_bytes(1, 'little')
            hash_output = XOF(seed, n * 2)
            coefficients = [int.from_bytes(hash_output[2 * l:2 * l + 2], 'little') % q for l in range(n)]
            row.append(Polynomial(coefficients, q))
        A.append(row)
    return A

def compress(x, q, d):
    """Compresses a value.

    Args:
        x (int): The value to be compressed.
        q (int): The modulus.
        d (int): The compression parameter.

    Returns:
        int: The compressed value.
    """
    return round_up_ties((2**d / q) * x) % (2**d)

def decompress(y, q, d):
    """Decompresses a value.

    Args:
        y (int): The value to be decompressed.
        q (int): The modulus.
        d (int): The compression parameter.

    Returns:
        int: The decompressed value.
    """
    return round_up_ties((q / 2**d) * y) % q