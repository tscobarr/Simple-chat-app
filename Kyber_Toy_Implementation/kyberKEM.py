import os
from kyberPKE import keygenPKE, encryptPKE, decryptPKE
from utils import serialize_polynomial_vector, bytes_to_bit_list, bit_list_to_bytes
from optimization import H, G, KDF

def keygenKEM(params):
    """Generates a key pair for Kyber-KEM.

    Args:
        params (dict): Dictionary containing parameters k, n, q, eta1, eta2.

    Returns:
        tuple: A tuple containing the encapsulation key (ek) and the decapsulation key (dk).
    """
    # Step 1: Use the Kyber-PKE key generation algorithm to select a Kyber-PKE encryption key (rho, t) and decryption key s
    pk, sk = keygenPKE(params)
    rho, t = pk

    # Step 2: Select z at random in {0,1}^256
    z = os.urandom(32)

    # Step 3: Alice's encapsulation key is ek = (rho, t)
    ek = (rho, t)

    # Step 4: Her decapsulation key is dk = (s, ek, H(ek), z)
    ek_bytes = rho + serialize_polynomial_vector(t)
    h_ek = H(ek_bytes)
    dk = (sk, pk, h_ek, z)

    return ek, dk

def encapsulate(ek, params):
    """Encapsulates a shared secret using the encapsulation key.

    Args:
        ek (tuple): The encapsulation key (rho, t).
        params (dict): Dictionary containing parameters k, n, q, eta1, eta2, du, dv.

    Returns:
        tuple: The ciphertext and the shared secret.
    """
    rho, t = ek

    # Step 1: Select m at random in {0,1}^256
    m = os.urandom(32)
    m = H(m)

    # Step 2: Compute h = H(ek) and (K, R) = G(m, h)
    ek_bytes = rho + serialize_polynomial_vector(t)
    h = H(ek_bytes)
    g_input = m + h
    K_hat, r = G(g_input)[:32], G(g_input)[32:]

    m_bit_list = bytes_to_bit_list(m, params["n"])

    # Step 3: Encrypt m using Kyber-PKE
    c = encryptPKE(params, ek, m_bit_list, r)

    # Step 4: Hash the ciphertext with H
    serialized_ciphertext = serialize_polynomial_vector(c[0]) + bytes(c[1].coefficients)
    hashed_ciphertext = H(serialized_ciphertext)

    # Step 5: Compute the shared secret ss = KDF(K + hashed_ciphertext, 32)
    K = KDF(K_hat + hashed_ciphertext, 32)

    return c, K

def decapsulate(dk, ciphertext, params):
    """Decapsulates a shared secret using the decapsulation key.

    Args:
        dk (tuple): The decapsulation key (s, ek, H(ek), z).
        ciphertext (tuple): The ciphertext to be decapsulated.
        params (dict): Dictionary containing parameters k, n, q, eta1, eta2, du, dv.

    Returns:
        bytes: The shared secret.
    """
    s, ek, h_ek, z = dk

    # Step 1: Decrypt the ciphertext using Kyber-PKE
    m_prime = decryptPKE(params, s, ciphertext)

    # Step 2: Compute (K', R') = G(bytes(m) + h_ek)
    g_input = bit_list_to_bytes(m_prime) + h_ek
    K_prime, R_prime = G(g_input)[:32], G(g_input)[32:]
    
    c_prime = encryptPKE(params, ek, m_prime, R_prime)

    # Detailed comparison of c_prime and ciphertext
    c1_prime, c2_prime = c_prime
    c1, c2 = ciphertext

    # Detailed comparison of c_prime and ciphertext
    c_prime_equal = True
    for i, (poly_prime, poly) in enumerate(zip(c1_prime.polynomials, c1.polynomials)):
        if poly_prime.coefficients != poly.coefficients:
            c_prime_equal = False
    if c2_prime.coefficients != c2.coefficients:
        c_prime_equal = False

    if c_prime_equal:
        return KDF(K_prime + H(serialize_polynomial_vector(c_prime[0]) + bytes(c_prime[1].coefficients)), 32)
    else:
        return KDF(z + H(serialize_polynomial_vector(c_prime[0]) + bytes(c_prime[1].coefficients)), 32)