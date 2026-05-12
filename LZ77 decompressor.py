from sharedClasses import Literal,Match
def lz77_decompress(tokens: list) -> bytes:
    output = []
    for token in tokens:
        if isinstance(token,Literal):
            output.append(token.byte)
        elif isinstance(token,Match):
            start = len(output) - token.distance
            for k in range(token.length):
                output.append(output[start + k])
    return bytes(output)