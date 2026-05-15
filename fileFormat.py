from math import log2

from sharedClasses import Literal
from sharedClasses import Match
from sharedClasses import LiteralEvent
from sharedClasses import MatchEvent
from sharedClasses import EndEvent

from bitIO import BitWriter, BitReader

from defaultSymbols import (
    length_base,
    length_extra_bits,
    distance_base,
    distance_extra_bits
)

from huffman import (
    count_frequencies,
    build_Huffman_tree,
    get_lengths,
    canonical_encode
)

def build_lengths(freqs):
    used = [f for f in freqs if f > 0]

    if len(used) == 0:
        return [0] * len(freqs)

    if len(used) == 1:
        lengths = [0] * len(freqs)

        for i, f in enumerate(freqs):
            if f > 0:
                lengths[i] = 1

        return lengths

    # NOTE:
    # This wrapper ignores symbols with frequency = 0
    # because the original Huffman implementation inserts
    # unused symbols into the tree.

    filtered_freqs = []
    symbol_map = []

    for i, f in enumerate(freqs):
        if f > 0:
            filtered_freqs.append(f)
            symbol_map.append(i)

    tree = build_Huffman_tree(filtered_freqs)
    filtered_lengths = get_lengths(tree, filtered_freqs)

    lengths = [0] * len(freqs)

    for idx, symbol in enumerate(symbol_map):
        lengths[symbol] = filtered_lengths[idx]

    return lengths



def build_decoder(codes):
    decoder = {}

    for symbol, code in enumerate(codes):
        if code != "":
            decoder[code] = symbol

    return decoder



def decode_symbol(reader, decoder):
    current = ""

    while True:
        current += str(reader.read_bit())

        if current in decoder:
            return decoder[current]


# =========================
# LENGTH / DISTANCE DECODING
# =========================


def decode_length(length_symbol, extra_value):
    if length_symbol == 285:
        return 258

    index = length_symbol - 257
    base = length_base[index]

    return base + extra_value



def decode_distance(distance_symbol, extra_value):
    base = distance_base[distance_symbol]

    return base + extra_value


# =========================
# BIT WIDTHS
# =========================


def compute_bw(lengths):
    maximum = max(lengths)

    if maximum == 0:
        return 0

    return int(log2(maximum)) + 1


# =========================
# HEADER
# =========================


def write_header(writer, lit_lengths, dist_lengths):
    lit_bw = compute_bw(lit_lengths)
    dist_bw = compute_bw(dist_lengths)

    writer.write_bits(lit_bw, 4)
    writer.write_bits(dist_bw, 4)

    for length in lit_lengths:
        if lit_bw > 0:
            writer.write_bits(length, lit_bw)

    for length in dist_lengths:
        if dist_bw > 0:
            writer.write_bits(length, dist_bw)



def read_header(reader):
    lit_bw = reader.read_bits(4)
    dist_bw = reader.read_bits(4)

    lit_lengths = []
    dist_lengths = []

    for _ in range(286):
        if lit_bw == 0:
            lit_lengths.append(0)
        else:
            lit_lengths.append(reader.read_bits(lit_bw))

    for _ in range(30):
        if dist_bw == 0:
            dist_lengths.append(0)
        else:
            dist_lengths.append(reader.read_bits(dist_bw))

    return lit_lengths, dist_lengths


# =========================
# PAYLOAD WRITING
# =========================


def write_payload(writer, events, lit_codes, dist_codes):
    for event in events:

        if isinstance(event, LiteralEvent):
            writer.write_bitstring(lit_codes[event.symbol])

        elif isinstance(event, MatchEvent):
            writer.write_bitstring(lit_codes[event.length_symbol])

            if event.length_extra != "":
                writer.write_bitstring(event.length_extra)

            writer.write_bitstring(dist_codes[event.distance_symbol])

            if event.distance_extra != "":
                writer.write_bitstring(event.distance_extra)

        elif isinstance(event, EndEvent):
            writer.write_bitstring(lit_codes[256])


# =========================
# COMPRESS FILE
# =========================


def compress_to_file(events, output_filename):
    lit_freq, dist_freq = count_frequencies(events)

    lit_lengths = build_lengths(lit_freq)
    dist_lengths = build_lengths(dist_freq)

    lit_codes = canonical_encode(lit_lengths)
    dist_codes = canonical_encode(dist_lengths)

    with open(output_filename, "wb") as f:
        writer = BitWriter(f)

        write_header(writer, lit_lengths, dist_lengths)
        write_payload(writer, events, lit_codes, dist_codes)

        writer.flush()


# =========================
# DECOMPRESS FILE
# =========================


def decompress_file(input_filename):
    with open(input_filename, "rb") as f:
        reader = BitReader(f)

        lit_lengths, dist_lengths = read_header(reader)

        lit_codes = canonical_encode(lit_lengths)
        dist_codes = canonical_encode(dist_lengths)

        lit_decoder = build_decoder(lit_codes)
        dist_decoder = build_decoder(dist_codes)

        tokens = []

        while True:
            symbol = decode_symbol(reader, lit_decoder)

            if 0 <= symbol <= 255:
                tokens.append(Literal(symbol))

            elif symbol == 256:
                break

            else:
                length_index = symbol - 257
                length_extra_count = length_extra_bits[length_index]

                if length_extra_count > 0:
                    extra_value = reader.read_bits(length_extra_count)
                else:
                    extra_value = 0

                actual_length = decode_length(symbol, extra_value)

                distance_symbol = decode_symbol(reader, dist_decoder)

                distance_extra_count = distance_extra_bits[distance_symbol]

                if distance_extra_count > 0:
                    distance_extra_value = reader.read_bits(distance_extra_count)
                else:
                    distance_extra_value = 0

                actual_distance = decode_distance(
                    distance_symbol,
                    distance_extra_value
                )

                tokens.append(Match(actual_length, actual_distance))

        return tokens
