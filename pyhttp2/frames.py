from .utils import int_to_bytes, int_to_byte, concat_bytes
from .hpack import Encoder


class Frame(object):
    frame_type = None

    def __init__(self, stream_id, flags=None, payload=None, frame_type=None):
        if isinstance(stream_id, int):
            stream_id = int_to_bytes(stream_id, 4)
        elif not isinstance(stream_id, (bytes, bytearray)):
            raise ValueError()

        self.stream_id = bytearray(stream_id)
        self.stream_id[0] = self.stream_id[0] & 127

        self.flags = flags
        self.payload = payload
        if frame_type:
            self.frame_type = frame_type

    def to_bytes(self):
        if not self.frame_type:
            raise Exception()

        payload = self.make_payload()
        payload_len = len(payload)

        return concat_bytes(
            int_to_bytes(payload_len, 3),
            self.frame_type,
            self.flags if self.flags is not None else b'\x00',
            self.stream_id,
            payload
        )

    def _make_payload(self):
        if self.payload is None:
            raise Exception()

        return bytes(self.payload)

    @classmethod
    def _flags_byte(cls, *ints):
        flags = 0
        for i in ints:
            flags |= i

        return int_to_byte(flags)
        

class DataFrame(Frame):
    frame_type = b'\x00'

    def __init__(self, data, end_stream=False, padding=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data = data
        self.padding = padding

        self.flags = self._flags_byte(
            0x1 if end_stream else None,
            0x8 if padding else None
        )

    def _make_payload(self):
        return concat_bytes(
            int_to_byte(self.padding) if self.padding else None,
            self.data,
            b'\x00' * self.padding if self.padding else None
        )

        
class HeadersFrame(Frame):
    frame_type = b'\x01'

    def __init__(self, headers, encoder=None, end_stream=False, end_headers=False, 
                 padding=None, stream_dep=None, weight=None, exclusive=None,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.headers = headers
        self.padding = padding
        self.stream_dep = stream_dep
        self.weight = weight
        self.exclusive = exclusive

        if encoder is None:
            self.encoder = Encoder()

        self.flags = self._flags_byte(
            0x1 if end_stream else None,
            0x4 if end_headers else None,
            0x8 if padding else None,
            0x20 if stream_dep else None
        )

    def _make_payload(self):
        return concat_bytes(
            int_to_byte(self.padding) if self.padding else None,
            self._make_dep() if self.stream_dep else None
            self.encoder.encode_headers(self.headers),
            b'\x00' * self.padding if self.padding else None
        )

    def _make_dep(self):
        dep = int_to_bytes(self.stream_dep, 4)
        if self.exclusive:
            dep[0] |= 128
        else:
            dep[0] &= 127

        weight = int_to_byte(self.weight)

        return dep, weight


class SettingsFrame(Frame):
    frame_type = b'\x04'

    SETTINGS_HEADER_TABLE_SIZE = 1
    SETTINGS_ENABLE_PUSH = 2

    def __init__(self, ack=None, header_table_size=None, enable_push=None, 
                 *args, **kwargs):

        super().__init__(stream_id=0, *args, **kwargs)

        self.header_table_size = header_table_size
        self.enable_push = enable_push
        self.ack = ack

        self.flags = self._flags_byte(0x1 if ack else None)

    def _make_payload(self):
        if self.ack is not None and self.ack == True:
            return b''

        settings = []

        if self.header_table_size is not None:
            settings.append(
                self._make_setting(self.SETTINGS_HEADER_TABLE_SIZE, self.header_table_size)
            )

        if self.enable_push is not None:
            settings.append(
                self._make_setting(self.SETTINGS_ENABLE_PUSH, 1 if self.enable_push else 0)
            )
        
        return concat_bytes(*settings)

    def _make_setting(self, _id, val):
        return concat_bytes(
            int_to_bytes(_id, 2),
            int_to_bytes(val, 4)
        )
