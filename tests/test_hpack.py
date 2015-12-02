import unittest

from pyhttp2.utils import byterepr_to_bytes, int_to_byte
from pyhttp2.hpack import (
    uint_encode, uint_decode, bytestr_encode
)


class TestHPACK(unittest.TestCase):
    def test_uint_encode(self):
        self.assertEqual(uint_encode(10, n=5), b'\x0a')
        self.assertEqual(uint_encode(1337, n=5), byterepr_to_bytes(
            '00011111',
            '10011010',
            '00001010'
        ))

        self.assertEqual(uint_encode(42), byterepr_to_bytes('00101010'))

        with self.assertRaises(ValueError):
            uint_encode(-42, n=5)

    def test_decode_encoded_uint(self):
        self.assertEqual(uint_decode(uint_encode(187, n=5), n=5), 187)
        self.assertEqual(uint_decode(uint_encode(78, n=7), n=7), 78)
        self.assertEqual(uint_decode(uint_encode(1126)), 1126)
        self.assertEqual(uint_decode(uint_encode(26)), 26)
        self.assertEqual(uint_decode(uint_encode(2000, n=2), n=2), 2000)
        
    def test_bytestr_encode(self):
        self.assertEqual(bytestr_encode(b'Hello, World'), b'\x0cHello, World')
        self.assertEqual(bytestr_encode('Hi!'), b'\x03Hi!')

        long_bstr = b'.' * 200
        # encoded 200 = 01111111 (127) + 01001001 (73) = 0x7f49
        self.assertEqual(bytestr_encode(long_bstr), b'\x7f\x49' + long_bstr)

    def test_bytestr_uncode_encode(self):
        hello = 'Привет'
        self.assertEqual(bytestr_encode(hello, encoding='utf-8'), 
            int_to_byte(len(hello.encode('utf-8'))) + hello.encode('utf-8'))

        long_hello = hello * 100
        self.assertEqual(bytestr_encode(long_hello, encoding='utf-8'), 
            uint_encode(len(long_hello.encode('utf-8')), n=7) + long_hello.encode('utf-8'))

    def test_bytestr_huffman_encode(self):
        pass


if __name__ == '__main__':
    unittest.main()