from sharedClasses import Literal, Match, LiteralEvent, MatchEvent, EndEvent

length_base = [
    3, 4, 5, 6, 7, 8, 9, 10,
    11, 13, 15, 17,
    19, 23, 27, 31,
    35, 43, 51, 59,
    67, 83, 99, 115,
    131, 163, 195, 227,
    258
]

length_extra_bits = [
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 1,
    2, 2, 2, 2,
    3, 3, 3, 3,
    4, 4, 4, 4,
    5, 5, 5, 5,
    0
]

distance_base = [
    1, 2, 3, 4,
    5, 7,
    9, 13,
    17, 25,
    33, 49,
    65, 97,
    129, 193,
    257, 385,
    513, 769,
    1025, 1537,
    2049, 3073,
    4097, 6145,
    8193, 12289,
    16385, 24577
]

distance_extra_bits = [
    0, 0, 0, 0,
    1, 1,
    2, 2,
    3, 3,
    4, 4,
    5, 5,
    6, 6,
    7, 7,
    8, 8,
    9, 9,
    10, 10,
    11, 11,
    12, 12,
    13, 13
]


def encode_length(length: int):
    if length == 258:
        return 285, ""
    for i in range(len(length_base) - 1):
        base      = length_base[i]
        n_extra   = length_extra_bits[i]
        range_end = base + (1 << n_extra) - 1
        if base <= length <= range_end:
            symbol      = 257 + i
            extra_value = length - base
            extra_str   = format(extra_value, f'0{n_extra}b') if n_extra > 0 else ""
            return symbol, extra_str
    return 285, ""


def encode_distance(distance: int):
    for i in range(len(distance_base) - 1):
        base      = distance_base[i]
        n_extra   = distance_extra_bits[i]
        range_end = base + (1 << n_extra) - 1
        if base <= distance <= range_end:
            symbol      = i
            extra_value = distance - base
            extra_str   = format(extra_value, f'0{n_extra}b') if n_extra > 0 else ""
            return symbol, extra_str

    i = 29
    base = distance_base[i]
    n_extra = distance_extra_bits[i]
    symbol = i
    extra_value = distance - base
    extra_str = format(extra_value, f'0{n_extra}b')
    return symbol, extra_str


def lz77_to_events(tokens: list) -> list:
    events = []

    for token in tokens:
        if isinstance(token, Literal):
            events.append(LiteralEvent(token.byte))

        elif isinstance(token, Match):
            length_symbol, length_extra = encode_length(token.length)
            dist_symbol,   dist_extra   = encode_distance(token.distance)
            events.append(MatchEvent(length_symbol, length_extra,
                                     dist_symbol,   dist_extra))
        else:
            raise ValueError(f"Unknown token type: {token}")

    events.append(EndEvent())
    return events
