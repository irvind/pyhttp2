import unittest

from pyhttp2.utils import byterepr_to_bytes, int_to_byte
from pyhttp2.hpack import (
    uint_encode, uint_decode, bytestr_encode, IndexTable, Encoder,
    Decoder
)


class TestEncodeDecodeSimpleTypes(unittest.TestCase):
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


class TestIndexTable(unittest.TestCase):
    def setUp(self):
        self.table = IndexTable()

        self.modif_table = IndexTable()
        self.modif_table.add('myfield', 'myvalue')
        self.modif_table.add('myfield2', 'myvalue2')
        self.modif_table.add('somefield', 'somevalue')

    def test_getitem(self):
        self.assertEqual(self.table[1], (':authority', ''))
        self.assertEqual(self.table[5], (':path', '/index.html'))
        self.assertEqual(self.table[IndexTable.STATIC_LENGTH], ('www-authenticate', ''))

        self.assertEqual(self.modif_table[IndexTable.STATIC_LENGTH + 1], ('somefield', 'somevalue'))

        with self.assertRaises(IndexError):
            print(self.table[100])

    def test_insertion(self):
        self.table.add('myfield', 'myval')
        self.assertEqual(self.table.get(IndexTable.STATIC_LENGTH + 1), ('myfield', 'myval'))

        self.table.add('myfield2', 'myval2')
        self.assertEqual(self.table.get(IndexTable.STATIC_LENGTH + 1), ('myfield2', 'myval2'))
        self.assertEqual(self.table.get(IndexTable.STATIC_LENGTH + 2), ('myfield', 'myval'))

    def test_len(self):
        self.assertEqual(len(self.table), IndexTable.STATIC_LENGTH)
        self.assertEqual(len(self.modif_table), IndexTable.STATIC_LENGTH + 3)

    def test_find_name(self):
        self.assertEqual(self.table.find(':scheme'), 6)
        self.assertEqual(self.table.find('www-authenticate'), IndexTable.STATIC_LENGTH)

        self.assertEqual(self.modif_table.find('myfield'), IndexTable.STATIC_LENGTH + 3)
        self.assertIsNone(self.modif_table.find('notfound'))

        tbl = IndexTable()
        tbl.add('f1', '1')
        tbl.add('f1', '2')
        tbl.add('f2', '3')
        self.assertEqual(tbl.find('f1'), IndexTable.STATIC_LENGTH + 2)

    def test_find_field(self):
        self.assertEqual(self.table.find(':method', 'POST'), 3)
        self.assertEqual(self.table.find('accept-charset', ''), 15)

        self.assertIsNone(self.table.find('none', 'none'))

        self.assertEqual(self.modif_table.find('somefield', 'somevalue'), IndexTable.STATIC_LENGTH + 1)
        self.assertEqual(self.modif_table.find('myfield', 'myvalue'), IndexTable.STATIC_LENGTH + 3)


class TestEncoder(unittest.TestCase):
    def test_encoder(self):
        encoder = Encoder()

        self.assertEqual(encoder.encode_headers('custom-key: custom-header'),
            b'\x40\x0acustom-key\x0dcustom-header')
        


class TestDecoder(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()