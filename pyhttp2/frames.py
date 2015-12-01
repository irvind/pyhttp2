from pyhttp2.utils import int_to_bytes


class FrameType(object):
    DATA = b'\x00'
    HEADERS = b'\x01'


class FrameFlags(object):
    def to_byte(flags):
        pass


class Frame(object):
    def __init__(self, _type, flags, payload=None, stream_id=None):
        self.type = _type
        self.flags = flags
        self.payload = payload

        if stream_id is None:
            pass
        
    def bytes_repr():
        arr = bytearray()
        arr.extend(int_to_bytes(len(self.payload), 3))
        arr.extend(frame_type)

    def 


class HeadersFrame(object):
    def __init__(self, *args, **kwargs):
        super().__init__(FrameType.HEADERS, *args, **kwargs)


def make_frame(frame_type, flags, stream_id, payload):
    arr = bytearray()
    arr.extend(int_to_bytes(len(payload), 3))
    arr.extend(frame_type)


    pass