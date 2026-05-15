import sys
import os

from LZ77 import lz77_compress
from LZ77decompressor import lz77_decompress
from defaultSymbols import lz77_to_events

from fileFormat import (
    compress_to_file,
    decompress_file
)


def compress_file(input_filename):
    with open(input_filename, "rb") as f:
        data = f.read()

    tokens = lz77_compress(data)
    events = lz77_to_events(tokens)

    output_filename = input_filename + ".sdfl"

    compress_to_file(events, output_filename)

    print(f"Compressed file written to: {output_filename}")


def decompress_sdfl(input_filename):
    tokens = decompress_file(input_filename)

    data = lz77_decompress(tokens)

    if input_filename.endswith(".sdfl"):
        output_filename = input_filename[:-5]
    else:
        output_filename = input_filename + ".out"

    with open(output_filename, "wb") as f:
        f.write(data)

    print(f"Decompressed file written to: {output_filename}")


def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("python main.py -c filename")
        print("python main.py -d filename")
        return

    mode = sys.argv[1]
    filename = sys.argv[2]

    if not os.path.exists(filename):
        print("File not found")
        return

    if mode == "-c":
        compress_file(filename)

    elif mode == "-d":
        decompress_sdfl(filename)

    else:
        print("Invalid mode")


if __name__ == "__main__":
    main()
