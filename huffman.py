from sharedClasses import LiteralEvent, MatchEvent,EndEvent
from collections import deque
import heapq

def count_frequencies(events: list):
    lit_freq = [0] * 286
    dist_freq = [0] * 30
    for event in events :
        if isinstance(event, LiteralEvent):
            lit_freq[event.symbol] += 1
        elif isinstance(event, MatchEvent):
            lit_freq[event.length_symbol] += 1
            dist_freq[event.distance_symbol] += 1
        elif isinstance(event, EndEvent):
            lit_freq[256] += 1
    return lit_freq, dist_freq

def build_Huffman_tree(freq_list: list) -> list:
    tree = []
    priority_q = []
    for i in range(len(freq_list)):
        tree.append((freq_list[i], -1, -1))
        priority_q.append((freq_list[i], i))
    heapq.heapify(priority_q)
    while len(priority_q) > 1:
        x, index_x = heapq.heappop(priority_q)
        y, index_y = heapq.heappop(priority_q)
        total = x + y
        new_index = len(tree)
        tree.append((total, index_x, index_y))
        heapq.heappush(priority_q, (total, new_index))
    return tree

def get_lengths(tree: list, freq_list: list) -> list:
    queue = deque()
    freqs = len(freq_list)
    lengths = [0] * freqs
    j = len(tree) - 1
    queue.append((j, 0))
    while queue:
        current_index, length = queue.popleft()
        freq, left, right = tree[current_index]
        if left == -1 and right == -1:
            if current_index < freqs:
                lengths[current_index] = length
        else:
            if left != -1:
                queue.append((left, length + 1))
            if right != -1:
                queue.append((right, length + 1))
    return lengths

def check_lengths(lengths: list) -> list:
    for i in range(len(lengths)):
        if lengths[i] > 15:
            lengths[i] = 15
    kraft = sum(2 ** (15 - l) for l in lengths if l > 0)
    heap = [(l, i) for i, l in enumerate(lengths) if l > 0]
    heapq.heapify(heap)
    while kraft > (2 ** 15):
        l, i = heapq.heappop(heap)
        if lengths[i] < 15:
            kraft -= 2 ** (15 - lengths[i])
            lengths[i] += 1
            kraft += 2 ** (15 - lengths[i])
            heapq.heappush(heap, (lengths[i], i))
    return lengths

def canonical_encode(lengths: list) -> list:
    lengths = check_lengths(lengths)
    symbol_code = [0] * len(lengths)
    count = [0] * 16
    for length in lengths:
        count[length] += 1
    count[0] = 0
    next_code = [0] * 16
    code = 0
    for bits in range(1, 16):
        code = (code + count[bits - 1]) << 1
        next_code[bits] = code
    for symbol in range(len(lengths)):
        length = lengths[symbol]
        if length != 0:
            symbol_code[symbol] = next_code[length]
            next_code[length] += 1
    return symbol_code