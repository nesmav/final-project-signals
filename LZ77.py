from sharedClasses import Literal, Match

WINDOW_SIZE = 32768
MIN_MATCH = 3
MAX_MATCH = 258
MAX_CANDIDATES = 64

def insert_into_table(table, data, pos):
    if pos + 3 <= len(data) :
        if data[pos : pos + 3] in table :
            table[data[pos : pos + 3]].append(pos)
        else :
            table[data[pos : pos + 3]] = [pos]


def lz77_compress(inputed_data : bytes) -> list :
    i = 0
    r_list = []
    h_table = {}
    while i < len(inputed_data) :
        if len(inputed_data) - i < MIN_MATCH :
            r_list.append(Literal(inputed_data[i]))
            i += 1
        else :
            candidates = h_table.get(inputed_data[i : i+3], [])
            best_length = 0
            best_distance = 0
            candidates = reversed(candidates[-MAX_CANDIDATES :])
            for candidate in candidates :
                distance = i - candidate
                if distance > WINDOW_SIZE :
                    break
                else :
                    counter = 0
                    while (counter < MAX_MATCH) and (i + counter < len(inputed_data)) and (inputed_data[candidate + counter] == inputed_data[i + counter]) :
                        counter += 1
                    if counter > best_length:
                        best_length = counter
                        best_distance = distance
                    elif (counter == best_length) and (distance < best_distance) :
                        best_distance = distance
            if best_length >= MIN_MATCH :
                r_list.append(Match(best_length, best_distance))
                start = i
                end = i + best_length
                while start != end :
                    insert_into_table(h_table, inputed_data, start)
                    start += 1
                i += best_length
            else:
                r_list.append(Literal(inputed_data[i]))
                insert_into_table(h_table, inputed_data, i)
                i += 1
    return r_list