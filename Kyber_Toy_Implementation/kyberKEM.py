import os
from .kyberPKE import keygenPKE, encryptPKE, decryptPKE
from .utils import bytesToBitList, bitListToBytes
from .optimization import H, G, KDF

def keygenKEM(params):
    """Generates a key pair for Kyber-KEM.

    Args:
        params (dict): Dictionary containing parameters k, n, q, eta1, eta2.

    Returns:
        tuple: A tuple containing the public key (pk) and the secret key (sk).
    """
    # Select z at random in {0,1}^256
    z = os.urandom(32)

    # Use the Kyber-PKE key generation algorithm to select a Kyber-PKE encryption key (pk) and decryption key (sk0)
    pk, sk0 = keygenPKE(params)

    # Compute H(pk)
    hPk = H(pk)

    # The secret key is sk = (sk0 || pk || H(pk) || z)
    sk = sk0 + pk + hPk + z

    # print("pk:", len(pk))
    # print("sk0:", len(sk0))

    return pk, sk

def encapsulate(pk, params):
    """Encapsulates a shared secret using the public key.

    Args:
        pk (bytes): The public key.
        params (dict): Dictionary containing parameters k, n, q, eta1, eta2, du, dv.

    Returns:
        tuple: The ciphertext and the shared secret.
    """
    # Select m at random in {0,1}^256
    m = os.urandom(32)
    m = H(m)

    # Compute (K, r) = G(m || H(pk))
    hPk = H(pk)
    gInput = m + hPk
    kHat, r = G(gInput)[:32], G(gInput)[32:]

    mBitList = bytesToBitList(m, params["n"])

    # Encrypt m using Kyber-PKE
    c = encryptPKE(params, pk, mBitList, r)

    # Hash the ciphertext with H
    serializedCiphertext = c
    hashedCiphertext = H(serializedCiphertext)

    # Compute the shared secret ss = KDF(K || H(c))
    K = KDF(kHat + hashedCiphertext, 32)

    return serializedCiphertext, K

def decapsulate(c, sk, params):
    """Decapsulates a shared secret using the secret key.

    Args:
        c (bytes): The ciphertext.
        sk (bytes): The secret key.
        params (dict): Dictionary containing parameters k, n, q, eta1, eta2, du, dv.

    Returns:
        bytes: The shared secret.
    """
    k = params["k"]

    sk0Len = 12 * k * 256 // 8
    pkLen = sk0Len + 32
    hLen = 32
    zLen = 32

    # Extract sk0 from sk
    sk0 = sk[:sk0Len]

    # Extract pk from sk
    pkStart = sk0Len
    pkEnd = pkStart + pkLen
    pk = sk[pkStart:pkEnd]

    # Extract h from sk
    hStart = pkEnd
    hEnd = hStart + hLen
    h = sk[hStart:hEnd]

    # Extract z from sk
    zStart = hEnd
    zEnd = zStart + zLen
    z = sk[zStart:zEnd]

    # Decrypt the ciphertext using Kyber-PKE
    mPrime = decryptPKE(params, sk0, c)

    # Compute (K', r') = G(m' || h)
    gInput = bitListToBytes(mPrime) + h
    kPrime, rPrime = G(gInput)[:32], G(gInput)[32:]

    # Encrypt m' using Kyber-PKE
    cPrime = encryptPKE(params, pk, mPrime, rPrime)

    # Compare c and c'
    if c == cPrime:
        return KDF(kPrime + H(c), 32)
    else:
        return KDF(z + H(c), 32)