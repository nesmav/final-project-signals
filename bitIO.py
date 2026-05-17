class BitWriter:

    def __init__(self):
        self._buffer = bytearray()
        self._current_byte = 0
        self._bits_filled = 0

    def write_bits(self, value: int, n_bits: int):
        """Write `n_bits` bits from `value`, MSB first."""
        for i in range(n_bits - 1, -1, -1):
            bit = (value >> i) & 1
            self._current_byte = (self._current_byte << 1) | bit
            self._bits_filled += 1
            if self._bits_filled == 8:
                self._buffer.append(self._current_byte)
                self._current_byte = 0
                self._bits_filled = 0

    def write_bit_string(self, bit_str: str):
        """Write a string like '01101' as individual bits."""
        for ch in bit_str:
            self._current_byte = (self._current_byte << 1) | int(ch)
            self._bits_filled += 1
            if self._bits_filled == 8:
                self._buffer.append(self._current_byte)
                self._current_byte = 0
                self._bits_filled = 0

    def flush(self) -> bytes:
        """Pad the last byte with zeros and return all bytes."""
        if self._bits_filled > 0:
            self._current_byte <<= (8 - self._bits_filled)
            self._buffer.append(self._current_byte)
            self._current_byte = 0
            self._bits_filled = 0
        return bytes(self._buffer)


class BitReader:
    """Reads bits MSB-first from a bytes object."""

    def __init__(self, data: bytes):
        self._data = data
        self._byte_pos = 0
        self._bit_pos = 0  

    def read_bits(self, n_bits: int) -> int:
        """Read `n_bits` bits and return as an integer."""
        value = 0
        for _ in range(n_bits):
            if self._byte_pos >= len(self._data):
                raise EOFError("Not enough bits to read")
            byte = self._data[self._byte_pos]
            bit = (byte >> (7 - self._bit_pos)) & 1
            value = (value << 1) | bit
            self._bit_pos += 1
            if self._bit_pos == 8:
                self._bit_pos = 0
                self._byte_pos += 1
        return value
