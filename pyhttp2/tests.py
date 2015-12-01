import unittest

from pyhttp2.hpack import (
    chunkify, to_bin, to_hex, int_to_byte, byte_to_int, uint_encode, uint_decode,
    bytestr_encode, byterepr_to_bytes
)


class TestHPACK(unittest.TestCase):
    def test_chunkify(self):
        self.assertEqual(chunkify([], 5), [])
        self.assertEqual(chunkify(list(range(11)), 3), [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10]
        ])

        self.assertEqual(chunkify(b'123456789', 4), [b'1234', b'5678', b'9'])

        with self.assertRaises(ValueError):
            chunkify([1, 2, 3, 4], 0)

    def test_to_bin(self):
        self.assertEqual(to_bin(4), '00000100')
        self.assertEqual(to_bin(255), '11111111')
        self.assertEqual(to_bin(256), '100000000')
        self.assertEqual(to_bin(-4), '00000100')

    def test_to_hex(self):
        self.assertEqual(to_hex(4), '04')
        self.assertEqual(to_hex(255), 'ff')
        self.assertEqual(to_hex(256), '100')
        self.assertEqual(to_hex(-4), '04')

    def test_byte_int_convertions(self):
        pass

    def test_byterepr_to_bytes(self):
        self.assertEqual(byterepr_to_bytes('00000000'), b'\x00')
        self.assertEqual(byterepr_to_bytes('00001111'), b'\x0f')
        self.assertEqual(byterepr_to_bytes('10101110'), b'\xae')
        self.assertEqual(byterepr_to_bytes(
            '00000000', '00001111', '10101110'), b'\x00\x0f\xae')
        self.assertEqual(byterepr_to_bytes(), b'')

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

    def test_uint_decode(self):
        pass

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


class TestFrames():
    pass


if __name__ == '__main__':
    unittest.main()
