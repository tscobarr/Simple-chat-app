from .poly import Polynomial, PolynomialVector

def preprocessMessage(messageStr, n):
    """Preprocesses a message string into a bit list of length n.

    Args:
        messageStr (str): The input message string.
        n (int): The desired length of the output bit list.

    Returns:
        list: The preprocessed message as a bit list.
    """
    messageBits = stringToBitstring(messageStr)
    messageBitsPadded = messageBits.ljust(n, '0')
    message = [int(bit) for bit in messageBitsPadded]
    return message

def postprocessMessage(decryptedMessageBits, originalLength):
    """Postprocesses a decrypted message bit list back into a string.

    Args:
        decryptedMessageBits (list): The decrypted message as a bit list.
        originalLength (int): The original length of the message.

    Returns:
        str: The postprocessed message string.
    """
    decryptedMessageBitsStr = ''.join(str(bit) for bit in decryptedMessageBits[:originalLength])
    decryptedMessage = bitstringToString(decryptedMessageBitsStr)
    return decryptedMessage

def bytesToBitList(byteData, n):
    """Converts a byte string to a bit list of length n.

    Args:
        byteData (bytes): The input byte string.
        n (int): The desired length of the output bit list.

    Returns:
        list: The bit list of length n.
    """
    # Convert the byte string to a bit string
    bitString = ''.join(format(byte, '08b') for byte in byteData)
    
    # Ensure the bit string has the desired length n
    bitStringPadded = bitString.ljust(n, '0')
    
    # Convert the bit string to a list of integers
    bitList = [int(bit) for bit in bitStringPadded[:n]]
    
    return bitList

def bitListToBytes(bitList):
    """Converts a bit list to a byte string.

    Args:
        bitList (list): The input bit list.

    Returns:
        bytes: The byte string.
    """
    # Group the bits into groups of 8
    byteList = []
    for i in range(0, len(bitList), 8):
        byte = 0
        for j in range(8):
            if i + j < len(bitList):
                byte |= bitList[i + j] << (7 - j)
        byteList.append(byte)
    
    return bytes(byteList)

def stringToBitstring(s):
    """Converts a string to a bitstring.

    Args:
        s (str): The input string.

    Returns:
        str: The bitstring representation of the input string.
    """
    return ''.join(format(ord(c), '08b') for c in s)

def bitstringToString(b):
    """Converts a bitstring to a string.

    Args:
        b (str): The input bitstring.

    Returns:
        str: The string representation of the input bitstring.
    """
    chars = [chr(int(b[i:i+8], 2)) for i in range(0, len(b), 8)]
    return ''.join(chars)

def decode(byteArray, q, n, l, k=None):
    """Deserializes an array of bytes into a Polynomial or PolynomialVector.

    Args:
        byteArray (bytes): The input byte array.
        q (int): The modulus for the polynomial coefficients.
        n (int): The number of coefficients in each polynomial.
        l (int): The length parameter.
        k (int, optional): The number of polynomials in the vector. If None, decode a single polynomial.

    Returns:
        Polynomial or PolynomialVector: The resulting polynomial or polynomial vector.
    """
    bitArray = []
    for byte in byteArray:
        for i in range(8):
            bitArray.append((byte >> (7 - i)) & 1)

    if k is None:
        # Decode a single polynomial
        coefficients = []
        requiredBits = n * l
        if len(bitArray) < requiredBits:
            bitArray.extend([0] * (requiredBits - len(bitArray)))

        for i in range(n):
            coeff = 0
            for j in range(l):
                coeff += bitArray[i * l + j] << j
            coefficients.append(coeff % q)
        return Polynomial(coefficients, q)
    else:
        # Decode a polynomial vector
        polynomials = []
        requiredBits = n * l * k
        if len(bitArray) < requiredBits:
            bitArray.extend([0] * (requiredBits - len(bitArray)))

        for i in range(k):
            coefficients = []
            for j in range(n):
                coeff = 0
                for m in range(l):
                    coeff += bitArray[(i * n + j) * l + m] << m
                coefficients.append(coeff % q)
            polynomials.append(Polynomial(coefficients, q))
        return PolynomialVector(polynomials)

def encode(poly, n, l):
    """Serializes a Polynomial or PolynomialVector into an array of bytes.

    Args:
        poly (Polynomial or PolynomialVector): The input polynomial or polynomial vector.
        n (int): The number of coefficients in each polynomial.
        l (int): The length parameter.

    Returns:
        bytes: The resulting byte array.
    """
    byteArray = bytearray()
    if isinstance(poly, PolynomialVector):
        for p in poly.polynomials:
            bitArray = []
            for coeff in p.coefficients:
                for j in range(l):
                    bitArray.append((coeff >> j) & 1)
            for i in range(0, len(bitArray), 8):
                byte = 0
                for j in range(8):
                    if i + j < len(bitArray):
                        byte |= bitArray[i + j] << (7 - j)
                byteArray.append(byte)
    elif isinstance(poly, Polynomial):
        bitArray = []
        for coeff in poly.coefficients:
            for j in range(l):
                bitArray.append((coeff >> j) & 1)
        for i in range(0, len(bitArray), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bitArray):
                    byte |= bitArray[i + j] << (7 - j)
            byteArray.append(byte)
    return bytes(byteArray)