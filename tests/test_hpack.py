import unittest

from pyhttp2.utils import byterepr_to_bytes
from pyhttp2.hpack import (
    uint_encode, uint_decode
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

    def test_uint_decode(self):
        pass
        
    def test_bytestr_encode(self):
        pass

    def test_bytestr_huffman_encode(self):
        pass


if __name__ == '__main__':
    unittest.main()