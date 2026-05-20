import sys
import os

from LZ77           import lz77_compress
from deflateSymbols import lz77_to_events
from huffman        import count_frequencies, build_Huffman_tree, get_lengths, canonical_encode
from fileFormat     import write_compressed, read_compressed


def compress(input_path: str):
    output_path = input_path + ".sdfl"

    with open(input_path, "rb") as f:
        data = f.read()

    tokens = lz77_compress(data)
    events = lz77_to_events(tokens)

    lit_freq, dist_freq = count_frequencies(events)

    lit_tree, root1  = build_Huffman_tree(lit_freq)
    dist_tree, root2 = build_Huffman_tree(dist_freq)

    lit_lengths  = get_lengths(lit_tree, root1, lit_freq)
    dist_lengths = get_lengths(dist_tree, root2, dist_freq)

    lit_codes  = canonical_encode(lit_lengths)
    dist_codes = canonical_encode(dist_lengths)

    compressed = write_compressed(events, lit_codes, dist_codes,
                                  lit_lengths, dist_lengths)

    with open(output_path, "wb") as f:
        f.write(compressed)

    original_size   = len(data)
    compressed_size = len(compressed)
    ratio = compressed_size / original_size * 100 if original_size else 0


def decompress(input_path: str):
    if input_path.endswith(".sdfl"):
        output_path = input_path[:-5]
    else:
        print("Warning: input file does not end with .sdfl; appending .decompressed")
        output_path = input_path + ".decompressed"

    with open(input_path, "rb") as f:
        data = f.read()

    original_data = read_compressed(data)

    with open(output_path, "wb") as f:
        f.write(original_data)


def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python main.py -c <file>   compress a file")
        print("  python main.py -d <file>   decompress a file")
        sys.exit(1)

    flag      = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.isfile(file_path):
        print(f"Error: file not found: {file_path}")
        sys.exit(1)

    if flag == "-c":
        compress(file_path)
    elif flag == "-d":
        decompress(file_path)
    else:
        print(f"Unknown flag: {flag}")
        print("Use -c to compress or -d to decompress.")
        sys.exit(1)


if __name__ == "__main__":
    main()

