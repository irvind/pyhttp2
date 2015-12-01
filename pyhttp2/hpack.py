import struct
import string

from .utils import chunkify, rchunkify

# chr(x) - int to single char
# bin(x) - int to bin repr

# ba = bytearray()
# ba.append(num) (num <= 255)
# ba.extend(b'\x01\x02\x03')

_static_table = (
    (':authority', ''),
    (':method', 'GET'),
    (':method', 'POST'),
    (':path', '/'),
    (':path', '/index.html'),
    (':scheme', 'http'),
    (':scheme', 'https'),
    (':status', '200'),
    (':status', '204'),
    (':status', '206'),
    (':status', '304'),
    (':status', '400'),
    (':status', '404'),
    (':status', '500'),
    ('accept-charset', ''),
    ('accept-encoding', 'gzip, deflate'),
    ('accept-language', ''),
    ('accept-ranges', ''),
    ('accept', ''),
    ('access-control-allow-origin', ''),
    ('age', ''),
    ('allow', ''),
    ('authorization', ''),
    ('cache-control', ''),
    ('content-disposition', ''),
    ('content-encoding', ''),
    ('content-language', ''),
    ('content-length', ''),
    ('content-location', ''),
    ('content-range', ''),
    ('content-type', ''),
    ('cookie', ''),
    ('date', ''),
    ('etag', ''),
    ('expect', ''),
    ('expires', ''),
    ('from', ''),
    ('host', ''),
    ('if-match', ''),
    ('if-modified-since', ''),
    ('if-none-match', ''),
    ('if-range', ''),
    ('if-unmodified-since', ''),
    ('last-modified', ''),
    ('link', ''),
    ('location', ''),
    ('max-forwards', ''),
    ('proxy-authenticate', ''),
    ('proxy-authorization', ''),
    ('range', ''),
    ('referer', ''),
    ('refresh', ''),
    ('retry-after', ''),
    ('server', ''),
    ('set-cookie', ''),
    ('strict-transport-security', ''),
    ('transfer-encoding', ''),
    ('user-agent', ''),
    ('vary', ''),
    ('via', ''),
    ('www-authenticate', ''),
)


def uint_encode(val, n=8):
    """
    Encodes unsigned integer accoriding to [RFC7541, section 5.1].

    :param val:
        pass
    :param n:
        pass
    """
    if val < 0:
        raise ValueError('Integer must be equal or greater than zero!')

    if val < 2**n - 1:
        return bytearray(int_to_byte(val))

    result = bytearray()
    i = val

    result.append(2**n - 1)
    i = i - (2**n - 1)
    while i >= 128:
        result.append(i % 128 + 128)
        i = i // 128

    result.append(i)

    return result


def uint_decode(array, n=8):
    """
    Decodes unsigned integer accoriding to [RFC7541, section 5.1]. 

    :param array:
        pass
    :param n:
        pass
    """
    ind = 0
    i = array[ind] & 2**n - 1
    if i < 2**n - 1:
        return i

    m = 0
    while True:
        ind += 1
        b = array[ind]
        i += (b & 127) * 2**m
        m += 7
        
        if b & 128 != 128:
            break

    return i


def bytestr_encode(bytestr, huffman=False):
    """
    Decodes byte string literal accoriding to [RFC7541, section 5.2]. 

    :param bytestr:
        pass
    :param huffman:
        pass
    """
    if not isinstance(bytestr, (bytes, bytearray)):
        pass

    if huffman:
        raise NotImplementedError()

    result = uint_encode(len(bytestr), n=7)
    if huffman:
        result[0] = 128 | result[0]

    result.extend(bytestr)

    return result


# def header_block_encode(headers):
#     headers = headers.split('\n')
    

# def header_block_decode(header_block):
#     pass


class IndexTable(list):
    def __init__(self, *args):
        list.__init__(self, *args)

        # todo static table

    def find_field(self, name, value):
        pass

    def find_name(self, name):
        pass

    def add_field(self, name, field):
        pass


class Encoder(object):
    def __init__(self):
        self.index_table = IndexTable()

    def encode(self, headers):
        if isinstance(str):
            headers.encode('ascii')

        result = bytearray()
        headers = headers.split(b'\n')
        for header in headers:
            h = header.rsplit(b':', 1)
            h[1] = h[1].strip()
            result.extend(self._encode_field(h[0], h[1]))

        return result

    def _encode_field(self, name, value):
        ind = self.index_table.find_field(name, value)
        if ind is not None:
            return self._encode_indexed_field(ind)

        ind = self.index_table.find_name(name)
        if ind is not None:
            return self._encode_indexed_name_field(ind, value)
            pass

    def _encode_indexed_field(self, ind):
        pass


class Decoder(object):
    def __init__(self):
        self.index_table = IndexTable()

    def decode(self, header_block):
        pass