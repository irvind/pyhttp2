import string
import struct


def int_to_byte(v):
    """
    Converts integer to single byte.
    """
    return struct.pack('>B', v)


def byte_to_int(b):
    """
    Converts byte to integer.
    """
    return struct.unpack('>B', b)[0]


def int_to_bytes(v, n):
    if n > 8:
        raise ValueError('n param is too big. 8 is the maximum value.')

    b = struct.pack('>Q', v)
    b_len = len(b)
    return b[b_len-n:]


def to_bin(v):
    """
    Turns integer to binary number string.
    """
    if v < 0:
        v = -v

    return '{:0>8}'.format(bin(v)[2:])


def to_hex(v):
    """
    Turns integer to hex number string.
    """
    if v < 0:
        v = -v

    return '{:0>2}'.format(hex(v)[2:])


def byterepr_to_bytes(*args):
    arr = bytearray()
    for r in chunkify(''.join(args), 8):
        arr.append(int(r, 2))

    return bytes(arr)


def reversed_wrapper(v):
    cls = type(v)
    if isinstance(v, (list, tuple, bytes, bytearray)):
        return cls(reversed(v))
    elif cls == str:
        return ''.join(list(reversed(v)))
    else:
        raise ValueError('Not supported value type ({})'.format(cls))


def chunkify(seq, item_size):
    """
    Chunkifies a sequence into list.
    """
    result = []
    i = 0

    if item_size <= 0:
        raise ValueError('item_size must be greater than zero')

    while True:
        item = seq[i*item_size:i*item_size+item_size]
        if len(item) == 0:
            break
        
        result.append(item)
        i += 1

    return result


def rchunkify(seq, item_size):
    """
    Same as chunkify but right-aligned.
    """
    items = chunkify(reversed_wrapper(seq), item_size)
    items = list(map(lambda s: reversed_wrapper(s), items))
    return reversed_wrapper(items)


def bin_repr(array):
    for b in array:
        print(to_bin(b))


def hex_repr(array):
    # Exclude space characters.
    ascii_visible = string.printable[:len(string.printable) - 5]

    def to_char(b):
        ch = chr(b)
        return ch if ch in ascii_visible else '.'
        
    rows = chunkify(array, 16)
    for row in rows:
        cells = chunkify(row, 2)
        left_repr = ' '.join(map(lambda i: to_hex(i[0]) + to_hex(i[1]), cells))
        right_repr = ''.join(map(to_char, row)) 
        
        print('{: <39} | {}'.format(left_repr, right_repr))
