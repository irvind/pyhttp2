import struct
import string

from .utils import chunkify, rchunkify, int_to_byte, byte_to_int

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


def bytestr_encode(bytestr, huffman=False, encoding='ascii'):
    """
    Decodes byte string literal accoriding to [RFC7541, section 5.2]. 

    :param bytestr:
        pass
    :param huffman:
        pass
    """
    if isinstance(bytestr, str):
        bytestr = bytestr.encode(encoding)

    if not isinstance(bytestr, (bytes, bytearray)):
        raise ValueError('bytestr must by an instance of bytes or bytearray')

    if huffman:
        raise NotImplementedError()

    result = uint_encode(len(bytestr), n=7)
    if huffman:
        result[0] = 128 | result[0]

    result.extend(bytestr)

    return result


class IndexTable(object):
    STATIC_LENGTH = len(_static_table)

    def __init__(self):
        self._dyn_table = []

    def find(self, name, value=None):
        return self._find_name(name) if value is None else self._find_field(name, value)

    def _find_name(self, name):
        static_names = [i[0] for i in _static_table]
        dynaimc_names = [i[0] for i in self._dyn_table]

        try:
            return (static_names + dynaimc_names).index(name) + 1
        except ValueError:
            return None

    def _find_field(self, name, value):
        try:
            return (list(_static_table) + self._dyn_table).index((name, value)) + 1
        except ValueError:
            return None

    def add(self, name, field):
        self._dyn_table.insert(0, (name, field))

    def get(self, index):
        index -= 1

        if index < self.STATIC_LENGTH:
            return _static_table[index]

        return self._dyn_table[index - self.STATIC_LENGTH]

    def __getitem__(self, index):
        return self.get(index)

    def __len__(self):
        return self.STATIC_LENGTH + len(self._dyn_table)
        

class Encoder(object):
    def __init__(self):
        self.index_table = IndexTable()

    def encode_headers(self, headers):
        if isinstance(headers, str):
            headers = headers.encode('ascii')

        result = bytearray()
        headers = headers.split(b'\n')
        for header in headers:
            h = header.rsplit(b':', 1)
            h[1] = h[1].strip()
            result.extend(self.encode_header(h[0], h[1]))

        return bytes(result)

    def encode_header(self, name, value):
        ind = self.index_table.find(name, value)
        if ind is not None:
            return self._encode_indexed_field(ind)

        ind = self.index_table.find(name)
        return self._encode_literal_field(
            name=ind if ind is not None else name, 
            value=value
        )
            
    def _encode_indexed_field(self, idx):
        result = uint_encode(idx, n=7)
        result[0] = 128 | result[0]
        
        return result

    def _encode_literal_field(self, name, value, indexed=True, never_indexed=False):
        if indexed and never_indexed:
            raise ValueError()

        if isinstance(name, int):
            header = uint_encode(name, n=6 if indexed else 4)
        else:
            header = bytearray(b'\x00')

        _map = {
            (True, False): b'\x40',
            (False, False): b'\x00',
            (False, True): b'\x10',
        }
  
        header[0] = byte_to_int(
            _map[(indexed, never_indexed)]
        ) | header[0]

        result = header

        if isinstance(name, bytes):
            l = uint_encode(len(name), n=7)
            # l[0] = 128 | l[0]
            l.extend(name)
            result.extend(l)

        l = uint_encode(len(value), n=7)
        # l[0] = 128 | l[0]
        l.extend(value)
        result.extend(l)

        return bytes(result)


class Decoder(object):
    def __init__(self):
        self.index_table = IndexTable()

    def decode(self, header_block):
        pass