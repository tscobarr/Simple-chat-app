def preprocess_message(message_str, n):
    """Preprocesses a message string into a bit list of length n.

    Args:
        message_str (str): The input message string.
        n (int): The desired length of the output bit list.

    Returns:
        list: The preprocessed message as a bit list.
    """
    message_bits = string_to_bitstring(message_str)
    message_bits_padded = message_bits.ljust(n, '0')
    message = [int(bit) for bit in message_bits_padded]
    return message

def postprocess_message(decrypted_message_bits, original_length):
    """Postprocesses a decrypted message bit list back into a string.

    Args:
        decrypted_message_bits (list): The decrypted message as a bit list.
        original_length (int): The original length of the message.

    Returns:
        str: The postprocessed message string.
    """
    decrypted_message_bits_str = ''.join(str(bit) for bit in decrypted_message_bits[:original_length])
    decrypted_message = bitstring_to_string(decrypted_message_bits_str)
    return decrypted_message

def bytes_to_bit_list(byte_data, n):
    """Converts a byte string to a bit list of length n.

    Args:
        byte_data (bytes): The input byte string.
        n (int): The desired length of the output bit list.

    Returns:
        list: The bit list of length n.
    """
    # Convertir la cadena de bytes a una cadena de bits
    bit_string = ''.join(format(byte, '08b') for byte in byte_data)
    
    # Asegurarse de que la cadena de bits tenga la longitud deseada n
    bit_string_padded = bit_string.ljust(n, '0')
    
    # Convertir la cadena de bits a una lista de enteros
    bit_list = [int(bit) for bit in bit_string_padded[:n]]
    
    return bit_list

def bit_list_to_bytes(bit_list):
    """Converts a bit list to a byte string.

    Args:
        bit_list (list): The input bit list.

    Returns:
        bytes: The byte string.
    """
    # Agrupar los bits en grupos de 8
    byte_list = []
    for i in range(0, len(bit_list), 8):
        byte = 0
        for j in range(8):
            if i + j < len(bit_list):
                byte |= bit_list[i + j] << (7 - j)
        byte_list.append(byte)
    
    return bytes(byte_list)

def bit_count(x):
    return bin(x).count('1')

def serialize_polynomial_vector(vector):
    """Serializes a polynomial vector to bytes.

    Args:
        vector (PolynomialVector): The polynomial vector to be serialized.

    Returns:
        bytes: The serialized polynomial vector.
    """
    return b''.join(coeff.to_bytes(2, 'little') for poly in vector.polynomials for coeff in poly.coefficients)

def string_to_bitstring(s):
    """Converts a string to a bitstring.

    Args:
        s (str): The input string.

    Returns:
        str: The bitstring representation of the input string.
    """
    return ''.join(format(ord(c), '08b') for c in s)

def bitstring_to_string(b):
    """Converts a bitstring to a string.

    Args:
        b (str): The input bitstring.

    Returns:
        str: The string representation of the input bitstring.
    """
    chars = [chr(int(b[i:i+8], 2)) for i in range(0, len(b), 8)]
    return ''.join(chars)