import math
from bitIO import BitWriter, BitReader
from sharedClasses import LiteralEvent, MatchEvent, EndEvent
from defaultSymbols import length_base, length_extra_bits, distance_base, distance_extra_bits


def _bit_width(max_val: int) -> int:
    if max_val == 0:
        return 0
    return math.floor(math.log2(max_val)) + 1


def write_compressed(events: list, lit_codes: list, dist_codes: list,
                     lit_lengths: list, dist_lengths: list) -> bytes:
    writer = BitWriter()

    max_lit  = max(lit_lengths)
    max_dist = max(dist_lengths) if any(dist_lengths) else 0

    lit_bw  = _bit_width(max_lit)
    dist_bw = _bit_width(max_dist)

    writer.write_bits(lit_bw,  4)
    writer.write_bits(dist_bw, 4)

    for length in lit_lengths:
        writer.write_bits(length, lit_bw)

    for length in dist_lengths:
        if dist_bw > 0:
            writer.write_bits(length, dist_bw)

    for event in events:
        if isinstance(event, LiteralEvent):
            writer.write_bit_string(lit_codes[event.symbol])

        elif isinstance(event, MatchEvent):
            writer.write_bit_string(lit_codes[event.length_symbol])
            if event.length_extra:
                writer.write_bit_string(event.length_extra)
            writer.write_bit_string(dist_codes[event.distance_symbol])
            if event.distance_extra:
                writer.write_bit_string(event.distance_extra)

        elif isinstance(event, EndEvent):
            writer.write_bit_string(lit_codes[256])

    return writer.flush()


def _build_decode_table(lengths: list) -> dict:
    count = [0] * 16
    for l in lengths:
        count[l] += 1
    count[0] = 0

    next_code = [0] * 16
    code = 0
    for bits in range(1, 16):
        code = (code + count[bits - 1]) << 1
        next_code[bits] = code

    decode_table = {}
    for symbol, length in enumerate(lengths):
        if length != 0:
            bit_str = format(next_code[length], f'0{length}b')
            decode_table[bit_str] = symbol
            next_code[length] += 1
    return decode_table


def _read_symbol(reader: BitReader, decode_table: dict) -> int:
    bits = ""
    for _ in range(16):
        bits += str(reader.read_bits(1))
        if bits in decode_table:
            return decode_table[bits]
    raise ValueError(f"Invalid Huffman code encountered: {bits}")


def read_compressed(data: bytes) -> bytes:
    reader = BitReader(data)

    lit_bw  = reader.read_bits(4)
    dist_bw = reader.read_bits(4)

    lit_lengths  = [reader.read_bits(lit_bw)  for _ in range(286)]
    dist_lengths = [reader.read_bits(dist_bw) for _ in range(30)] if dist_bw > 0 else [0] * 30

    lit_decode  = _build_decode_table(lit_lengths)
    dist_decode = _build_decode_table(dist_lengths)

    output = bytearray()

    while True:
        symbol = _read_symbol(reader, lit_decode)

        if symbol < 256:
            output.append(symbol)

        elif symbol == 256:
            break

        else:
            idx = symbol - 257

            base_len    = length_base[idx]
            n_len_extra = length_extra_bits[idx]
            extra_len   = reader.read_bits(n_len_extra) if n_len_extra > 0 else 0
            length      = base_len + extra_len

            dist_sym     = _read_symbol(reader, dist_decode)
            base_dist    = distance_base[dist_sym]
            n_dist_extra = distance_extra_bits[dist_sym]
            extra_dist   = reader.read_bits(n_dist_extra) if n_dist_extra > 0 else 0
            distance     = base_dist + extra_dist

            start = len(output) - distance
            for k in range(length):
                output.append(output[start + k])

    return bytes(output)
